import json
import sys
import urllib2
import base64
import gzip
import StringIO
from time import sleep

from rdflib import Namespace, Graph, URIRef, RDF, RDFS, Literal

import common

__author__ = 'prayzzz'

USERNAME = ""
PASSWORD = ""

EP_TUNEFIND_MOVIES = "https://www.tunefind.com/api/v1/movie"
EP_TUNEFIND_MOVIE_SONGS = "https://www.tunefind.com/api/v1/movie/%s"

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#%s"
NS_PB_TF = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def toRdf(movies):
    g = Graph()
    g.bind("", NS_PB_TF)
    g.bind("dbpedia-owl", NS_DBPEDIA_OWL)
    g.bind("dbpprop", NS_DBPPROP)

    for m in movies:
        mov = URIRef(BASE_URI % common.encodeString(m["title"]))
        g.add((mov, RDF.type, NS_DBPEDIA_OWL.Film))
        g.add((mov, RDFS.label, Literal(m["title"])))
        g.add((mov, NS_DBPPROP.title, Literal(m["title"])))

        for s in m["soundtrack"]:
            artist = URIRef(BASE_URI % common.encodeString(s["artist"]))
            g.add((artist, RDF.type, NS_DBPEDIA_OWL.MusicalArtist))
            g.add((artist, RDFS.label, s["artist"]))

            song = URIRef(BASE_URI % common.encodeString(s["title"]))
            g.add((song, RDF.type, NS_DBPEDIA_OWL.Song))
            g.add((song, RDFS.label, Literal(s["title"])))
            g.add((song, NS_DBPPROP.title, Literal(s["title"])))
            g.add((song, NS_DBPEDIA_OWL.artist, artist))

            g.add((mov, NS_PB_TF.contains, song))

    common.write_rdf("tunefind.owl", g)


def parse_response(response):
    if response.info().get('Content-Encoding') != 'gzip':
        return response.read()

    fp = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(response.read()))
    data = json.load(fp, encoding="utf-8")
    return data


def add_header(request):
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
    request.add_header("accept", "text/html, application/json")
    request.add_header("accept-encoding", "gzip, deflate")
    request.add_header("authorization", "Basic %s" % base64string)

    common.add_useragent(request)


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

        movie = {"title": m["name"], "soundtrack": get_songs(m['id'])}
        movies.append(movie)

        # One request per second
        sleep(1.1)

        if count == 10:
            break

    common.write_json("tunefind.json", movies)
    toRdf(movies)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Tunefind.py"
        print ""
        print "Usage:"
        print "python TuneFind.py [APIUserName] [APIPassword]"
        exit()

    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    main()
