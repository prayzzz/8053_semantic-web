"""
    This skript is unfinished and was not used
"""

from multiprocessing.pool import Pool
import musicbrainzngs
import common

__author__ = 'prayzzz'


def process_song(s):
    result = musicbrainzngs.search_recordings(artist=s["artist"], release=s["title"], limit=1)

    if len(result) < 1:
        print u"Song not found {0:s} - {1:s}".format(s["artist"], s["title"])
        return

    recording = result["recording-list"][0]
    s["mbid"] = recording["id"]
    s["artist_mbid"] = recording["artist-credit"][0]["artist"]["id"]

    if "length" in recording:
        s["length"] = recording["length"]

    if "tag-list" in recording:
        tags = []
        for t in recording["tag-list"]:
            tags.append(t["name"])
        s["tags"] = tags
    else:
        print u"Tags not found for {0:s} - {1:s}".format(s["artist"], s["title"])


def process_movie(m):
    musicbrainzngs.set_useragent(
        "Application for Semantic Web Lecture @ HTWK Leipzig; patrick.bachmann@stud.htwk-leipzig.de", "0.1")
    print "{0:35} {1:10}".format(m["title"], m["imdb_id"])

    for s in m["soundtrack"]:
        process_song(s)

    return m


def main():
    print "Processing"

    movies = common.read_json("tunefind.json")

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("musicbrainz.json", updated_movies)


if __name__ == "__main__":
    main()
