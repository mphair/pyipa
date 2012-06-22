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

    ,[ u's > /_#' # word-final s removed
     , [(u"abse abs see seas"
     , u"abse ab see sea")]]

    ,[ u's > /#_' # word-initial s removed
     , [(u"abse abs see seas"
     , u"abse abs ee eas")]]

#################################################
### Not going to do this style of thing, currently.
###   Can be replicated by u"se > e /"
##    ,[ u's > /_e' # s removed when followed by an e
##     , [(u"abse abs see seas"
##     , u"abe abs ee eas")]]
    ,[ u'se > e /' # s removed when followed by an e
     , [(u"abse abs see seas"
     , u"abe abs ee eas")]]


#################################################
    ,[u'[sz] > t /' #alveolar fricatives
     ,[(u'abse abze'
         ,u'abte abte')]]
    ,[u'{alveolar fricative} > t /'
     ,[(u'abse abze'
         ,u'abte abte')]]
# todo to parse this:
# (done) 1. parse [ ] -- or terms
# >>> here >>> 2. parse { } -- ref terms


#################################################
    ,[u'{palatal plosive} > {palatal nasal} /'
      , [(u'aca ac ca c', u'aɲ̥a aɲ̥ ɲ̥a ɲ̥')
        ,(u'aɟa aɟ ɟa ɟ', u'aɲa aɲ ɲa ɲ')]
      ]
# todo to parse this:
# 1. find individual sound mappings,
#  s.t. voiced palatal plosive -> voiced palatal nasal
]

#################################################
#################################################

TO_NODE_NAME = "to"
FROM_NODE_NAME = "from"
CONDITION_NODE_NAME = "condition"
END_OF_WORD_CONDITION = "endOfWord"
START_OF_WORD_CONDITION = "startOfWord"

def ParseSoundChangeRule(ruleString):
    return SeparatedSequenceNode(
                separatorNode = OptionalWhitespaceNode()
                , initialSep = True
                , finalSep = True
                , storeSep = False
                , sequenceNodes = [
                    OrNode([
                        ManyNode(AlphaNode(), name=FROM_NODE_NAME)
                       ,GroupNode(GraphemeNode('['),ManyNode(AlphaNode(name=FROM_NODE_NAME)),GraphemeNode(']')) # inside [ ], each grapheme is an option
                    ])
                    , GraphemeNode('>')
                    , OptionalNode(AlphaNode(name=TO_NODE_NAME))
                    , GraphemeNode('/')
                    , SelectNameOneOfOrNoneNode(name=CONDITION_NODE_NAME,
                        namedOptionNodes=[
                              SequenceNode([UnderscoreNode(), HashNode()], name=END_OF_WORD_CONDITION)
                            , SequenceNode([HashNode(), UnderscoreNode()], name=START_OF_WORD_CONDITION)])
                    , EndNode()
                ]
        ).Parse(ruleString)

def CreateParserFromSoundChange(fromPatterns, condition):
    fromNodes = []
    for fromPattern in fromPatterns:
        L = GraphemeSplit(fromPattern)
        if len(L) == 1: fromNode = GraphemeNode(fromPattern, name=FROM_NODE_NAME)
        else: fromNode = SequenceNode([GraphemeNode(g) for g in L], name=FROM_NODE_NAME)
        fromNodes.append(fromNode)
    if len(fromNodes) == 1: fromNode = fromNodes[0]
    else: fromNode = OrNode(fromNodes)

    if condition == None:
        return ManyNode(OrNode([fromNode,OrNode([AlphaNode(),WhitespaceNode()])]))
    elif condition == START_OF_WORD_CONDITION:
        return SequenceNode([
            OptionalWhitespaceNode()
            , ManyNode(
                OrNode([
                    SequenceNode([
                        GraphemeNode(fromPattern, name=FROM_NODE_NAME)
                        , OptionalNode(ManyNode(AlphaNode()))
                        , OrNode([EndNode(), WhitespaceNode()])
                    ])
                    , SequenceNode([ManyNode(AlphaNode()), OptionalNode(WhitespaceNode())])
                ])
            )
        ])
    elif condition == END_OF_WORD_CONDITION:
        return SequenceNode([
            OptionalWhitespaceNode()
            , ManyNode(
                OrNode([
                    SequenceNode([
                        ManyEndsWithSubsetNode(
                            OptionalNode(AlphaNode())
                            , GraphemeNode(fromPattern, name=FROM_NODE_NAME)
                            , 1
                        )
                        , OrNode([EndNode(), WhitespaceNode()])
                    ])
                    , SequenceNode([ManyNode(AlphaNode()), OptionalNode(WhitespaceNode())])
                ])
            )
        ])

def DoReplacement(replacerPair, text):
    parser, toPattern = replacerPair
    s1, res = parser.Parse(text)
    return res.ReplaceWith({FROM_NODE_NAME: toPattern})

def CreateReplacerPair(res):
    fromPatterns = [n.Text for n in res.FindAll(FROM_NODE_NAME)]
    toSet = res.FindAll(TO_NODE_NAME)
    if len(toSet) == 0:
        toPattern = ""
    else:
        toPattern = toSet[0].Text
    conditionNodeSet = res.FindAll(CONDITION_NODE_NAME)
    if len(conditionNodeSet) == 0:
        condition = None
    else:
        condition = conditionNodeSet[0].GetSelectionName()
    return CreateParserFromSoundChange(fromPatterns, condition), toPattern

if __name__ == '__main__':
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

