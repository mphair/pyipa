# -*- encoding: utf-8 -*-
###
## Convert wiktionary-export-style dictionaries to pyipa internal format
"""
The import dictionary format is a tab-separated file in the following form per line:

language<tab>word<tab>part of speech<tab># wikimedia markup of definition

Markup includes:
 * [[other word]]
 * {{grammatical note}}, e.g. {{countable}} for nouns or {{transitive}} for verbs

You can get a good starting point for natural lanauges from Wiktionary:
REMEMBER THAT USING THAT DATA REQUIRES YOU TO FOLLOW THE FREE DOCUMENTATION LICENSE TERMS.
PLEASE SEE THE SITE FOR DETAILS.

http://en.wiktionary.org/wiki/Help:FAQ#Downloading_Wiktionary

In particular, check out the "just definitions" files available at
http://toolserver.org/~enwikt/definitions/
(which is the import file format)

Currently, the "internal" format is:
word<tab>part of speech<tab># wikimedia markup of definition

which is just the same format without the language column.
So at this point, this script just strips out the first column
"""
import sys
import codecs
inFile = codecs.open(sys.argv[1], encoding="utf-8")
outFile = codecs.open(sys.argv[2], "w", encoding="utf-8")

for line in inFile:
    outFile.write(u"\t".join(line.split(u"\t")[1:]))
