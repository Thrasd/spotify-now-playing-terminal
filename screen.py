import curses
from time import sleep, time

from pyfiglet import Figlet

from dbus_api import DbusAPI, DBusResult
from text_scrolling import TextScrolling


class Screen:
    def __init__(self, title_text: str, dbus: DbusAPI, animation_speed: int, title_as_text=False, use_vlc=False):
        # Properties
        self.title_as_text = title_as_text
        self.title_text = title_text
        self.dbus_api = dbus
        self.use_vlc = use_vlc  # Use VLC? (NOTE: currently only experimental)
        self.animation_speed = animation_speed

        # Store information for current track
        self.track_info = {'track_id': '', 'lines': [], 'playback_status': None}

    def get_lines(self, result: DBusResult, screen_width: int):
        # If it is not the same track, update the lines
        if self.track_info['track_id'] != result.track_id:
            self.track_info['track_id'] = result.track_id
            self.track_info['lines'] = [TextScrolling(x, screen_width) for x in result.lines]
            self.track_info['playback_status'] = None

        # Show the paused text
        if result.playback_status.lower() == 'paused':
            if self.track_info['playback_status'] is None:
                self.track_info['playback_status'] = TextScrolling('(Paused)', screen_width)
        else:
            self.track_info['playback_status'] = None

        # Return the lines
        if self.track_info['playback_status'] is not None:
            return self.track_info['lines'] + [self.track_info['playback_status'], ]
        return self.track_info['lines']

    def __init_title(self, screen_width: int):
        if self.title_as_text:
            self.title = TextScrolling(self.title_text, screen_width, is_multi_line=False)
        else:
            title_ascii = Figlet(font='small').renderText(self.title_text).split('\n')
            self.title = TextScrolling(title_ascii, screen_width, is_multi_line=True)

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

        self.__init_title(width)

        result = None
        song_update_time = 1  # We want to update the song information once every second
        last_song_update = 0

        # Do stuff
        while True:
            # Clear screen
            stdscr.clear()

            # Draw the title
            row_index = self.title.draw_text(stdscr, 0)

            # Get now playing information (But only once every second
            if time() > (last_song_update + song_update_time):
                result = self.dbus_api.get_vlc_now_playing() if self.use_vlc else self.dbus_api.get_spotify_now_playing()
                last_song_update = time()

            for line in self.get_lines(result, width):
                row_index = line.draw_text(stdscr, row_index)

            # Refresh to draw on screen
            stdscr.refresh()

            # Sleep (This is our animation speed)
            sleep(self.animation_speed)
