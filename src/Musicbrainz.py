from collections import namedtuple
import json
import sys
import urllib2
import base64
import gzip
import StringIO
from models.movie import Movie
from models.Song import Song

__author__ = 'Patrick'


movies = []

with open('movies.json', 'r') as infile:
    movies = json.load(infile)

movies[0]['directors'] = []
print(movies)

