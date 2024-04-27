"""Runs examples from tutorial and copies the image to the docs directory"""

import subprocess
import glob
import time

start = time.time()

for filename in glob.iglob("*.py"):
    if filename.endswith("build.py"):
        continue

    print(f"Running {filename}")
    subprocess.call(f"python {filename}", shell=True)


print("Copying images to tutorial directory...")
subprocess.call(f"cp *.png ../docs/images/tutorial/", shell=True)

print(f"{time.time() - start}")
