# -*- encoding: utf-8 -*-
###
# IPA-based sound change
#  Understands multi-codepoint graphemes

from ipaParse import *
WHITESPACE_INCLUDES_NEWLINES = False # turn off newlines as wspace in ipaParse

TESTS = [
#################################################
    u'b > p /' # b goes to p
# todo to parse this:
# (done) 1. parse into the three parts, A > B / C
# (done) 2. add ability to name parts

# todo to apply this:
# (done) 1. Build parser from rule
# >>> here >>> 2. read word list
# 3. apply rule appropriately


#################################################
    , u's > /_#' # word-final s removed

# todo to parse this:
# 1. parse into the three parts, A > B / C
# 2. parse condition
#   a. parse word boundaries #
#   b. parse position indicator _

# todo to apply this:
# 1. parse rule
# 2. read word list
# 3. apply rule appropriately


#################################################
    , u'[sz] > t /' #alveolar fricatives
    , u'{alveolar fricative} > t /'

# todo to parse this:
# 1. parse [ ] or terms 
# 2. parse { } ref terms


#################################################
    , u'{palatal plosive} > {palatal nasal} /'

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

def ProcessTestResult(result):
    s1, res = result
    if res == None:
        return 'FAIL'
    else:
        rp = CreateReplacerPair(res)
        return DoReplacement(rp, u"a b c d")

results = [ProcessTestResult(ParseSoundChangeRule(test)) for test in TESTS]    
print results

