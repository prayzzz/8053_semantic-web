from datetime import datetime, timedelta
from multiprocessing import Pool

from bs4 import BeautifulSoup
from rdflib import Namespace, Graph, URIRef, RDF, RDFS, Literal, BNode, XSD

import common

__author__ = 'prayzzz'

EP = "http://www.officialcharts.com/charts/singles-chart/%s/"

BASE_URI = "http://imn.htwk-leipzig.de/pbachman/ontologies/charts#%s"
NS_CHARTS = Namespace("http://imn.htwk-leipzig.de/pbachman/ontologies/charts#")
NS_DBPEDIA_OWL = Namespace("http://dbpedia.org/ontology/")
NS_DBPPROP = Namespace("http://dbpedia.org/property/")


def toRdf(charts):
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

            song = URIRef(BASE_URI % common.encodeString(t["artist"] + "-" + t["title"]))
            g.add((song, RDF.type, NS_DBPEDIA_OWL.Song))
            g.add((song, RDFS.label, Literal(t["title"])))
            g.add((song, NS_DBPPROP.title, Literal(t["title"])))
            g.add((song, NS_DBPEDIA_OWL.artist, artist))

            ranked = BNode()
            g.add((ranked, RDF.type, NS_CHARTS.RankedSong))
            g.add((ranked, NS_CHARTS.song, song))
            g.add((ranked, NS_CHARTS.position, Literal(t["pos"])))

            g.add((chart, NS_CHARTS.rankedSong, ranked))

    common.write_rdf("charts_uk.owl", g)


def process_date(current_date):
    print "Charts for %s" % current_date.strftime("%Y%m%d")
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
def main():
    start_date = datetime.strptime("07.12.2014", "%d.%m.%Y")
    end_date = datetime.strptime("01.01.2015", "%d.%m.%Y")

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

    common.write_json("charts_uk.json", charts)
    toRdf(charts)


if __name__ == "__main__":
    main()
