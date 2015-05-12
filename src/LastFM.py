from multiprocessing import Pool
import sys

import pylast
import common


__author__ = 'Patrick'

API_KEY = ""
API_SECRET = ""

def process_song(s, network):
    try:
        result = network.get_track_by_mbid(s["mbid"])
    except pylast.WSError:
        result = None

    if result is None:
        try:
            result = network.get_track(s["artist"], s["title"])
        except pylast.WSError:
            result = None

    if result is None:
        print u"Song not found {0:s} - {1:s}".format(s["artist"], s["title"])
        return

    try:
        top_tags = result.get_top_tags(5)
    except pylast.WSError:
        return

    tags = s["tags"] if "tags" in s else []

    for t in top_tags:
        tags.append(t[0].name)

    s["tags"] = tags


def process_movie(m):
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    print "{0:35} {1:10}".format(m["title"], m["imdb_id"])

    for s in m["soundtrack"]:
        process_song(s, network)


def main():
    print "Processing"

    movies = common.read_json("movies.json")

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("movies.json", updated_movies)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "LastFM.py"
        print ""
        print "Usage:"
        print "python LastFM.py [API_KEY] [API_SECRECT]"
        exit()

    API_KEY = sys.argv[1]
    API_SECRET = sys.argv[2]
    main()