import json
import re
import urllib2
from common import write_json, read_json


__author__ = "Patrick"

EP_OMDB = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json"


# Main
def main():
    movies = read_json("movies.json")

    print "Processing..."
    for m in movies:
        print m["title"]

        re_match = re.search("^(.*?)(\s\(\d{4}\))?$", m["title"])

        if len(re_match.groups()) < 2:
            title = m["title"]
        else:
            title = re_match.group(1)

        title = title.replace(" ", "+")
        url = EP_OMDB % urllib2.quote(title)

        response = urllib2.urlopen(url)
        data = json.load(response)

        m["imdb_id"] = data["imdbID"]

    write_json("movies.json", movies)


if __name__ == "__main__":
    main()