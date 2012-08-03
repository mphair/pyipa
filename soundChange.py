# -*- encoding: utf-8 -*-
###
# IPA-based sound change
#  Understands multi-codepoint graphemes

from ipaParse import *
WHITESPACE_INCLUDES_NEWLINES = False # turn off newlines as wspace in ipaParse
STOP_ON_EXCEPTION = False

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

    ,[u'b > pp /' # b goes to pp
    , [(u"a b c d"
    , u"a pp c d")]]

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
    ,[ u's > /{vowel}_' # s removed after vowel
     , [(u"abse as see sase"
     , u"abse a see sae")]]

    ,[ u's > /_{vowel}' # s removed before vowel
     , [(u"abse as see sase"
     , u"abe as ee ae")]]

    ,[ u's > /{vowel}_{vowel}' # intervolic s removed
     , [(u"abse as see sase"
     , u"abse as see sae")]]
# todo:
# (done) 1. parse {vowel} (list of names to be passed in)

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
AFTER_NAMED_CONDITION = "afterNamed"
BEFORE_NAMED_CONDITION = "beforeNamed"
BETWEEN_NAMED_CONDITION = "betweenNamed"
SPECIAL_NAME = "specialName"

def ParseSoundChangeRule(ruleString, specialNames=None):
    conditions=[
          SequenceNode([UnderscoreNode(), HashNode()], name=END_OF_WORD_CONDITION)
        , SequenceNode([HashNode(), UnderscoreNode()], name=START_OF_WORD_CONDITION)
    ]
    if specialNames != None:
        conditions.extend([
            # {}_{} needs to go first, because it is a superset of the other two,
            #  the others will get recognized but not eat enough of the condition
            SequenceNode([
                GroupNode(GraphemeNode('{'),ManyNode(AlphaNode(),name=SPECIAL_NAME),GraphemeNode('}'))
                , UnderscoreNode()
                , GroupNode(GraphemeNode('{'),ManyNode(AlphaNode(),name=SPECIAL_NAME),GraphemeNode('}'))]
                , name=BETWEEN_NAMED_CONDITION)
            , SequenceNode([
                GroupNode(GraphemeNode('{'),ManyNode(AlphaNode(),name=SPECIAL_NAME),GraphemeNode('}'))
                , UnderscoreNode()]
                , name=AFTER_NAMED_CONDITION)
            , SequenceNode([
                UnderscoreNode()
                , GroupNode(GraphemeNode('{'),ManyNode(AlphaNode(),name=SPECIAL_NAME),GraphemeNode('}'))]
                , name=BEFORE_NAMED_CONDITION)
        ])

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
                    , OptionalNode(ManyNode(AlphaNode(), name=TO_NODE_NAME))
                    , GraphemeNode('/')
                    , SelectNameOneOfOrNoneNode(name=CONDITION_NODE_NAME, namedOptionNodes=conditions)
                    , EndNode()
                ]
        ).Parse(ruleString)

def CreateParserFromSoundChange(fromPatterns, condition, conditionArgs, specialNames=None):
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
    elif condition == BETWEEN_NAMED_CONDITION:
        return ManyNode(
            OrNode([
                SequenceNode([
                    GraphemeNode(specialNames[conditionArgs[0]])
                    , GraphemeNode(fromPattern, name=FROM_NODE_NAME)
                    , GraphemeNode(specialNames[conditionArgs[1]])])
                , AlphaNode()
                , OrNode([EndNode(), WhitespaceNode()])
            ])
        )
    elif condition == AFTER_NAMED_CONDITION:
        return ManyNode(
            OrNode([
                SequenceNode([GraphemeNode(specialNames[conditionArgs[0]]), GraphemeNode(fromPattern, name=FROM_NODE_NAME)])
                , AlphaNode()
                , OrNode([EndNode(), WhitespaceNode()])
            ])
        )
    elif condition == BEFORE_NAMED_CONDITION:
        return ManyNode(
            OrNode([
                SequenceNode([GraphemeNode(fromPattern, name=FROM_NODE_NAME), GraphemeNode(specialNames[conditionArgs[0]])])
                , AlphaNode()
                , OrNode([EndNode(), WhitespaceNode()])
            ])
        )

SPECIAL_NAME = "specialName"

def DoReplacement(replacerPair, text):
    parser, toPattern = replacerPair
    s1, res = parser.Parse(text)
    return res.ReplaceWith({FROM_NODE_NAME: toPattern})

def CreateReplacerPair(res, specialNames=None):
    fromPatterns = [n.Text for n in res.FindAll(FROM_NODE_NAME)]
    toSet = res.FindAll(TO_NODE_NAME)
    if len(toSet) == 0:
        toPattern = ""
    else:
        toPattern = toSet[0].Text
    conditionNodeSet = res.FindAll(CONDITION_NODE_NAME)
    conditionArgs = None
    if len(conditionNodeSet) == 0:
        condition = None
    else:
        condition = conditionNodeSet[0].GetSelectionName()
        if condition in (AFTER_NAMED_CONDITION, BEFORE_NAMED_CONDITION, BETWEEN_NAMED_CONDITION):
            specials = conditionNodeSet[0].FindAll(SPECIAL_NAME)
            conditionArgs = [special.Text for special in specials]
    return CreateParserFromSoundChange(fromPatterns, condition, conditionArgs, specialNames), toPattern

class SoundChange:
    def __init__(self, ruleList, specialNames=None):
        parsedRules = [(ParseSoundChangeRule(ruleLine, specialNames), ruleLine) for ruleLine in ruleList]
        replacerPairs = [(CreateReplacerPair(pscr[1], specialNames),ruleLine) for (pscr,ruleLine) in parsedRules if pscr != None]
        # this needs to be ordered, because order of application matters
        #  if we want to change this to another datastructure, self.Rules
        #  should probably have a list
        self.Rules = [(rp,ruleLine) for (rp,ruleLine) in replacerPairs if rp != None]
    def Apply(self, text):
        results = [text]
        for (rp,ruleLine) in self.Rules:
            results.append(DoReplacement(rp, results[-1]))
        return results

if __name__ == '__main__':
    specialNames={"vowel":["a","e","i","o","u"]} # these vowels just for testing, get full list from ipaParse
    for test in TESTS:
        rule, L = test
        s1, res = ParseSoundChangeRule(rule, specialNames=specialNames)
        if res == None:
            print rule, ": DID NOT PARSE"
            continue
        rp = CreateReplacerPair(res, specialNames=specialNames)
        for entry in L:
            word,expected = entry
            try:
                actual = DoReplacement(rp, word)
                if (actual != expected):
                    print rule, ": expected=", expected, "actual=", actual
                else:
                    print rule, ": SUCCESS"
            except Exception as e:
                if STOP_ON_EXCEPTION:
                    raise
                else:
                    print rule, entry, ": EXCEPTION", e

