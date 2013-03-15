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
                                English.dictionary   <-- dictionary file for English

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

def CombineAffix(word, affix):
    if affix[0] == u'-':
        return word+affix[1:]
    else:
        return affix[:-1]+word

# ===============================================
#   these were made specifically for Western
#      but they might be able to be adapted for other uses
def vagree(gsl1, gsl2):
    """This requires a global agreement variable that is a dict(dict(dict)) and all need to be prefixes"""
    return CombineAffix(
            CombineAffix(
                agreement[u'gender'][gsl1[0]][gsl2[0]]
                ,agreement[u'status'][gsl1[1]][gsl2[1]]
            ),agreement[u'lightness'][gsl1[2]][gsl2[2]])
def add_plural_nouns():
    plural_nouns = pickle.load(open("plural_nouns.pickle"))
    for n in plural_nouns:
        western.Vocabulary[n[0]] = [[u'N',n[1],n[2],n[3],n[4]]]

import pickle
import os
def loadwestern():
    global western
    western = allFamilies.AllChildLanguages()['Western']
    os.chdir("..")

def initials(actor): return '/'.join([a[0] for a in actor])

def add_conj_verbs():
    global agreement
    global verbs
    global tense
    tense = pickle.load(open('tense.pickle'))
    allattrib = [(g,s,l,t) for t in tense.keys() for g in [u'MALE',u'FEMALE',u'CHILD',u'AGED'] for s in [u'LOW',u'MEDIUM',u'HIGH'] for l in [u'LIGHT',u'NEUTRAL',u'DARK']]
    agreement = pickle.load(open('agreement.pickle'))
    verbs = [[item[0]]+item[1][0][1:] for item in western.Vocabulary.items() if item[1][0][0] == u'V']
    conj_verbs = [( CombineAffix(CombineAffix(verb[0],vagree(verb[2:],attri[:3])),tense[attri[3]][verb[2]]), verb[1]+u"(actor="+initials(attri[:3])+u","+attri[3]+u")", attri[0], attri[1], attri[2]) for verb in verbs for attri in allattrib]
    ##>>> pickle.dump(conj_verbs, open('conj_verbs.pickle','w'))
    for item in conj_verbs:
        word,d,g,s,l = item
        if not(word in western.Vocabulary):
            western.Vocabulary[word] = []
        western.Vocabulary[word].append([u'CONJV',d,g,s,l])
# ===============================================

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

    import soundChange
    sc = soundChange.SoundChange([u"\u0283 > st / _{vowel}"], {"vowel": ipaParse.ALL_VOWELS})
    pnw = allFamilies["ProtoNorthwestern"]
    fakeNW = Language.FromSoundChange(pnw, "fake northwestern", sc.Apply)
