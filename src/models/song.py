from models.JSONEncodable import JSONEncodable

__author__ = 'Patrick'


class Song(JSONEncodable):
    """Represents a Song"""

    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

        self.mbid = ""
        self.artist_mbid = ""