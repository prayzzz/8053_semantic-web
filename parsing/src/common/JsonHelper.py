import json
import os

__author__ = 'Patrick'

DIRECTORY = "data/"


def write_json(filepath, obj):
    print "Writing %s..." % filepath

    if not os.path.isdir(DIRECTORY):
        os.mkdir(DIRECTORY)

    with open(DIRECTORY + filepath, "w") as outfile:
        json.dump(obj, outfile, encoding="utf-8")


def read_json(filepath):
    print "Reading %s..." % filepath
    with open(DIRECTORY + filepath, "r") as infile:
        return json.load(infile, encoding="utf8")
