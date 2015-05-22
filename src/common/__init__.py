import urllib2

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


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
