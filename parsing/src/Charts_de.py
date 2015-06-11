from datetime import datetime, timedelta
import getopt
from multiprocessing import Pool
import time

from bs4 import BeautifulSoup
from rdflib import Graph, Namespace, Literal, RDFS, URIRef, RDF, XSD, BNode
import sys

import common

__author__ = 'prayzzz'

EP = "https://www.offiziellecharts.de/charts/single/for-date-%d"

JSON_OUT_FILE = "charts_de.json"
RDF_OUT_FILE = "charts_de.ttl"
LOAD_FROM_WEB = False
CONVERT_TO_RDF = False
STARTDATE = "01.01.2000"
ENDDATE = "31.05.2015"
POSITION_LIMIT = 50

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/charts_de#%s"
NS_CHARTS = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/charts_de#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def convert_to_rdf():
    print ""
    print "Convert to RDF..."

    charts = common.read_json(JSON_OUT_FILE)

    g = Graph()
    g.bind("", NS_CHARTS)
    g.bind("dbpedia-owl", NS_DBPEDIA_OWL)
    g.bind("dbpprop", NS_DBPPROP)

    for c in charts:
        if c["date"] < "2005-01-01T00:00:00":
            continue

        chart = URIRef(
            BASE_URI % common.encodeString(datetime.strptime(c["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")))
        g.add((chart, RDF.type, NS_CHARTS.Chart))
        g.add((chart, NS_DBPEDIA_OWL.publicationDate, Literal(c["date"] + "Z", datatype=XSD.dateTime)))

        for t in c["tracks"]:
            artist = URIRef(BASE_URI % common.encodeString(t["artist"]))
            g.add((artist, RDF.type, NS_DBPEDIA_OWL.MusicalArtist))
            g.add((artist, RDFS.label, Literal(t["artist"])))
            g.add((artist, NS_DBPPROP.name, Literal(t["artist"])))

            song = URIRef(BASE_URI % common.encodeString(t["title"]))
            g.add((song, RDF.type, NS_DBPEDIA_OWL.Song))
            g.add((song, RDFS.label, Literal(u"{0:s} - {1:s}".format(t['artist'], t["title"]))))
            g.add((song, NS_DBPPROP.title, Literal(t["title"])))
            g.add((song, NS_DBPEDIA_OWL.artist, artist))

            ranked = BNode()
            g.add((ranked, RDF.type, NS_CHARTS.RankedSong))
            g.add((ranked, NS_CHARTS.song, song))
            g.add((ranked, NS_CHARTS.position, Literal(t["pos"], datatype=XSD.integer)))
            g.add((ranked, RDFS.label, Literal(u"{0:s}: {1:s} - {2:s}".format(t["pos"], t['artist'], t["title"]))))

            g.add((chart, NS_CHARTS.rankedSong, ranked))

    common.write_rdf(RDF_OUT_FILE, g)


def process_date(current_date):
    print u"{0:s}".format(current_date.strftime("%d.%m.%Y"))

    date_in_milliseconds = time.mktime(current_date.timetuple()) * 1000
    url = EP % date_in_milliseconds

    html = common.request_url(url)
    soup = BeautifulSoup(html.replace("\n", ""), from_encoding="utf-8")

    chart_row = soup.find("table", class_="table chart-table").find("tr", class_="drill-down-link")

    tracks = []
    chart = {"date": current_date.strftime("%Y-%m-%dT%H:%M:%S"), "tracks": tracks}
    while chart_row is not None:
        pos_tag = chart_row.find("td", class_="ch-pos")
        pos = pos_tag.text.strip()

        info_tag = chart_row.find("td", class_="ch-info")
        artist = info_tag.find("span", class_="info-artist").text.strip()
        title = info_tag.find("span", class_="info-title").text.strip()

        track = {"artist": artist, "title": title, "pos": pos}
        tracks.append(track)

        chart_row = chart_row.find_next_sibling("tr", class_="drill-down-link")

        if pos == str(POSITION_LIMIT):
            break

    return chart


# Main
def load_from_web():
    print "Loading from Web..."

    start_date = datetime.strptime(STARTDATE, "%d.%m.%Y")
    end_date = datetime.strptime(ENDDATE, "%d.%m.%Y")

    date_delta = timedelta(days=7)
    current_date = start_date

    days = []
    while current_date < end_date:
        days.append(current_date)
        current_date = current_date + date_delta

    pool = Pool(5)
    results = [pool.apply_async(process_date, [d]) for d in days]

    charts = []
    for w in results:
        w.wait()
        charts.append(w.get())

    common.write_json(JSON_OUT_FILE, charts)


def usage():
    print "Charts_de.py"
    print ""
    print "Usage:"
    print "python Charts_de.py"
    print " -w \t Load data from Web"
    print " -r \t Convert data to RDF"
    print " -s \t Startdate"
    print " -e \t Enddate"


def main():
    if LOAD_FROM_WEB:
        load_from_web()

    if CONVERT_TO_RDF:
        convert_to_rdf()

# Main
if __name__ == "__main__":
    try:
        options = getopt.getopt(sys.argv[1:], "wrs:e:", ["web", "rdf", "startdate=", "enddate="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in options[0]:
        if opt == "-w":
            LOAD_FROM_WEB = True
        elif opt == "-r":
            CONVERT_TO_RDF = True
        elif opt in ('-s', '--startdate'):
            POSITION_LIMIT = STARTDATE
        elif opt in ('-e', '--enddate'):
            POSITION_LIMIT = ENDDATE

    main()
