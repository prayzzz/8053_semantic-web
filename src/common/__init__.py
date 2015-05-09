__author__ = 'prayzzz'
__all__ = ['write_json']

import json
from operator import methodcaller


def write_json(filepath, obj):
    global outfile
    with open(filepath, "w") as outfile:
        json.dump(obj, outfile, default=methodcaller("json"))


def read_json(filepath):
    with open(filepath, "r") as infile:
        return json.load(infile)
