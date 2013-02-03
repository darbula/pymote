c = get_config()
app = c.InteractiveShellApp
term_app = c.TerminalIPythonApp


# This can be used at any point in a config file to load a sub config
# and merge it into the current one.
load_subconfig('ipython_config.py', profile='default')
lines = """
from pymote import *
"""

# You have to make sure that attributes that are containers already
# exist before using them.  Simple assigning a new list will override
# all previous values.

if hasattr(app, 'exec_lines'):
    app.exec_lines.append(lines)
else:
    app.exec_lines = [lines]

if hasattr(app, 'extensions'):
    app.extensions.append('autoreload')
else:
    app.extensions = ['autoreload']

app.gui = 'qt'

term_app.gui = 'qt'
term_app.pylab = 'qt'
    