__author__ = 'prayzzz'


from HTMLParser import HTMLParser


class IMDB_ReleaseInfo_Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print "Start tag:", tag
        for attr in attrs:
            print "     attr:", attr

    def handle_endtag(self, tag):
        print "End tag  :", tag
