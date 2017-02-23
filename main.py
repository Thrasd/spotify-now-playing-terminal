import curses
import locale
from curses import wrapper
from time import sleep

import dbus
from dbus import DBusException
from pyfiglet import Figlet

# Make sure we can handle special characters
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

# Initialize dbus session
try:
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
except DBusException:
    print("Could not find spotify, are you sure it is running?")
    exit()

# Figlet
figlet = Figlet(font='small')
now_playing_text = figlet.renderText('Now Playing').split('\n')


def get_info():
    # Get meta-data from spotify
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    # Extract artists and title
    artists = ",".join([x for x in metadata['xesam:artist']]) + '   '
    title = metadata['xesam:title'] + '   '
    track_id = metadata['mpris:trackid'].split(':')[-1]

    # Return information
    return artists.encode(code), title.encode(code), track_id


pos_info = {'track_id': ''}


# TODO bug in scrolling algorithm, it does not show the last character (Hardcoded extra spaces in the title/artist)
# TODO add option to define if we should 'hang' at the end/beginning for a few seconds before starting scroll again
def get_position(terminal_width, text, track_id):
    global pos_info
    # If we can show the entire text within the width, lets just do that
    is_too_wide = terminal_width < len(text)
    if not is_too_wide or track_id is None:
        return text, int((terminal_width / 2) - (len(text) / 2))

    # The title is too long, we need to do some horizontal text scrolling
    if pos_info['track_id'] != track_id:
        # If it is a new song, remove all previous information in the dictionary
        pos_info = {'track_id': track_id}

    if text not in pos_info:
        out_of_bounds_count = len(text) - terminal_width
        pos_info[text] = {'all_text': text, 'oob_count': out_of_bounds_count, 'index': 0, 'direction': 1}

    skip_begin = int(pos_info[text]['index'])
    skip_end = int(pos_info[text]['oob_count']) - int(pos_info[text]['index'])

    # TODO find a better way to store these information
    new_text = pos_info[text]['all_text'][skip_begin:-skip_end]
    pos_info[text]['index'] += pos_info[text]['direction']
    if pos_info[text]['index'] >= pos_info[text]['oob_count'] - 1 or pos_info[text]['index'] == 0:
        pos_info[text]['direction'] *= -1
    return new_text, 1


def main(stdscr):
    # Configure Curses
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    # Terminal information
    height, width = stdscr.getmaxyx()

    # Do stuff
    while True:
        # Clear screen
        stdscr.clear()

        # Write ASCII art with now playing
        # TODO make sure the Now Playing ASCII art can scroll as well
        np_text, np_pos = get_position(width, now_playing_text[0], None)
        row_index = 0
        for val in now_playing_text:
            stdscr.addstr(row_index, np_pos, str(val))
            row_index += 1

        # Get song info
        artist, title, track_id = get_info()

        # Write artist
        artist_text, artist_pos = get_position(width, artist, track_id)
        stdscr.addnstr(row_index - 1, artist_pos, artist_text, width - 1)

        # Write title
        title_text, title_pos = get_position(width, title, track_id)
        stdscr.addnstr(row_index, title_pos, title_text, width - 1)

        # TODO Do we need to refresh?
        stdscr.refresh()

        # TODO define the scroll speed of the text and how fast we retrieve data from spotify
        sleep(0.5)


# Run curses in the wrapper
wrapper(main)
