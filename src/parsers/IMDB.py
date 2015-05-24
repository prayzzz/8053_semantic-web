from multiprocessing.pool import Pool
from datetime import datetime
import re

from bs4 import BeautifulSoup
from rdflib import Namespace, Graph, URIRef, RDF, RDFS, Literal, BNode, XSD

import common

__author__ = "prayzzz"

EP_IMDB_RELEASEINFO = "http://www.imdb.com/title/%s/releaseinfo"
EP_IMDB_CAST = "http://www.imdb.com/title/%s/fullcredits"

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#%s"
NS_PB_TF = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#")
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
        g.add((mov, NS_DBPEDIA_OWL.imdbId, Literal(m["imdb_id"])))

        for s in m["directors"]:
            director = URIRef(BASE_URI % common.encodeString(s))
            g.add((director, RDF.type, NS_DBPEDIA_OWL.Person))
            g.add((director, RDFS.label, Literal(s)))
            g.add((mov, NS_DBPEDIA_OWL.director, director))

        for c in m["cast"]:
            actor = URIRef(BASE_URI % common.encodeString(c["name"]))
            g.add((actor, RDF.type, NS_DBPEDIA_OWL.Actor))
            g.add((actor, RDFS.label, Literal(c["name"])))
            g.add((mov, NS_DBPEDIA_OWL.starring, actor))

        for r in m["release_info"]:
            release = BNode()
            g.add((release, RDF.type, NS_PB_TF.ReleaseCountry))
            g.add((release, NS_DBPEDIA_OWL.publicationDate, Literal(r["date"], datatype=XSD.datetime)))
            g.add((release, NS_DBPEDIA_OWL.comment, Literal(r["event"])))
            g.add((release, NS_DBPEDIA_OWL.country, URIRef("http://dbpedia.org/resource/%s" % common.encodeString(r["country"]))))
            g.add((mov, NS_PB_TF.ReleaseCountry, release))

    common.write_rdf("imdb.owl", g)


def fetch_release_info(m):
    url = EP_IMDB_RELEASEINFO % m["imdb_id"]
    html = common.request_url(url)

    soup = BeautifulSoup(html.replace("\n", ""))
    info_row = soup.find(id="release_dates").find("tr")

    release_infos = []
    while info_row is not None:
        info = {}
        country_tag = info_row.contents[1]
        info["country"] = country_tag.text.strip()

        date_tag = country_tag.find_next_sibling("td")
        try:
            info["date"] = datetime.strptime(date_tag.text.strip(), "%d %B %Y").strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            info["date"] = datetime.strptime(date_tag.text.strip(), "%B %Y").strftime("%Y-%m-%dT%H:%M:%S")

        event_tag = date_tag.find_next_sibling("td")
        info["event"] = event_tag.text.strip()

        release_infos.append(info)
        info_row = info_row.find_next_sibling("tr")

    m["release_info"] = release_infos

    # End While


def extract_directors(soup):
    director_row = soup.find("h4", text=re.compile("Directed")).find_next_sibling("table").find("tr")
    directors = []

    while director_row is not None:
        director_tag = director_row.find("td", class_="name")
        directors.append(director_tag.text.strip())

        director_row = director_row.find_next_sibling("tr")

    return directors


def extract_cast(soup):
    info_row = soup.find(class_="cast_list").find("tr").find_next_sibling("tr")
    cast = []

    while info_row is not None:
        actor = {}
        actor_tag = info_row.find(attrs={"itemprop": "actor"})
        if actor_tag is None:
            break
        actor["name"] = actor_tag.text.strip()

        screen_name_tag = actor_tag.find_next_sibling(class_="character")
        if screen_name_tag is None:
            break

        screen_name = screen_name_tag.text.strip()
        re_match = re.search("^(.+?)(\((\w|\W)+?\))?$", screen_name)

        if len(re_match.groups()) < 2:
            actor["screen_name"] = screen_name
        else:
            actor["screen_name"] = re_match.group(1).strip()

        cast.append(actor)
        info_row = info_row.find_next_sibling("tr")

    return cast


def fetch_cast(m):
    url = EP_IMDB_CAST % m["imdb_id"]
    html = common.request_url(url)

    soup = BeautifulSoup(html.replace("\n", ""))

    # Director
    directors = extract_directors(soup)
    m["directors"] = directors

    # Cast
    cast = extract_cast(soup)
    m["cast"] = cast


def process_movie(m):
    print "{0:35} {1:10}".format(m["title"], m["imdb_id"])

    entry = {"title": m["title"], "imdb_id": m["imdb_id"]}
    fetch_release_info(entry)
    fetch_cast(entry)

    return entry


def main():
    print "Processing..."

    movies = common.read_json("omdb.json")

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("imdb.json", updated_movies)
    toRdf(updated_movies)

# Main
if __name__ == "__main__":
    main()
