"""Runs examples from documentation and copies the image to the docs directory"""

import subprocess
import glob
import time

from PIL import Image
from multiprocessing import Pool

from starplot.data.catalogs import download_all_catalogs

skip = [
    "map_comet_neowise.py",
    "horizon_sgr.py",
    "optic_moon_saturn.py",
    # "map_milky_way_stars.py",
    # "stuff.py",
]


def thumbnail(filename, max_dimension=900):
    print(filename)
    img = Image.open(filename)
    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    img.save(f"{filename[:-4]}-sm.png", optimize=True)


def get_example_names():
    filenames = []

    for filename in glob.iglob("*.py"):
        # if filename not in ["map_virgo_cluster.py"]:
        #     continue

        if filename.endswith("examples.py"):
            continue

        if filename in skip:
            continue

        filenames.append(filename)

    return filenames


def run_example(filename):
    print(f"Running {filename}")
    subprocess.call(["python", filename])


if __name__ == "__main__":
    num_workers = 10
    start = time.time()
    example_files = get_example_names()
    processes = []

    # download catalogs if they dont exist
    download_all_catalogs(silent=True)

    with Pool(num_workers) as pool:
        pool.map(run_example, example_files)

    # Create thumbnail images for the examples list page
    image_files = glob.glob("*.png")
    pool = Pool(num_workers)
    results = pool.map(thumbnail, image_files)

    # Copy all images to docs directory
    print("Copying images to examples directory...")
    subprocess.call("cp *.png ../docs/images/examples/", shell=True)

    print(f"{time.time() - start}")
