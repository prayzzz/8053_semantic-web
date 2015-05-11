__author__ = 'Patrick'

import json


def write_json(filepath, obj):
    global outfile
    with open(filepath, "w") as outfile:
        json.dump(obj, outfile)


def read_json(filepath):
    with open(filepath, "r") as infile:
        return json.load(infile)
