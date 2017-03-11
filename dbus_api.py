import locale

import dbus
from dbus import DBusException


class DbusAPI:
    def __init__(self):
        self.session_bus = dbus.SessionBus()

        # Spotify properties
        self.spotify_bus = None
        self.spotify_properties = None
        self.has_loaded_spotify = False
        self.has_not_loaded_spotify_message = ("[Spotify not found]", "[Are you sure spotify is running?]", "spotify-not-running",)

        # Stupid special characters, why can't we just use ASCII? :(
        locale.setlocale(locale.LC_ALL, '')
        self.language_code = locale.getpreferredencoding()

    def __init_spotify(self):
        # Do not init spotify if we have already done it
        if self.has_loaded_spotify:
            return

        try:
            # Load spotify DBUS information
            self.spotify_bus = self.session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
            self.spotify_properties = dbus.Interface(self.spotify_bus, "org.freedesktop.DBus.Properties")
            self.has_loaded_spotify = True
        except DBusException:
            self.has_loaded_spotify = False

    def get_spotify_now_playing(self):
        # Init spotify
        self.__init_spotify()

        # We did not load spotify correct?
        if not self.has_loaded_spotify:
            return self.has_not_loaded_spotify_message

        # Attempt to get metadata
        try:
            metadata = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        except DBusException:
            self.has_loaded_spotify = False
            return self.has_not_loaded_spotify_message

        # Extract information from metadata
        artists = ",".join([x for x in metadata['xesam:artist']])
        title = metadata['xesam:title']
        track_id = metadata['mpris:trackid'].split(':')[-1]

        # Returns Artist, Title, TrackId
        return artists.encode(self.language_code), title.encode(self.language_code), track_id,
