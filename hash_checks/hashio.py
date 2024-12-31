import sys
import inspect
import time
import multiprocessing as mp

from pathlib import Path

import imagehash
import yaml

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image
from rich.console import Console

import map_checks
import optic_checks
import zenith_checks
import horizon_checks

TEMPLATE_NAME = "template.html"

HERE = Path(__file__).resolve().parent

RESULTS_PATH = HERE / "results.html"

console = Console()


class Hashio:
    """
    Helper class that iterates through a list of callables that each return a filename for an image,
    and computes the dhash and colorhash of each callable and checks those hashes against a hashlock.yml file.

    This is used to help build tests for different plotting functions.
    """

    def __init__(self, callables: list, lockfile: str = HERE / "hashlock.yml") -> None:
        self.callables = callables
        self._lockfile_path = lockfile

    @staticmethod
    def find_functions(module):
        """
        Finds all functions in module that start with 'check_'

        Returns:
            list of function objects
        """
        funcs = inspect.getmembers(module, inspect.isfunction)
        hashio_funcs = []
        for func_name, func in funcs:
            if func_name.startswith("check_"):
                hashio_funcs.append(func)
        return hashio_funcs

    def _load_lockfile(self):
        try:
            with open(self._lockfile_path, "r") as hashlock_file:
                return yaml.safe_load(hashlock_file)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Hashlock file not found. Call lock() to create it."
            )

    def _colorhash(self, img) -> str:
        return str(imagehash.colorhash(img))

    def _dhash(self, img) -> str:
        r, g, b, a = img.split()
        hash_red = imagehash.dhash(r)
        hash_green = imagehash.dhash(g)
        hash_blue = imagehash.dhash(b)
        return str(hash_red) + str(hash_green) + str(hash_blue)

    def _phash(self, img) -> str:
        return str(imagehash.phash(img))

    def _call_wrapper(self, c):
        func_name = c.__name__[6:]
        console.print(f"{func_name}...")
        filename = c()
        img = Image.open(filename)
        return func_name, {
            "filename": str(filename),
            "dhash": self._dhash(img),
            "phash": self._phash(img),
        }

    def _get_hashes(self) -> dict:
        """Gets hashes for all callables"""
        # mp.set_start_method("spawn")  # required for M1 macs? or macOS issue?

        console.print("Getting hashes...", style="bold")
        with mp.Pool(5) as p:
            results = p.map(self._call_wrapper, self.callables)

        return {func_name: hashes for func_name, hashes in results}

    def _check(self):
        passed = {}
        failed = {}
        new = {}
        hashes = self._get_hashes()
        hashlock = self._load_lockfile()

        console.print("\nChecking hashes...", style="bold")
        for func_name, values in hashes.items():
            values["filename"] = Path(values["filename"]).relative_to(HERE)

            if func_name not in hashlock:
                new[func_name] = values
                console.print(f"{func_name}...NEW", style="blue")
                continue

            if not all(
                [
                    values["dhash"] == hashlock[func_name]["dhash"],
                    values["phash"] == hashlock[func_name]["phash"],
                ]
            ):
                values["dhash_expected"] = hashlock[func_name]["dhash"]
                values["phash_expected"] = hashlock[func_name]["phash"]
                failed[func_name] = values
                console.print(f"{func_name}...FAIL", style="red")

            else:
                passed[func_name] = values
                console.print(f"{func_name}...", style="green")

        return passed, failed, new

    def check(self):
        env = Environment(loader=FileSystemLoader(HERE), autoescape=select_autoescape())
        template = env.get_template(str(TEMPLATE_NAME))

        passed, failed, new = self._check()

        with open(RESULTS_PATH, "w") as results_file:
            results_file.write(template.render(passed=passed, failed=failed, new=new))

        return len(passed.keys()), len(failed.keys()), len(new.keys())

    def lock(self):
        """Updates lockfile with hashes of all callables"""
        with open(self._lockfile_path, "w") as outfile:
            hashes = self._get_hashes()
            hashes_yaml = yaml.dump(hashes)
            outfile.write(hashes_yaml)


if __name__ == "__main__":
    start = time.time()
    command = sys.argv[1]

    callables = Hashio.find_functions(map_checks)
    callables += Hashio.find_functions(zenith_checks)
    callables += Hashio.find_functions(optic_checks)
    callables += Hashio.find_functions(horizon_checks)

    h = Hashio(callables=callables)

    if command.lower() == "lock":
        h.lock()
        console.print(":lock: Hashes locked!", style="bold green")
        console.print(f":stopwatch: Time: {round(time.time() - start)}s")
    elif command.lower() == "check":
        passed, failed, new = h.check()
        console.print(f":stopwatch: {round(time.time() - start)}s")

        console.print(f"\nPASSED: {passed}\n", style="green")

        if failed:
            console.print("FAILED: retrying...\n", style="bold red")
            passed, failed, new = h.check()

        if failed or new:
            console.print(f"FAILED: {failed}\n", style="bold red")
            console.print(f"NEW   : {new}\n", style="blue")
            exit(1)
    else:
        raise ValueError(f"Unrecognized command: {command}")
