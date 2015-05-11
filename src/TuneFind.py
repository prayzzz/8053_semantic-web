import json
import sys
import urllib2
import base64
import gzip
import StringIO
from time import sleep

import common


__author__ = 'prayzzz'

EP_TUNEFIND_MOVIES = "https://www.tunefind.com/api/v1/movie"
EP_TUNEFIND_MOVIE_SONGS = "https://www.tunefind.com/api/v1/movie/%s"
USERNAME = ""
PASSWORD = ""


def parse_response(response):
    if response.info().get('Content-Encoding') != 'gzip':
        return response.read()

    buf = StringIO.StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = json.load(f)
    return data


def add_header(request):
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
    request.add_header("accept", "text/html, application/json")
    request.add_header("accept-encoding", "gzip, deflate")
    request.add_header("authorization", "Basic %s" % base64string)
    request.add_header("user-agent", "Mozilla/5.0")


def get_songs(movieid):
    request = urllib2.Request(EP_TUNEFIND_MOVIE_SONGS % movieid)
    add_header(request)

    songdata = parse_response(urllib2.urlopen(request))

    songs = []
    for s in songdata["songs"]:
        if s["confidence"] != "high":
            continue

        song = {"title": s["name"], "artist": s["artist"]["name"]}
        songs.append(song)

    return songs


def main():
    request = urllib2.Request(EP_TUNEFIND_MOVIES)
    add_header(request)

    moviedata = parse_response(urllib2.urlopen(request))

    count = 0
    movies = []
    print "Adding..."
    for m in moviedata["movies"]:
        count += 1
        print "#%02d: %s" % (count, m["name"])

        movie = {"name": m["name"], "soundtrack": get_songs(m['id'])}
        movies.append(movie)

        # One request per second
        sleep(1.1)

        if count == 10:
            break

    common.write_json("movies.json", movies)


# Main
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Tunefind.py"
        print ""
        print "Usage:"
        print "python tuneFindFetcher [APIUserName] [APIPassword]"
        exit()

    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    main()