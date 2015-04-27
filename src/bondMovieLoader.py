__author__ = 'Patrick'


import mechanize
import re

URL = "http://www.twerponline.net/timewell/databases/bond.htm"

browser = mechanize.Browser()
response = browser.open(URL).read()

pattern = re.compile("<a name=\"(?P<tag>[a-z0-9]*?)\">.*?<FONT color=black>(?P<title>[A-Z\s\W]*?)</B>.*?<P>")

for (letters, numbers) in re.findall(pattern, response):
    print numbers, '*', letters



