import json
import re
import urllib2
from common import write_json, read_json


__author__ = "Patrick"


EP = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json"

movies = read_json("movies.json")

for m in movies:
    print("Processing %s" % m["title"])

    re_match = re.search("^(.*?)(\s\(\d{4}\))?$", m["title"])

    if len(re_match.groups()) < 2:
        title = m["title"]
    else:
        title = re_match.group(1)

    title = title.replace(" ", "+")
    url = EP % urllib2.quote(title)

    response = urllib2.urlopen(url)
    data = json.load(response)

    m["imdb_id"] = data["imdbID"]

write_json("movies.json", movies)