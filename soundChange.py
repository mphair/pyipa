# -*- encoding: utf-8 -*-
###
# IPA-based sound change
#  Understands multi-codepoint graphemes

from ipaParse import *
WHITESPACE_INCLUDES_NEWLINES = False # turn off newlines as wspace in ipaParse

TESTS = [
#################################################
    [u'b > p /' # b goes to p
    , [(u"a b c d"
    , u"a p c d")]]
# todo to parse this:
# (done) 1. parse into the three parts, A > B / C
# (done) 2. add ability to name parts

# todo to apply this:
# (done) 1. Build parser from rule
# (done) 2. read word list
# (done) 3. apply rule appropriately


#################################################
    ,[ u's > /_#' # word-final s removed
     , [(u"abse abs see"
     , u"abse ab see")]]
# todo to parse this:
# 1. >>> here >>> parse into the three parts, A > B / C
# 2. parse condition
#   a. parse word boundaries #
#   b. parse position indicator _

# todo to apply this:
# 1. parse rule
# 2. read word list
# 3. apply rule appropriately


#################################################
    ,[u'[sz] > t /' #alveolar fricatives
     ,[(u'abse abze'
         ,u'abte abte')]]
    ,[u'{alveolar fricative} > t /'
     ,[(u'abse abze'
     ,u'abte abte')]]
# todo to parse this:
# 1. parse [ ] or terms 
# 2. parse { } ref terms


#################################################
    ,[u'{palatal plosive} > {palatal nasal} /'
      , [(u'ac', u'aɲ̥')
        ,(u'aɟ', u'aɲ')]
      ]
# todo to parse this:
# 1. find individual sound mappings,
#  s.t. voiced palatal plosive -> voiced palatal nasal
]

#################################################
#################################################

def ParseSoundChangeRule(ruleString):
    return SeparatedSequenceNode(
                separatorNode = OptionalWhitespaceNode()
                , initialSep = True
                , finalSep = True
                , storeSep = False
                , sequenceNodes = [
                    AlphaNode(name="from")
                    , GraphemeNode('>')
                    , OptionalNode(AlphaNode(name="to"))
                    , GraphemeNode('/')
                    # not doing conditions currently
                    , EndNode()
                ]
        ).Parse(ruleString)

def CreateParserFromSoundChange(fromPattern): # no conditions yet
    return ManyNode(OrNode([GraphemeNode(fromPattern, name="from"),OrNode([AlphaNode(),WhitespaceNode()])]))

def DoReplacement(replacerPair, text):
    parser, toPattern = replacerPair
    s1, res = parser.Parse(text)
    return res.ReplaceWith({"from": toPattern})

def CreateReplacerPair(res):
    fromPattern = res.FindAll("from")[0].Text
    toPattern = res.FindAll("to")[0].Text
    return CreateParserFromSoundChange(fromPattern), toPattern

for test in TESTS:
    rule, L = test
    s1, res = ParseSoundChangeRule(rule)
    if res == None:
        print rule, ": DID NOT PARSE"
        continue
    rp = CreateReplacerPair(res)
    for entry in L:
        word,expected = entry
        try:
            actual = DoReplacement(rp, word)
            if (actual != expected):
                print rule, ": expected=", expected, "actual=", actual
            else:
                print rule, ": SUCCESS"
        except Exception as e:
            print rule, entry, ": EXCEPTION", e

