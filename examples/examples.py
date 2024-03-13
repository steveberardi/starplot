"""Runs examples from documentation and copies the image to the docs directory"""

import subprocess

NUM_EXAMPLES = 7

for n in range(1, NUM_EXAMPLES + 1):
    print(f"Running example {n}")
    subprocess.call(f"python example_{n:02}.py", shell=True)
    subprocess.call(
        f"cp {n:02}*.png ../docs/images/examples/example_{n:02}.png", shell=True
    )
