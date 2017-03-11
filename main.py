import curses
from curses import wrapper
from time import sleep

from pyfiglet import Figlet

from dbus_api import DbusAPI

# DBUS Api
dbus_api = DbusAPI()

# Figlet
figlet = Figlet(font='small')
now_playing_text = figlet.renderText('Now Playing').split('\n')

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
        artist, title, track_id, playback_status = dbus_api.get_spotify_now_playing()

        # Write artist
        row_index -= 1
        artist_text, artist_pos = get_position(width, artist, track_id)
        stdscr.addnstr(row_index, artist_pos, artist_text, width - 1)

        # Write title
        row_index += 1
        title_text, title_pos = get_position(width, title, track_id)
        stdscr.addnstr(row_index, title_pos, title_text, width - 1)

        if playback_status.lower() == "paused":
            row_index += 1
            playback_status = "(" + playback_status + ")"
            playback_pos = int((width / 2) - (len(playback_status) / 2))
            stdscr.addnstr(row_index, playback_pos, playback_status, len(playback_status))

        # Refresh to draw on screen
        stdscr.refresh()

        # TODO define the scroll speed of the text and how fast we retrieve data from spotify
        sleep(0.5)


# Run curses in the wrapper
wrapper(main)
