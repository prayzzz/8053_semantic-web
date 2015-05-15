from datetime import datetime, timedelta
from multiprocessing import Pool
import time

from bs4 import BeautifulSoup, NavigableString
import math

import common


__author__ = 'Patrick'

EP = "https://www.offiziellecharts.de/charts/single/for-date-%d"


def process_date(current_date):
    print "Charts for %s" % current_date.strftime("%d.%m.%Y")
    date_in_milliseconds = time.mktime(current_date.timetuple()) * 1000
    url = EP % date_in_milliseconds

    html = common.request_url(url)
    soup = BeautifulSoup(html.replace("\n", ""))

    chart_row = soup.find("table", class_="table chart-table").find("tr", class_="drill-down-link")

    tracks = []
    chart = {"date": current_date.strftime("%d.%m.%Y"), "tracks": tracks}
    while chart_row is not None:
        if type(chart_row) is NavigableString:
            chart_row = chart_row.next_sibling
            continue

        pos_tag = chart_row.find("td", class_="ch-pos")
        pos = pos_tag.text.strip()

        info_tag = chart_row.find("td", class_="ch-info")
        artist = info_tag.find("span", class_="info-artist").text.strip()
        title = info_tag.find("span", class_="info-title").text.strip()

        track = {"artist": artist, "title": title, "pos": pos}
        tracks.append(track)

        chart_row = chart_row.next_sibling
    return chart


# Main
def main():
    start_date = datetime.strptime("01.01.2014", "%d.%m.%Y")
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

    common.write_json("charts.json", charts)


if __name__ == "__main__":
    main()
