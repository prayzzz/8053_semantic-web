import json

__author__ = 'Patrick'

DIRECTORY = "data/"

def write_json(filepath, obj):
    global outfile
    with open(DIRECTORY + filepath, "w") as outfile:
        json.dump(obj, outfile)


def read_json(filepath):
    with open(DIRECTORY + filepath, "r") as infile:
        return json.load(infile)
