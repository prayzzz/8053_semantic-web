from datetime import datetime, timedelta
import getopt
from multiprocessing import Pool

from bs4 import BeautifulSoup
from rdflib import Namespace, Graph, URIRef, RDF, RDFS, Literal, BNode, XSD
import sys

import common

__author__ = 'prayzzz'

EP = "http://www.officialcharts.com/charts/singles-chart/%s/"

JSON_OUT_FILE = "charts_uk.json"
RDF_OUT_FILE = "charts_uk.ttl"
LOAD_FROM_WEB = False
CONVERT_TO_RDF = False
STARTDATE = "07.12.2014"
ENDDATE = "01.01.2015"

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/charts#%s"
NS_CHARTS = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/charts#")
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
        chart = URIRef(
            BASE_URI % common.encodeString(datetime.strptime(c["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")))
        g.add((chart, RDF.type, NS_CHARTS.Chart))
        g.add((chart, NS_DBPEDIA_OWL.publicationDate, Literal(c["date"], datatype=XSD.datetime)))

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

    url = EP % current_date.strftime("%Y%m%d")

    html = common.request_url(url)
    soup = BeautifulSoup(html.replace("\n", ""))

    chart_row = soup.find("table", class_="chart-positions").find("tr", class_="")

    tracks = []
    chart = {"date": current_date.strftime("%Y-%m-%dT%H:%M:%S"), "tracks": tracks}
    while chart_row is not None:
        if len(chart_row.contents) < 19:
            chart_row = chart_row.find_next_sibling("tr", class_="")
            continue

        pos = chart_row.find("span", class_="position").text.strip()
        title = chart_row.find("div", class_="title").text.strip()
        artist = chart_row.find("div", class_="artist").text.strip()

        track = {"artist": artist, "title": title, "pos": pos}
        tracks.append(track)

        chart_row = chart_row.find_next_sibling("tr", class_="")

    return chart


# Main
def load_from_web():
    print "Loading from web..."

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
    print "Charts_uk.py"
    print ""
    print "Usage:"
    print "python Charts_uk.py"
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
            LIMIT = STARTDATE
        elif opt in ('-e', '--enddate'):
            LIMIT = ENDDATE
    main()
