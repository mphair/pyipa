# -*- encoding: utf-8 -*-
###
# Manage on-disk dictionaries of words
#

from languageFamily import *

BaseDictionaryHowTo = """
The dictionary format is a tab-separated file in the following form per line:

word<tab>part of speech<tab># wikimedia markup of definition

Markup includes:
 * [[other word]]
 * {{grammatical note}}, e.g. {{countable}} for nouns or {{transitive}} for verbs

You can get a good starting point for natural lanauges from Wiktionary:
REMEMBER THAT USING THAT DATA REQUIRES YOU TO FOLLOW THE FREE DOCUMENTATION LICENSE TERMS.
PLEASE SEE THE SITE FOR DETAILS.

http://en.wiktionary.org/wiki/Help:FAQ#Downloading_Wiktionary

In particular, check out the "just definitions" files available at

http://toolserver.org/~enwikt/definitions/

which were the original basis of the dictionary format used here.

You probably want enwikt-defs-latest-en.tsv.gz. If you want non-english langauges, you'll have to split them out yourself.
convertToInternalFormat.py strips out the language. That script can be modified to split into different languages as needed.

You can decompress that file using gzip from gzip.org.

Dictionaries are organized by family. Create a series of nested folders appropriately.
For example,

pyipa
    data
        dictionaries
            Indo-European
                Germanic
                    West Germanic
                        Anglo-Frisian
                            Anglic
                                English   <-- dictionary file

(see http://en.wikipedia.org/wiki/English_language for the above accepted family tree of English)
"""

def GetDictionariesPath():
    import sys
    import os
    if hasattr(sys.modules['__main__'], "__file__"):
        basePath = path.abspath(sys.modules['__main__'].__file__)
    elif sys.argv[0] != '':
        basePath = os.path.dirname(sys.argv[0])
    else:
        basePath = os.getcwd()
    s = os.path.join(basePath, "data", "dictionaries")
    if os.path.exists(s): return s
    else: return ""

def LoadFromDefault():
    dataPath = GetDictionariesPath()
    allFamilies = LanguageFamily("all families")
    if dataPath != "":
        allFamilies.LoadFromPath(dataPath)
    return allFamilies                                                                                                                       

if __name__ == '__main__':
    print "Loading families..."
    allFamilies = LoadFromDefault()
    if len(allFamilies.AllChildLanguages().keys()) == 0:
        print "*"*80
        print "You don't seem to have any languages"
        print "*"*80
        print BaseDictionaryHowTo
    else:
        print allFamilies.FamilyTree("*", 0)
