import json
from multiprocessing.pool import Pool
import re
import urllib2

from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal

import common

__author__ = "prayzzz"

EP_OMDB = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json"

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/omdb#%s"
NS_OMDB = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/omdb#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def toRdf(movies):
    g = Graph()
    g.bind("", NS_OMDB)
    g.bind("dbpedia-owl", NS_DBPEDIA_OWL)
    g.bind("dbpprop", NS_DBPPROP)

    for m in movies:
        movie = URIRef(BASE_URI % common.encodeString(m["title"]))
        g.add((movie, RDF.type, NS_DBPEDIA_OWL.Film))
        g.add((movie, RDFS.label, Literal(m["title"])))
        g.add((movie, NS_DBPPROP.title, Literal(m["title"])))
        g.add((movie, NS_DBPEDIA_OWL.imdbId, Literal(m["imdb_id"])))

    common.write_rdf("omdb.owl", g)


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

    entry = {"title": m["title"], "imdb_id": data["imdbID"]}
    return entry


def main():
    movies = common.read_json("tunefind.json")

    print "Processing..."

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("omdb.json", updated_movies)
    toRdf(updated_movies)


if __name__ == "__main__":
    main()
