"""Runs examples from documentation and copies the image to the docs directory"""

import subprocess
import glob
import time

from PIL import Image
from multiprocessing import Pool

start = time.time()


def thumbnail(filename, max_dimension=900):
    print(filename)
    img = Image.open(filename)
    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    img.save(f"{filename[:-4]}-sm.png", optimize=True)


# Run all examples
for filename in glob.iglob("*.py"):
    if filename.endswith("examples.py"):
        continue

    # if filename != "star_chart_basic.py":
    #     continue
    print(f"Running {filename}")
    subprocess.call(f"python {filename}", shell=True)

# Create thumbnail images for the examples list page
image_files = glob.glob("*.png")
pool = Pool(8)
results = pool.map(thumbnail, image_files)

# Copy all images to docs directory
print("Copying images to examples directory...")
subprocess.call("cp *.png ../docs/images/examples/", shell=True)

print(f"{time.time() - start}")
