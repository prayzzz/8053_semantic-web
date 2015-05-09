import sys
import urllib2

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from common import read_json, write_json


__author__ = "prayzzz"

EP_RELEASEINFO = "http://www.imdb.com/title/%s/releaseinfo"
EP_CAST = "http://www.imdb.com/title/%s/fullcredits"


def fetch_release_info(m):
    imdburl = EP_RELEASEINFO % m["imdb_id"]

    response = urllib2.urlopen(imdburl)
    html = response.read()

    soup = BeautifulSoup(html.replace("\n", ""))
    info_row = soup.find(id="release_dates").find("tr")

    release_infos = []
    while info_row is not None:
        if type(info_row) is NavigableString:
            info_row = info_row.next_sibling
            continue

        info = {}
        country_tag = info_row.contents[1]
        info["country"] = country_tag.text.strip()

        date_tag = country_tag.find_next_sibling("td")
        info["date"] = date_tag.text.strip()

        event_tag = date_tag.find_next_sibling("td")
        info["event"] = event_tag.text.strip()

        release_infos.append(info)
        info_row = info_row.next_sibling

    # End While

    info = filter(lambda x: x['event'] == "" and x['country'] == "USA", release_infos)
    if len(info) > 0:
        m["cinedate_usa"] = info[0]["date"]
    else:
        info = filter(lambda x: x['country'] == "USA", release_infos)
        if len(info) > 0:
            m["cinedate_usa"] = info[0]["date"]

    info = filter(lambda x: x['event'] == "" and x['country'] == "Germany", release_infos)
    if len(info) > 0:
        m["cinedate_germany"] = info[0]["date"]
    else:
        info = filter(lambda x: x['country'] == "Germany", release_infos)
        if len(info) > 0:
            m["cinedate_germany"] = info[0]["date"]

    info = filter(lambda x: x['event'] == "" and x['country'] == "UK", release_infos)
    if len(info) > 0:
        m["cinedate_uk"] = info[0]["date"]
    else:
        info = filter(lambda x: x['country'] == "UK", release_infos)
        if len(info) > 0:
            m["cinedate_uk"] = info[0]["date"]


def fetch_cast(m):
    imdburl = EP_CAST % m["imdb_id"]

    response = urllib2.urlopen(imdburl)
    html = response.read()

    soup = BeautifulSoup(html.replace("\n", ""))
    info_row = soup.find(class_="cast_list").find("tr").find_next_sibling("tr")

    cast = []
    while info_row is not None:
        if type(info_row) is NavigableString:
            info_row = info_row.next_sibling
            continue

        actor = {}
        actor_tag = info_row.find(attrs={"itemprop": "actor"})
        if actor_tag is None:
            break
        actor["name"] = actor_tag.text.strip()

        screen_name_tag = actor_tag.find_next_sibling(class_="character")
        if screen_name_tag is None:
            break
        actor["screen_name"] = screen_name_tag.text.strip()
        # TODO remove parenthesis ex: Wimpy Loser       (as Benjamin Laurance)

        cast.append(actor)

        info_row = info_row.next_sibling

    m["cast"] = cast

    # End While


def main():
    movies = read_json("movies.json")

    for m in movies:
        print("Processing %s %s" % (m["title"], m["imdb_id"]))

        # fetch_release_info(m)
        fetch_cast(m)

    write_json("movies.json", movies)


# Main
if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("IMDB.py")
        print("")
        print("Usage:")
        print("python IMDB [APIKey]")
        exit()

    main()