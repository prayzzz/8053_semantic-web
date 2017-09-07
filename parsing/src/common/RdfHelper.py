import urllib2

__author__ = 'Patrick'

DIRECTORY = "data/"

def write_rdf(filepath, graph):
    print "Writing %s..." % filepath
    with open(DIRECTORY + filepath, "w") as outfile:
        data = graph.serialize(format="turtle")
        outfile.write(data)

def encodeString(s):
    s2 = s.encode('utf8').replace(" ", "_")
    s2 = urllib2.quote(s2, "/()[]")
    return s2
