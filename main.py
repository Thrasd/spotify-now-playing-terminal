import argparse
from curses import wrapper

from dbus_api import DbusAPI
from screen import Screen

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-tas', '--title-as-text', action='store_true', default=False, dest='title_as_text', help='Show the title as normal text')
parser.add_argument('-tt', '--title-text', action='store', default=None, dest='title_text', help='The title of the terminal window', nargs='+')
parser.add_argument('-v', '--version', action='version', version='Version 0.0.1')
parser.add_argument('-vlc', action='store_true', default=False, dest='vlc_as_input', help='Use VLC as input source')
settings = parser.parse_args()

# Parse title
title_text = "Now Playing" if settings.title_text is None else " ".join(settings.title_text)

# DBUS Api
dbus_api = DbusAPI()

# Create screen
screen = Screen(title_text, dbus_api, settings.title_as_text, settings.vlc_as_input)

# Run curses in the wrapper
wrapper(screen.run)
