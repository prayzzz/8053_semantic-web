from multiprocessing import Pool
import sys

import pylast
from rdflib import Namespace, URIRef, Graph, RDF, Literal, RDFS

import common

__author__ = 'Patrick'


BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#%s"
NS_LASTFM = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def toRdf(songs):
    g = Graph()
    g.bind("", NS_LASTFM)
    g.bind("dbpedia-owl", NS_DBPEDIA_OWL)
    g.bind("dbpprop", NS_DBPPROP)

    for s in songs:
        artist = URIRef(BASE_URI % common.encodeString(s["artist"]))
        g.add((artist, RDF.type, NS_DBPEDIA_OWL.MusicalArtist))
        g.add((artist, RDFS.label, Literal(s["artist"])))
        g.add((artist, NS_DBPPROP.name, Literal(s["artist"])))

        song = URIRef(BASE_URI % common.encodeString(s["title"]))
        g.add((song, RDF.type, NS_DBPEDIA_OWL.Song))
        g.add((song, RDFS.label, Literal(s["title"])))
        g.add((song, NS_DBPPROP.title, Literal(s["title"])))
        g.add((song, NS_DBPEDIA_OWL.artist, artist))

        if "tags" in s:
            for t in s["tags"]:
                tag = URIRef(BASE_URI % common.encodeString(t))
                g.add((tag, NS_LASTFM.label, Literal(s)))
                g.add((song, NS_DBPEDIA_OWL.tag, tag))

    common.write_rdf("lastfm.owl", g)

def process_song(s, network):
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

def process_songs(songs, network):
    for s in songs:
        process_song(s, network)

    return songs

def main():
    api_key = sys.argv[1]
    api_secret = sys.argv[2]
    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

    print "Processing"

    movies = common.read_json("tunefind.json")

    song_chunks = []
    for m in movies:
        song_chunks.append(m["soundtrack"])

    pool = Pool(5)
    results = [pool.apply_async(process_songs, [chunk, network]) for chunk in song_chunks]

    updated_songs = []
    for w in results:
        w.wait()
        for s in w.get():
            updated_songs.append(s)

    common.write_json("lastfm.json", updated_songs)
    toRdf(updated_songs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "LastFM.py"
        print ""
        print "Usage:"
        print "python LastFM.py [API_KEY] [API_SECRECT]"
        exit()

    main()
