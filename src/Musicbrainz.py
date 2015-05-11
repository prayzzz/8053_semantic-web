import musicbrainzngs
import common

__author__ = 'prayzzz'


def main():
    musicbrainzngs.set_useragent("Semantic Web Project", "0.1", "https://github.com/prayzzz/movie-soundtrack-events")

    movies = common.read_json("movies.json")
    print "Processing"
    for m in movies:
        print "{0:35} {1:10}".format(m["title"], m["imdb_id"])

        for s in m["soundtrack"]:
            result = musicbrainzngs.search_recordings(artist=s["artist"], release=s["title"], limit=1)

            if len(result) > 0:
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
            else:
                print u"Song not found {0:s} - {1:s}".format(s["artist"], s["title"])

    common.write_json("movies.json", movies)

if __name__ == "__main__":
    main()
