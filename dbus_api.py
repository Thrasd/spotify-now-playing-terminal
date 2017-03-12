import locale

import dbus
from dbus import DBusException


class DbusAPI:
    def __init__(self):
        self.session_bus = dbus.SessionBus()

        # Spotify Properties
        self.spotify_bus = None
        self.spotify_properties = None
        self.spotify_is_loaded = False
        self.spotify_error_message = ("[Spotify not found]", "[Are you sure spotify is running?]", "spotify-not-running", "",)

        # VLC Properties
        self.vlc_bus = None
        self.vlc_properties = None
        self.vlc_is_loaded = False
        self.vlc_error_message = ("[VLC not found]", "[Are you sure VLC is running?]", "vlc-not-running", "",)

        # Stupid special characters, why can't we just use ASCII? :(
        locale.setlocale(locale.LC_ALL, '')
        self.language_code = locale.getpreferredencoding()

    def __init_spotify(self):
        # Do not init spotify if we have already done it
        if self.spotify_is_loaded:
            return

        try:
            # Load spotify DBUS information
            self.spotify_bus = self.session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
            self.spotify_properties = dbus.Interface(self.spotify_bus, "org.freedesktop.DBus.Properties")
            self.spotify_is_loaded = True
        except DBusException:
            self.spotify_is_loaded = False

    def __init_vlc(self):
        # Do not init VLC if we have already done so
        if self.vlc_is_loaded:
            return

        try:
            # Load VLC DBUS Information
            self.vlc_bus = self.session_bus.get_object("org.mpris.MediaPlayer2.vlc", "/org/mpris/MediaPlayer2")
            self.vlc_properties = dbus.Interface(self.vlc_bus, "org.freedesktop.DBus.Properties")
            self.vlc_is_loaded = True
        except DBusException:
            self.vlc_is_loaded = False

    def get_spotify_now_playing(self):
        # Init spotify
        self.__init_spotify()

        # We did not load spotify correct?
        if not self.spotify_is_loaded:
            return self.spotify_error_message

        try:
            # Attempt to get metadata
            metadata = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            playback_status = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        except DBusException:
            self.spotify_is_loaded = False
            return self.spotify_error_message

        # Extract information from metadata
        artists = ",".join([x for x in metadata['xesam:artist']])
        title = metadata['xesam:title']
        track_id = metadata['mpris:trackid'].split(':')[-1]

        # Returns Artist, Title, TrackId, PlaybackStatus
        return artists.encode(self.language_code), title.encode(self.language_code), track_id, playback_status

    def get_vlc_now_playing(self):
        # Init VLC
        self.__init_vlc()

        # We did not load spotify correct?
        if not self.vlc_is_loaded:
            return self.vlc_error_message

        try:
            # Attempt to get metadata
            metadata = self.vlc_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            playback_status = self.vlc_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        except DBusException:
            self.vlc_is_loaded = False
            return self.vlc_error_message

        # Extract information from metadata
        try:
            artists = metadata['xesam:title']
            # TODO remove hardcoded values for DR.DK P3 radio
            title = metadata['vlc:nowplaying'].replace('Senest spillet: ', '')
            track_id = artists
        except KeyError:
            return self.vlc_error_message

        # Returns Artist, Title, TrackId, PlaybackStatus
        return artists.encode(self.language_code), title.encode(self.language_code), track_id, playback_status
