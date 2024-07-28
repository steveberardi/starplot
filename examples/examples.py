"""Runs examples from documentation and copies the image to the docs directory"""

import subprocess
import glob
import time

start = time.time()

for filename in glob.iglob("*.py"):
    if filename.endswith("examples.py"):
        continue

    # if filename != "star_chart_basic.py":
    #     continue
    print(f"Running {filename}")
    subprocess.call(f"python {filename}", shell=True)


print("Copying images to examples directory...")
subprocess.call("cp *.png *.jpg ../docs/images/examples/", shell=True)

print(f"{time.time() - start}")
