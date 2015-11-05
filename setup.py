from distutils.core import setup
import py2exe

wx = dict(
    script = 'duoMainWnd.py',
    icon_resources = [(1, "res/icon.ico")],
)

cx = dict(
    script = 'duoMainWnd.pyw',
    icon_resources = [(0, "res/icon.ico")],
)

setup(
    name = "Bookload",
    description = "Download free book.",
    version = "1.1.0.0",
    # console=[cx],
    # windows=[wx],
    windows = [wx]
)