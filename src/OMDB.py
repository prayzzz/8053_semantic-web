import json
from multiprocessing.pool import Pool
import re
import urllib2
import common


__author__ = "Patrick"


EP_OMDB = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json"


# Main
def process_movie(m):
    print m["title"]

    re_match = re.search("^(.*?)(\s\(\d{4}\))?$", m["title"])

    if len(re_match.groups()) < 2:
        title = m["title"]
    else:
        title = re_match.group(1)

    title = title.replace(" ", "+")
    url = EP_OMDB % urllib2.quote(title)
    data = json.loads(common.request_url(url))

    m["imdb_id"] = data["imdbID"]

    return m


def main():
    movies = common.read_json("movies.json")

    print "Processing..."

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("movies.json", updated_movies)


if __name__ == "__main__":
    main()