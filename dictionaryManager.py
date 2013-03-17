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
    global genders
    global tenses
    western = allFamilies.AllChildLanguages()['Western']
    os.chdir("..")
    genders = [u'MALE',u'FEMALE',u'CHILD',u'AGED']
    tenses = [u'distant past', u'memorable past', u'future', u'present']

def loadimpiety():
    global western
    global genders
    global tenses
    impiety = allFamilies.AllChildLanguages()['Impiety']
    os.chdir("..")
    genders = [u'MALE',u'FEMALE',u'CHILD',u'AGED']
    tenses = [u'distant past', u'memorable past', u'future', u'present']    

def initials(actor): return '/'.join([a[0] for a in actor])

def add_qualified_nouns():
    #### WARNING: THIS ONLY WORKS IF THE ADJ IS THE FIRST ENTRY FOR THE WORD
    #### WARNING: Add plurals before using this
    global definiteness
    global nouns
    global qual_nouns
    definiteness = pickle.load(open('definiteness.pickle'))
    defins = definiteness.keys()
    nouns = [[item[0]]+item[1][0][1:] for item in western.Vocabulary.items() if item[1][0][0] == u'N']
    qual_nouns = [( CombineAffix(noun[0],definiteness[d][noun[2]]), noun[1]+u"("+d+u")", noun[2], noun[3], noun[4]) for noun in nouns for d in defins]
    ###>> pickle.dump(qual_nouns, open('qual_nouns.pickle','w'))
    for item in qual_nouns:
        word,d,g,s,l = item
        if not(word in western.Vocabulary):
            western.Vocabulary[word] = []
        western.Vocabulary[word].append([u'QUALN',d,g,s,l])

def add_conj_verbs():
    #### WARNING: THIS ONLY WORKS IF THE V IS THE FIRST ENTRY FOR THE WORD
    global agreement
    global verbs
    global tense
    tense = pickle.load(open('tense.pickle'))
    allattrib = [(g,s,l,t) for t in tense.keys() for g in genders for s in [u'LOW',u'MEDIUM',u'HIGH'] for l in [u'LIGHT',u'NEUTRAL',u'DARK']]
    agreement = pickle.load(open('agreement.pickle'))
    verbs = [[item[0]]+item[1][0][1:] for item in western.Vocabulary.items() if item[1][0][0] == u'V']
    conj_verbs = [( CombineAffix(CombineAffix(verb[0],vagree(verb[2:],attri[:3])),tense[attri[3]][verb[2]]), verb[1]+u"(actor="+initials(attri[:3])+u","+attri[3]+u")", attri[0], attri[1], attri[2]) for verb in verbs for attri in allattrib]
    ##>>> pickle.dump(conj_verbs, open('conj_verbs.pickle','w'))
    for item in conj_verbs:
        word,d,g,s,l = item
        if not(word in western.Vocabulary):
            western.Vocabulary[word] = []
        western.Vocabulary[word].append([u'CONJV',d,g,s,l])
def add_conj_adj():
    #### WARNING: THIS ONLY WORKS IF THE ADJ IS THE FIRST ENTRY FOR THE WORD
    global adj_agreement
    global adjectives
    global conj_adj
    allattrib = [u'LIGHT',u'NEUTRAL',u'DARK']
    adj_agreement = pickle.load(open('adj_agreement.pickle'))
    adjectives = [[item[0]]+item[1][0][1:] for item in western.Vocabulary.items() if item[1][0][0] == u'ADJ']
    conj_adj = [( CombineAffix(adj[0],adj_agreement[adj[4]][attri]), adj[1]+u"(actor="+attri+u")", attri) for adj in adjectives for attri in allattrib]
    ##>>> pickle.dump(conj_adj, open('conj_adj.pickle','w'))
    for item in conj_adj:
        word,d,l = item
        if not(word in western.Vocabulary):
            western.Vocabulary[word] = []
        western.Vocabulary[word].append([u'CONJADJ',d,l])

def add_pn():
    global pns
    pns = pickle.load(open('pns.pickle'))
    for word,d,g in [[pns[gender][x],u'# PN,'+gender+u','+x,gender] for gender in genders for x in [u'SINGULAR',u'PLURAL']]:
        if not(word in western.Vocabulary):
            western.Vocabulary[word] = []
        western.Vocabulary[word].append([u'PN',d,g])    

def produce_impiety():
    global impiety
    loadwestern()
    allsc = allFamilies.AllAvailableSoundChanges()
    sc = allsc['Western-Impiety']
    impiety = Language.FromSoundChange(western, "Impiety", soundChange.SoundChange.FromSoundChangeList(sc).Apply)

def flattenVocab(vocab):
    result = []
    for item in vocab.items():
        result.extend([[item[0]]+entry for entry in item[1]])
    return result

def produceGroupedVerbs(vocab):
    global fv
    global verbs
    global conjv
    global grouped_v
    fv = flattenVocab(vocab)
    verbs = [v for v in fv if v[1] == u'V']
    conjv = [cv for cv in fv if cv[1] == u'CONJV']
    grouped_v = {v[0]:(v[1:],[cv for cv in conjv if cv[2].startswith(v[2]) ]) for v in verbs}

def getTenseFromGv(gv,ii): # gv is an item from grouped_v above, ii is the index of the conjv inside the given gv
    return gv[1][1][ii][2][len(gv[1][0][1])+13:-1]

def yieldMatchingTense(gv,tense):
    v,dat = gv
    for y in dat[1]:
        if y[2][len(dat[0][1])+13:-1] == tense:
            yield (y[0],y[3:])

def yieldContainsFull(gv):
    v,dat = gv
    for y in dat[1]:
        if v in y[0]:
            yield (y[0],y[3:])

def countContainsFull(gv):
    return len(zip(range(len(gv[1][1])),yieldContainsFull(gv)))

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
