# Run examples from documentation

import subprocess

for n in range(1, 6):
    subprocess.call(f"python example_{n:02}.py", shell=True)
    subprocess.call(f"cp {n:02}*.png ../docs/images/example_{n:02}.png", shell=True)

# subprocess.call("python example_2.py", shell=True)
# subprocess.call("cp 02*.png ../docs/images/example_2.png", shell=True)

# subprocess.call("python example_3.py", shell=True)
# subprocess.call("cp 03*.png ../docs/images/example_3.png", shell=True)

# subprocess.call("python example_4.py", shell=True)
# subprocess.call("cp 04*.png ../docs/images/example_4.png", shell=True)

# subprocess.call("python example_5.py", shell=True)
# subprocess.call("cp 05*.png ../docs/images/example_5.png", shell=True)
