import urllib2

__author__ = 'prayzzz'

from JsonHelper import *

__author__ = 'prayzzz'


def add_useragent(request):
    request.add_header("user-agent",
                       "Application for Semantic Web Lecture @ HTWK Leipzig; patrick.bachmann@stud.htwk-leipzig.de")


def request_url(url):
    """:returns string from urlopen"""

    request = urllib2.Request(url)
    add_useragent(request)

    return urllib2.urlopen(request).read()
