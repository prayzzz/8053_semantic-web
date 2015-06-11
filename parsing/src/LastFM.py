import getopt
from multiprocessing import Pool
import sys

import pylast
from rdflib import Namespace, URIRef, Graph, RDF, Literal, RDFS

import common

__author__ = 'Patrick'

JSON_IN_FILE = "tunefind.json"
JSON_OUT_FILE = "lastfm.json"
RDF_OUT_FILE = "lastfm.ttl"
LOAD_FROM_WEB = False
CONVERT_TO_RDF = False

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#%s"
NS_LASTFM = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def convert_to_rdf():
    print ""
    print "Convert to RDF..."

    songs = common.read_json(JSON_OUT_FILE)

    g = Graph()
    g.bind("", NS_LASTFM)
    g.bind("dbpedia-owl", NS_DBPEDIA_OWL)
    g.bind("dbpprop", NS_DBPPROP)

    for s in songs:
        if "tags" not in s or len(s["tags"]) < 1:
            continue

        artist = URIRef(BASE_URI % common.encodeString(s["artist"]))
        g.add((artist, RDF.type, NS_DBPEDIA_OWL.MusicalArtist))
        g.add((artist, RDFS.label, Literal(s["artist"])))
        g.add((artist, NS_DBPPROP.name, Literal(s["artist"])))

        song = URIRef(BASE_URI % common.encodeString(u"{0:s} - {1:s}".format(s['artist'],  s["title"])))
        g.add((song, RDF.type, NS_DBPEDIA_OWL.Song))
        g.add((song, RDFS.label, Literal(u"{0:s} - {1:s}".format(s['artist'], s["title"]))))
        g.add((song, NS_DBPPROP.title, Literal(s["title"])))
        g.add((song, NS_DBPEDIA_OWL.artist, artist))

        for t in s["tags"]:
            g.add((song, NS_LASTFM.tagged, Literal(t)))

    common.write_rdf(RDF_OUT_FILE, g)


def process_songs(songs, network):
    for s in songs:
        print u"{0:s} - {1:s}".format(s["artist"], s["title"])

        try:
            result = network.get_track(s["artist"], s["title"])
        except pylast.WSError, e:
            print e.details + u" {0:s} - {1:s}".format(s["artist"], s["title"])
            continue

        try:
            top_tags = result.get_top_tags(5)
        except pylast.WSError, e:
            print e.details + u" {0:s} - {1:s}".format(s["artist"], s["title"])
            continue

        tags = s["tags"] if "tags" in s else []

        for t in top_tags:
            tags.append(t[0].name)

        s["tags"] = tags

    return songs


def load_from_web():
    print "Loading from Web..."

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    movies = common.read_json(JSON_IN_FILE)

    song_chunks = []
    for m in movies:
        if len(m["soundtrack"]) > 0:
            song_chunks.append(m["soundtrack"])

    pool = Pool(5)
    worker = [pool.apply_async(process_songs, [chunk, network]) for chunk in song_chunks]

    lastfm_songs = []
    for w in worker:
        w.wait()
        for s in w.get():
            lastfm_songs.append(s)

    common.write_json(JSON_OUT_FILE, lastfm_songs)


def main():
    if LOAD_FROM_WEB:
        load_from_web()

    if CONVERT_TO_RDF:
        convert_to_rdf()


def usage():
    print "LastFM.py"
    print ""
    print "Usage:"
    print "python LastFM.py"
    print " -w \t Load data from Web"
    print " -r \t Convert data to RDF"
    print " -k \t API Key"
    print " -s \t API Secret"


if __name__ == "__main__":
    try:
        options = getopt.getopt(sys.argv[1:], "wrs:k:", ["web", "rdf", "key=", "secret="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in options[0]:
        if opt in ('-k', '--key'):
            API_KEY = arg
        elif opt in ('-s', '--secret'):
            API_SECRET = arg
        elif opt == "-w":
            LOAD_FROM_WEB = True
        elif opt == "-r":
            CONVERT_TO_RDF = True

    main()
