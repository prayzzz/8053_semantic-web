__author__ = 'Patrick'


class JSONEncodable(object):
    def json(self):
        return vars(self)