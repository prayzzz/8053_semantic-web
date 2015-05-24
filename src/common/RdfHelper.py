import urllib2

__author__ = 'Patrick'

DIRECTORY = "data/"

def write_rdf(filepath, graph):
    with open(DIRECTORY + filepath, "w") as outfile:
        outfile.write(graph.serialize(format="turtle"))

def encodeString(s):
    s2 = s.encode('utf8').replace(" ", "_")
    s2 = urllib2.quote(s2)
    return s2
