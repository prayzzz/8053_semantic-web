from multiprocessing.pool import Pool
import re
import urllib2

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from common import read_json, write_json


__author__ = "prayzzz"

EP_IMDB_RELEASEINFO = "http://www.imdb.com/title/%s/releaseinfo"
EP_IMDB_CAST = "http://www.imdb.com/title/%s/fullcredits"


def fetch_release_info(m):
    imdburl = EP_IMDB_RELEASEINFO % m["imdb_id"]

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


def extract_directors(soup):
    director_row = soup.find("h4", text=re.compile("Directed")).find_next_sibling("table").find("tr")
    directors = []

    while director_row is not None:
        if type(director_row) is NavigableString:
            director_row = director_row.next_sibling
            continue

        director_tag = director_row.find("td", class_="name")

        directors.append(director_tag.text.strip())

        director_row = director_row.next_sibling

    return directors


def extract_cast(soup):
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

        screen_name = screen_name_tag.text.strip()
        re_match = re.search("^(.+?)(\((\w|\W)+?\))?$", screen_name)

        if len(re_match.groups()) < 2:
            actor["screen_name"] = screen_name
        else:
            actor["screen_name"] = re_match.group(1).strip()

        cast.append(actor)
        info_row = info_row.next_sibling

    return cast


def fetch_cast(m):
    imdburl = EP_IMDB_CAST % m["imdb_id"]

    response = urllib2.urlopen(imdburl)
    html = response.read()

    soup = BeautifulSoup(html.replace("\n", ""))

    # Director
    directors = extract_directors(soup)
    m["directors"] = directors

    # Cast
    cast = extract_cast(soup)
    m["cast"] = cast


def process_movie(m):
    print "{0:35} {1:10}".format(m["title"], m["imdb_id"])
    fetch_release_info(m)
    fetch_cast(m)


def main():
    print "Processing..."

    movies = read_json("movies.json")

    pool = Pool(5)
    results = [pool.apply_async(process_movie, [m]) for m in movies]

    updated_movies = []
    for w in results:
        w.wait()
        updated_movies.append(w.get())

    common.write_json("movies.json", updated_movies)


# Main
if __name__ == "__main__":
    main()