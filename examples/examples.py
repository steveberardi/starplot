# Run examples from documentation

import subprocess

subprocess.call("python example_1.py", shell=True)
subprocess.call("cp 01*.png ../docs/images/example_1.png", shell=True)

subprocess.call("python example_2.py", shell=True)
subprocess.call("cp 02*.png ../docs/images/example_2.png", shell=True)

subprocess.call("python example_3.py", shell=True)
subprocess.call("cp 03*.png ../docs/images/example_3.png", shell=True)

subprocess.call("python example_4.py", shell=True)
subprocess.call("cp 04*.png ../docs/images/example_4.png", shell=True)
