from multiprocessing import Pool
import sys

import pylast
import common


__author__ = 'Patrick'

API_KEY = ""
API_SECRET = ""


def process_song(s, network):
    # try:
    #     result = network.get_track_by_mbid(s["mbid"])
    # except pylast.WSError:
    #     result = None

    # if result is None:
    try:
        result = network.get_track(s["artist"], s["title"])
    except pylast.WSError, e:
        print e.details + u" {0:s} - {1:s}".format(s["artist"], s["title"])
        return

    try:
        top_tags = result.get_top_tags(5)
    except pylast.WSError, e:
        print e.details + u" {0:s} - {1:s}".format(s["artist"], s["title"])
        return

    tags = s["tags"] if "tags" in s else []

    for t in top_tags:
        tags.append(t[0].name)

    s["tags"] = tags


def process_movie(m):
    api_key = sys.argv[1]
    api_secret = sys.argv[2]
    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

    print "{0:35}".format(m["title"])

    songs = list(m["soundtrack"])
    for s in songs:
        process_song(s, network)

    return songs


def main():
    print "Processing"

    movies = common.read_json("tunefind.json")

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("lastfm.json", updated_movies)

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
