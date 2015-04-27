class bondMovie(object):
    """Represents a James Bond Movie"""

    def __init__(self, title, bond):
        self.title = title
        self.bond = bond
        
        self.girls = []
        self.villians = []
        self.themeSong = ""
        self.cars = []

    @property
    def girls(self):
        return self.__girls

    @girls.setter
    def girls(self, val):
        self.__girls = val

    @property
    def villians(self):
        return self.__villians

    @villians.setter
    def villians(self, val):
        self.__villians = val

    @property
    def themeSong(self):
        return self.__themeSong

    @themeSong.setter
    def themeSong(self, val):
        self.__themeSong = val

    @property
    def cars(self):
        return self.__cars

    @cars.setter
    def cars(self, val):
        self.__cars = val


