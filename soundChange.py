# -*- encoding: utf-8 -*-
###
# IPA-based sound change
#  Understands multi-codepoint graphemes

from ipaParse import *
WHITESPACE_INCLUDES_NEWLINES = False # turn off newlines as wspace in ipaParse

TESTS = [
    u'b > p /' # b goes to p
# todo to parse this:
# (done) 1. parse into the three parts, A > B / C
#here >>> 2. add ability to name parts

# todo to apply this:
# 1. parse rule
# 2. read word list
# 3. apply rule appropriately


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


    , u'[sz] > t /' #alveolar fricatives
    , u'{alveolar fricative} > t /'

# todo to parse this:
# 1. parse [ ] or terms 
# 2. parse { } ref terms


    , u'{palatal plosive} > {palatal nasal} /'

# todo to parse this:
# 1. find individual sound mappings,
#  s.t. voiced palatal plosive -> voiced palatal nasal
]

def ParseSoundChangeRule(ruleString):
    return SequenceNode([
            OptionalWhitespaceNode()
            , AlphaNode()
            , OptionalWhitespaceNode()
            , GraphemeNode('>')
            , OptionalWhitespaceNode()
            , OptionalNode(AlphaNode())
            , OptionalWhitespaceNode()
            , GraphemeNode('/')
             # not doing conditions currently
            , OptionalWhitespaceNode()
            , EndNode()
        ]).Parse(ruleString)

def ProcessTestResult(result):
    s1, res = result
    if res == None:
        return 'FAIL'
    else:
        return res.GetParsedResult()
results = [ProcessTestResult(ParseSoundChangeRule(test)) for test in TESTS]    
print results

# TODO: Make a compound SeperatedSequenceNode
#  that acts just like a sequence node but has seperators
#  Can use that to make SeperatedSequenceNode(OptionalWhitespaceNode(), seq...)
