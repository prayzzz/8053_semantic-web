import json

__author__ = 'Patrick'


EP = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json"

with open('movies.json', 'r') as infile:
    movies = json.load(infile)

for m in movies:
    url = EP % m['title']
    print(url)
