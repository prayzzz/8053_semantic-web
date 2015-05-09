__author__ = 'prayzzz'


from JSONEncodable import JSONEncodable


class Movie(JSONEncodable):
    """Represents a Movie"""

    def __init__(self, title):
        self.title = title

        self.imdb_id = ""
        self.cinedate_germany = ""
        self.cinedate_usa = ""
        self.cinedate_uk = ""
        self.directors = []
        self.cast = []
        self.soundtrack = []