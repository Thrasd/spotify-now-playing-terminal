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
parser.add_argument('-speed', action='store', default=250, dest='animation_speed', help='The scrolling speed in milliseconds')
settings = parser.parse_args()

# Parse title
title_text = "Now Playing" if settings.title_text is None else " ".join(settings.title_text)

# DBUS Api
dbus_api = DbusAPI()

animation_speed = int(settings.animation_speed)
if animation_speed <= 0:
    animation_speed = 250

# Create screen
screen = Screen(title_text=title_text, dbus=dbus_api, animation_speed=animation_speed / 1000, title_as_text=settings.title_as_text, use_vlc=settings.vlc_as_input)

# Run curses in the wrapper
wrapper(screen.run)
