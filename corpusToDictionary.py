# -*- encoding: utf-8 -*-
###
# Convert a corpus into a directionary
#  Whole thing, picks up whole sentences

import sys
import codecs

lines = codecs.open(sys.argv[1]+".corpus", encoding="utf-16").readlines()
outfile = codecs.open(sys.argv[1]+".dictionary", mode="wb", encoding="utf-8")
for line in lines:
    segments = line.split(u"=")
    word = segments[0].strip()
    partOfSpeech = u"?"
    definition = u"# " + u" = ".join([segment.strip() for segment in segments[1:]])
    outfile.write(u"\t".join([word,partOfSpeech,definition])+u"\n")
outfile.close()
