from datetime import datetime, timedelta
import time
import urllib2
from bs4 import BeautifulSoup, NavigableString

__author__ = 'Patrick'

EP = "https://www.offiziellecharts.de/charts/single/for-date-%d"


# Main
def main():
    start_date = datetime.strptime("05.01.1990", "%d.%m.%Y")
    date_delta = timedelta(days=7)

    current_date = start_date
    end_date = datetime.strptime("01.01.2015", "%d.%m.%Y")

    charts = []
    while current_date < end_date:
        print "Charts for %s" % current_date.strftime("%d.%m.%Y")
        date_in_milliseconds = time.mktime(current_date.timetuple()) * 1000

        url = EP % date_in_milliseconds
        response = urllib2.urlopen(url)
        html = response.read()

        soup = BeautifulSoup(html.replace("\n", ""))

        chart_row = soup.find("table", class_="table chart-table").find("tr", class_="drill-down-link")

        tracks = []
        chart = {"date": current_date, "tracks": tracks}
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

        charts.append(chart)
        current_date = current_date + date_delta


if __name__ == "__main__":
    main()
