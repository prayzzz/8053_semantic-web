from datetime import datetime, timedelta
from multiprocessing import Pool

from bs4 import BeautifulSoup

import common

__author__ = 'prayzzz'

EP = "http://www.officialcharts.com/charts/singles-chart/%s/"


def process_date(current_date):
    print "Charts for %s" % current_date.strftime("%Y%m%d")
    url = EP % current_date.strftime("%Y%m%d")

    html = common.request_url(url)
    soup = BeautifulSoup(html.replace("\n", ""))

    chart_row = soup.find("table", class_="chart-positions").find("tr", class_="")

    tracks = []
    chart = {"date": current_date.strftime("%d.%m.%Y"), "tracks": tracks}
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
    start_date = datetime.strptime("05.01.2014", "%d.%m.%Y")
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


if __name__ == "__main__":
    main()
