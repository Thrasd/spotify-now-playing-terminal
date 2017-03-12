import curses
from time import sleep

from pyfiglet import Figlet

from dbus_api import DbusAPI


class Screen:
    def __init__(self, title_text: str, dbus: DbusAPI, title_as_text=False, use_vlc=False):
        # Title
        self.title_text = title_text
        self.title_as_text = title_as_text
        self.title_text_ascii = Figlet(font='small').renderText(self.title_text).split('\n')

        # Properties
        self.dbus_api = dbus
        self.use_vlc = use_vlc  # Use VLC? (NOTE: currently only experimental)

        # Uhm, stuff?
        self.pos_info = {'track_id': ''}

    # TODO bug in scrolling algorithm, it does not show the last character (Hardcoded extra spaces in the title/artist)
    # TODO add option to define if we should 'hang' at the end/beginning for a few seconds before starting scroll again
    def get_position(self, terminal_width, text, track_id):
        # If we can show the entire text within the width, lets just do that
        is_too_wide = terminal_width < len(text)
        if not is_too_wide or track_id is None:
            return text, int((terminal_width / 2) - (len(text) / 2))

        # The title is too long, we need to do some horizontal text scrolling
        if self.pos_info['track_id'] != track_id:
            # If it is a new song, remove all previous information in the dictionary
            self.pos_info = {'track_id': track_id}

        if text not in self.pos_info:
            out_of_bounds_count = len(text) - terminal_width
            self.pos_info[text] = {'all_text': text, 'oob_count': out_of_bounds_count, 'index': 0, 'direction': 1}

        skip_begin = int(self.pos_info[text]['index'])
        skip_end = int(self.pos_info[text]['oob_count']) - int(self.pos_info[text]['index'])

        # TODO find a better way to store these information
        new_text = self.pos_info[text]['all_text'][skip_begin:-skip_end]
        self.pos_info[text]['index'] += self.pos_info[text]['direction']
        if self.pos_info[text]['index'] >= self.pos_info[text]['oob_count'] - 1 or self.pos_info[text]['index'] == 0:
            self.pos_info[text]['direction'] *= -1
        return new_text, 1

    def run(self, stdscr):
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

            if self.title_as_text:
                title_pos = int((width / 2) - (len(self.title_text) / 2))
                stdscr.addnstr(0, title_pos, self.title_text, len(self.title_text))
                row_index = 1
            else:
                # Write ASCII art with the title
                # TODO make sure the Now Playing ASCII art can scroll as well
                np_text, np_pos = self.get_position(width, self.title_text_ascii[0], None)
                row_index = -1
                for val in self.title_text_ascii:
                    row_index += 1
                    stdscr.addstr(row_index, np_pos, str(val))

            artist, title, track_id, playback_status = self.dbus_api.get_vlc_now_playing() if self.use_vlc else self.dbus_api.get_spotify_now_playing()
            # Get song info

            # Write artist
            artist_text, artist_pos = self.get_position(width, artist, track_id)
            stdscr.addnstr(row_index, artist_pos, artist_text, width - 1)
            row_index += 1

            # Write title
            song_title_text, title_pos = self.get_position(width, title, track_id)
            stdscr.addnstr(row_index, title_pos, song_title_text, width - 1)
            row_index += 1

            # Show if we have paused the music
            if playback_status.lower() == "paused":
                playback_status = "(" + playback_status + ")"
                playback_pos = int((width / 2) - (len(playback_status) / 2))
                stdscr.addnstr(row_index, playback_pos, playback_status, len(playback_status))
                row_index += 1

            # Refresh to draw on screen
            stdscr.refresh()

            # TODO define the scroll speed of the text and how fast we retrieve data from spotify
            sleep(0.5)
