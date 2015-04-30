class Movie(object):
    """Represents a James Bond Movie"""

    def __init__(self, title, cinedate):
        self.title = title
        self.cinedate = cinedate

        self.directors = []
        self.actors = []
        self.soundtrack = []

    @property
    def directors(self):
        return self.__directors

    @directors.setter
    def directors(self, val):
        self.__directors = val

    @property
    def actors(self):
        return self.__actors

    @actors.setter
    def actors(self, val):
        self.__actors = val

    @property
    def soundtrack(self):
        return self.__soundtrack

    @soundtrack.setter
    def soundtrack(self, val):
        self.__soundtrack = val

    def jdefault(o):
        return o.__dict__


