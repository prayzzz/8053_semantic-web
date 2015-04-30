import json
import sys
import urllib2
import base64
import gzip
import StringIO
from models.movie import Movie

__author__ = 'Patrick'

EP_MOVIE = "https://www.tunefind.com/api/v1/movie"
USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]


def parseResponse(response):
    if response.info().get('Content-Encoding') != 'gzip':
        return response.read()

    buf = StringIO.StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = json.load(f)
    return data


def main():
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')

    request = urllib2.Request(EP_MOVIE)
    request.add_header("accept", "text/html, application/json")
    request.add_header("accept-encoding", "gzip, deflate")
    request.add_header("authorization", "Basic %s" % base64string)
    request.add_header("user-agent", "Mozilla/5.0")

    data = parseResponse(urllib2.urlopen(request))

    movies = []
    for m in data["movies"]:
        movie = Movie(m["name"], m["air_date"])
        movies.append(movie)

    with open('movies.json', 'w') as outfile:
        json.dump(movies, outfile, default=jdefault)


def jdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__

if __name__ == "__main__":
    main()