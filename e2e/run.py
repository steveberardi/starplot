"""
Runs every function named `e2e_*` found in the .py files in this directory,
compares each one's exported SVG against the matching file in expected/, and
writes an HTML report (actual/results.html) summarizing what passed, failed,
or is new (no expected file yet).
"""

import difflib
import importlib.util
import inspect
import multiprocessing as mp
import sys
import time
import traceback
import webbrowser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

HERE = Path(__file__).resolve().parent
EXPECTED_PATH = HERE / "expected"
ACTUAL_PATH = HERE / "actual"
TEMPLATE_NAME = "template.html"
RESULTS_PATH = ACTUAL_PATH / "results.html"
SELF_NAME = Path(__file__).name

NUM_WORKERS = 4
DIFF_LINE_LIMIT = 1000

console = Console()


def _discover_functions() -> list:
    """Finds every `e2e_*` function in every .py file in this directory (except this file)."""
    functions = []

    for path in sorted(HERE.glob("*.py")):
        if path.name == SELF_NAME:
            continue

        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)

        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("e2e_"):
                functions.append(func)

    return functions


def _run(func) -> tuple[str, str, dict]:
    """
    Runs one e2e_* function and compares its output to the expected file.

    Returns:
        (name, category, values) -- category is one of "passed", "failed", "new"
    """
    name = func.__name__[len("e2e_") :]
    console.print(f"{name}...")

    try:
        actual_file = Path(func())
    except Exception:  # noqa: BLE001 -- catch anything the e2e function raises
        return (
            name,
            "failed",
            {"exception": traceback.format_exc(), "diff": None},
        )

    relative_path = actual_file.relative_to(ACTUAL_PATH)
    expected_file = EXPECTED_PATH / relative_path
    actual_svg = actual_file.read_text()

    values = {
        "exception": None,
        "expected_filename": f"../expected/{relative_path}",
        "actual_filename": str(relative_path),
        "diff": None,
    }

    if not expected_file.exists():
        return name, "new", values

    expected_svg = expected_file.read_text()

    diff_lines = list(
        difflib.unified_diff(
            expected_svg.splitlines(),
            actual_svg.splitlines(),
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
    )
    if len(diff_lines) > DIFF_LINE_LIMIT:
        diff_lines = diff_lines[:DIFF_LINE_LIMIT]
        diff_lines.append(f"... diff truncated after {DIFF_LINE_LIMIT} lines ...")
    values["diff"] = "\n".join(diff_lines)

    if expected_svg == actual_svg:
        return name, "passed", values

    return name, "failed", values


def run() -> tuple[dict, dict, dict]:
    passed, failed, new = {}, {}, {}
    styles_by_category = {
        "passed": ("green", ""),
        "failed": ("red", "FAIL"),
        "new": ("blue", "NEW"),
    }

    functions = _discover_functions()

    console.print("Running e2e checks...", style="bold")
    with mp.Pool(NUM_WORKERS) as pool:
        results = pool.map(_run, functions)

    for name, category, values in results:
        {"passed": passed, "failed": failed, "new": new}[category][name] = values

        color, label = styles_by_category[category]
        console.print(f"{name}...{label}", style=color)

    return passed, failed, new


def write_report(passed: dict, failed: dict, new: dict) -> None:
    env = Environment(loader=FileSystemLoader(HERE), autoescape=select_autoescape())
    template = env.get_template(TEMPLATE_NAME)

    ACTUAL_PATH.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as results_file:
        results_file.write(template.render(passed=passed, failed=failed, new=new))


if __name__ == "__main__":
    start = time.time()

    passed, failed, new = run()
    write_report(passed, failed, new)

    console.print(f"\n:stopwatch: {round(time.time() - start)}s")
    console.print(f"PASSED: {len(passed)}\n", style="green")
    console.print("Results:")
    console.print(f"{RESULTS_PATH}\n")
    # webbrowser.open(RESULTS_PATH.as_uri())

    if failed or new:
        console.print(f"FAILED: {list(failed)}\n", style="bold red")
        console.print(f"NEW   : {list(new)}\n", style="blue")
        sys.exit(1)
