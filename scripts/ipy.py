from traitlets.config import Config

c = Config()

c.InteractiveShellApp.exec_lines = [
    'print("\\nimporting some things\\n")',
    "import math",
    "math",
]
# c.InteractiveShell.colors = 'LightBG'
# c.InteractiveShell.color_info = True

# c.InteractiveShell.colors = 'neutral'

# c.TerminalInteractiveShell.highlighting_style = 'nord'

# c.TerminalInteractiveShell.highlight_matching_brackets = True

# c.InteractiveShell.confirm_exit = False
# c.TerminalIPythonApp.display_banner = False


import IPython

IPython.start_ipython(config=c)
