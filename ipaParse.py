# -*- encoding: utf-8 -*-
###
# IPA-based parser
#  Understands multi-codepoint graphemes

import copy
import unicodedata

## Config
WHITESPACE_INCLUDES_NEWLINES = True

## Debug and Test Config
SHOW_PASSES = False

MANNER = {"nasal": u'm̥mɱn̪n̥nn̠ɳɲ̥ɲŋ̊ŋɴ',
           "plosive": u'pbp̪b̪t̪d̪tdʈɖcɟkɡgqɢʡʔ',
           "fricative": u'ɸβfvθðszʃʒʂʐçʝxɣχʁħʕʜʢhɦ',
           "approximant": u'ʋɹɻjɰʁʕʢhɦw',
           "trill": u'ʙrʀя', # does not include retroflex because of unsupported glyph stuff,
           "flap_or_tap": u'ⱱ̟ⱱɾɽɢ̆ʡ̯',
           "lateral_fric": u'ɬɮɭ˔̊ʎ̥˔ʟ̝̊ʟ̝',
           "lateral_approx": u'lɭʎʟ',
           "lateral_flap": u'ɺɺ̠ʎ̯'
}

PLACE = {
    "labial": {
        "bilabial": u'm̥pɸmbβⱱ̟',
        "labiodental": u'p̪fɱb̪vʋⱱ'
    },
    "labio-velar": {
        "laboio-velar": u'w'
    },
    "coronal": {
        "dental": u'n̪t̪d̪θð',
        "alveolar": u'n̥ntdszɹrɾɬɮlɺ',
        "postlav": u'n̠ʃʒ',
        "retroflex": u'ɳʈɖʂʐɻɽɭ˔̊ɭɺ̠'
    },
    "dorsal": {
        "palatal": u'ɲ̥ɲcɟçʝjʎ̥˔ʎʎ̯',
        "velar": u'ŋ̊ŋkɡgxɣɰʟ̝̊ʟ̝ʟ',
        "uvular": u'ɴqɢχʁʀɢ̆'
    },
    "radical": {
        "pharyngeal": u'ħʕ',
        "epiglottal": u'ʡʜʢяʡ̯'
    },
    "glottal": {
        "glottal": u'ʔhɦ'
    }
}

PLACE_MINOR = {}
PLACE_MAJOR = {}
for major in PLACE.keys():
    PLACE_MAJOR[major] = u''
    for minor in PLACE[major].keys():
        s = PLACE[major][minor]
        PLACE_MINOR[minor] = s
        PLACE_MAJOR[major] += s

VOICING = {
    "unvoiced": u'm̥pɸp̪ft̪θn̥tsɬʃʈʂɭ˔̊ɲ̥cçʎ̥˔ŋ̊kxʟ̝̊qχħʡʜʔh',
    "voiced": u'mbβʙⱱ̟ɱb̪vʋⱱn̪d̪ðndzɹrɾɮlɺn̠ʒɳɖʐɻɽɭɺ̠ɲɟʝjʎʎ̯ŋɡgɣɰʟ̝ʟɴɢʁʀɢ̆ʕʢяʡ̯ɦw'
}



BACKNESS = {
    'front': u'iyeøe̞ø̞ɛœæaɶ',
    'near-front': u'ɪʏ',
    'central': u'ɨʉɪ̈ʊ̈ɘɵəɜɞɐä',
    'near-back': u'ʊ',
    'back': u'ɯuɤoɤ̞o̞ʌɔɑɒ'
}

HEIGHT = {
    'high/close': u'iyɨʉɯu',
    'near-close': u'ɪʏɪ̈ʊ̈ʊ',
    'close-mid': u'eøɘɵɤo',
    'mid': u'e̞ø̞əɤ̞o̞',
    'open-mid': u'ɛœɜɞʌɔ',
    'near-open': u'æɐ',		
    'low/open': u'aɶäɑɒ'
}

ROUNDEDNESS = {
    'unrounded': u'iɨɯɪɪ̈eɘɤe̞əɤ̞ɛɜʌæɐaäɑ',
    'rounded': u'yʉuʏʊ̈ʊøɵoø̞o̞œɞɔɐɶɒ'
}


def CombiningCategory(c):
    cat = unicodedata.category(c)
    return cat[0] == 'M' or cat == 'Lm' or cat == 'Sk'

def PopGrapheme(s):
    if len(s) == 0: return None, s
    elif len(s) == 1: return s, ''
    elif CombiningCategory(s[0]):
        print s
        raise Exception("Should not have a combining as first codepoint in grapheme")
    else:
        for ii in range(len(s[1:])):
            if not(CombiningCategory(s[1+ii])):
                return s[:ii+1], s[ii+1:]
        return s, ''

def GraphemeSplit(s, errorsTo=None):
    graphemeL = []
    while len(s) > 0:
        try:
            g, s = PopGrapheme(s)
        except:
            if errorsTo != None:
                errorsTo.add(s)
                return []
            else:
                raise
        if g == None: break
        graphemeL.append(g)
    return graphemeL

ALL_CONSONANTS = GraphemeSplit(VOICING['unvoiced'] + VOICING['voiced'])
ALL_VOWELS = GraphemeSplit(ROUNDEDNESS['unrounded'] + ROUNDEDNESS['rounded'])
ALL_ALPHA = ALL_CONSONANTS + ALL_VOWELS

ConsonantData = {}
for c in ALL_CONSONANTS:
    ConsonantData[c] = {}
VowelData = {}
for c in ALL_VOWELS:
    VowelData[c] = {}

def FillData(byGrapheme, byType, typeType):
    for t in byType.keys():
        graphemeL = GraphemeSplit(byType[t])
        for grapheme in graphemeL:
            byGrapheme[grapheme][typeType] = t

FillData(ConsonantData, MANNER, 'manner')
FillData(ConsonantData, PLACE_MAJOR, 'place_major')
FillData(ConsonantData, PLACE_MINOR, 'place_minor')
FillData(ConsonantData, VOICING, 'voicing')

FillData(VowelData, BACKNESS, 'backness')
FillData(VowelData, HEIGHT, 'height')
FillData(VowelData, ROUNDEDNESS, 'roundedness')

class ParserNode:
    def __init__(self, name=None):
        self.Name = name
    def Recognize(self, s0):
        s1, res = self.Parse(s0)
        return s1, res != None
    def Parsed(self, s0, s1):
        n = copy.copy(self)
        n.Text = s0[:len(s0)-len(s1)]
        return s1, n
    def Parsing(self):
        self.Text = None
    def FindAll(self, name):
        if self.Name == name and self.Text != None: return [self]
        else: return []
    def ReplaceWith(self, d):
        if self.Name in d.keys():
            return d[self.Name]
        else:
            return self.Text

def WeaveAndClean(l1, l2):
    result = []
    for ii in range(len(l1)):
        result.append(l1[ii])
        if len(l2) > ii: result.append(l2[ii])
    return [r for r in result if r != None]

class SeparatedSequenceNode (ParserNode):
    def __init__(self, separatorNode, sequenceNodes, initialSep=False, finalSep=False, storeSep=True, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in sequenceNodes]
        self.SepNode = separatorNode
        self.InitialSep = initialSep
        self.FinalSep = finalSep
        self.StoreSep = storeSep
    def __repr__(self):
        initial = ""
        final = ""
        store = ""
        if self.InitialSep: initial = ", initialSep=True"
        if self.FinalSep: final = ", finalSep=True"
        if not(self.StoreSep): store = ", storeSep=False"
        return "SeparatedSequenceNode(" + str(self.SepNode) + ", " + str(self.Nodes) + initial + final + store + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        self.Separators = []
        s1 = s0
        if self.InitialSep:
            s1, res = self.SepNode.Parse(s1)
            if res == None: return s0, None
            self.Separators.append(res)
        for ii in range(len(self.Nodes)):
            node = self.Nodes[ii]
            s1,res = node.Parse(s1)
            if res == None:
                return s0, None
            self.ParsedNodes.append(res)
            if self.FinalSep or (ii != len(self.Nodes) - 1):
                s1,res = self.SepNode.Parse(s1)
                if res == None:
                    return s0, None
                if self.StoreSep: self.Separators.append(res)
        return self.Parsed(s0, s1)
    def __WeaveAndClean(self, nodes, sep):
        if not(self.StoreSep):
            return [node for node in nodes if node != None]
        elif self.InitialSep:
            return WeaveAndClean(sep, nodes)
        else:
            return WeaveAndClean(nodes, sep)
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            nodes = [n.GetParsedResult() for n in self.ParsedNodes]
            if not(self.StoreSep): return nodes
            sep = [n.GetParsedResult() for n in self.Separators]
            return self.__WeaveAndClean(nodes, sep)
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.__WeaveAndClean(self.ParsedNodes, self.Separators):
            results.extend(node.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if len(self.ParsedNodes) == 0:
            return None
        if self.Name in d.keys():
            return d[self.Name]
        else:
            nodes = [n.ReplaceWith(d) for n in self.ParsedNodes]
            if not(self.StoreSep): return ''.join(nodes)
            sep = [n.ReplaceWith(d) for n in self.Separators]
            return ''.join(self.__WeaveAndClean(nodes, sep))

class SequenceNode (ParserNode):
    def __init__(self, nodes, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in nodes]
    def __repr__(self):
        return "SequenceNode(" + str(self.Nodes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        s1 = s0
        for node in self.Nodes:
            s1,res = node.Parse(s1)
            if res == None: return s0, None
            self.ParsedNodes.append(res)
        return self.Parsed(s0, s1)
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            return [x for x in [n.GetParsedResult() for n in self.ParsedNodes] if x != None]
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.ParsedNodes:
            results.extend(node.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if len(self.ParsedNodes) == 0:
            return None
        elif self.Name in d.keys():
            return d[self.Name]
        else:
            replaced = [n.ReplaceWith(d) for n in self.ParsedNodes]
            return ''.join([r for r in replaced if r != None])
    
class OrNode (ParserNode):
    def __init__(self, nodes, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in nodes]
    def __repr__(self):
        return "OrNode(" + str(self.Nodes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNode = None
        for node in self.Nodes:
            s1,res = node.Parse(s0)
            if res != None:
                self.ParsedNode = res
                return self.Parsed(s0, s1)
        return s0, None
    def GetParsedResult(self):
        return self.ParsedNode.GetParsedResult()
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        results.extend(self.ParsedNode.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if self.ParsedNode == None:
            return None
        elif self.Name in d.keys():
            return d[self.Name]
        else:
            return self.ParsedNode.ReplaceWith(d)

class GraphemeNode (ParserNode):
    def __init__(self, graphemes, name=None):
        ParserNode.__init__(self, name)
        s = u''.join(graphemes)
        self.Graphemes = []
        while len(s) > 0:
            g, s = PopGrapheme(s)
            self.Graphemes.append(g)
    def __repr__(self):
        if self.Name != None: nameStr = ", name='" + self.Name + "'"
        else: nameStr = ""
        return "GraphemeNode(" + str(self.Graphemes) + nameStr + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedGrapheme = None
        if len(s0) == 0: return s0, None
        g, s1 = PopGrapheme(s0)
        if g in self.Graphemes:
            self.ParsedGrapheme = g
            return self.Parsed(s0, s1)
        return s0, None
    def GetParsedResult(self):
        return self.ParsedGrapheme

class WhitespaceNode (ParserNode):
    def __init__(self, name=None):
        ParserNode.__init__(self, name)
    def __repr__(self):
        return "WhitespaceNode()"
    def Parse(self, s0):
        self.Parsing()
        if (len(s0) == 0): return s0, None
        for ii in range(len(s0)):
            if (not(s0[ii].isspace())
                or (not(WHITESPACE_INCLUDES_NEWLINES)
                    and (s0[ii] == '\n' or s0[ii] == '\r')
                )):
                if ii > 0:
                    return self.Parsed(s0, s0[ii:])
                else: return s0, None
        return self.Parsed(s0, u'')
    def GetParsedResult(self):
        return self.Text

class OptionalNode (ParserNode):
    def __init__(self, node, name=None):
        ParserNode.__init__(self, name)
        self.Node = node
    def __repr__(self):
        return "OptionalNode(" + str(self.Node) + ")"
    def Parse(self, s0):
        self.Parsing()
        s1, res = self.Node.Parse(s0)
        self.Chosen = res
        return self.Parsed(s0, s1)
    def GetParsedResult(self):
        if self.Chosen == None: return None
        else: return self.Chosen.GetParsedResult()
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        if self.Chosen != None:
            results.extend(self.Chosen.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if self.Chosen == None:
            return None
        elif self.Name in d.keys():
            return d[self.Name]
        else:
            return self.Chosen.ReplaceWith(d)

class ManyNode (ParserNode):
    def __init__(self, node, name=None):
        if not(isinstance(node, ParserNode)): raise Exception("ManyNode expects a node: " + str(node))
        ParserNode.__init__(self, name)
        self.Node = node
        self.ParsedNodes = []
    def __repr__(self):
        return "ManyNode(" + str(self.Node) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        s1 = s0
        if len(s0) == 0:
            s1, res = self.Node.Parse(u'')
            if (res == None):
                return s0, None
            else:
                self.ParsedNodes.append(res)
        while len(s1) > 0:
            pending,res = self.Node.Parse(s1)
            if res == None or (pending == s1 and len(self.ParsedNodes) > 0):
                break
            self.ParsedNodes.append(res)
            s1 = pending
        if len(self.ParsedNodes) > 0:
            return self.Parsed(s0, s1)
        else:
            return s0, None
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            return [n.GetParsedResult() for n in self.ParsedNodes]
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.ParsedNodes:
            results.extend(node.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if len(self.ParsedNodes) == 0:
            return None
        elif self.Name in d.keys():
            return d[self.Name]
        else:
            return ''.join([n.ReplaceWith(d) for n in self.ParsedNodes])

# =================================================
# ============ Composite Helper Nodes =============
# =================================================
class OptionalWhitespaceNode (OptionalNode):
    def __init__(self, name=None):
        OptionalNode.__init__(self, WhitespaceNode(), name)
    def __repr__(self):
        return "OptionalWhitespaceNode()"

class AlphaNode(GraphemeNode):
    def __init__(self, name=None):
        GraphemeNode.__init__(self, ALL_ALPHA, name)
    def __repr__(self):
        return "AlphaNode()"

## Python automatically converts CrLf EOL when reading files as
##   text so this isn't needed. Add it back in if data might come
##   in from other means, like binary data converted or something
##class EOLNode(OrNode):
##    def __init__(self, name=None):
##        OrNode.__init__(self, [
##            GraphemeNode(u'\n')
##            , GraphemeNode(u'\r')
##            , SequenceNode(GraphemeNode(u'\n'), GraphemeNode(u'\r'))]
##            , name)
class EOLNode(GraphemeNode):
    def __init__(self, name=None):
        GraphemeNode.__init__(self, u'\n', name)
    def __repr__(self):
        return "EOLNode()"

class EndNode (ParserNode):
    def __init__(self, name=None):
        ParserNode.__init__(self, name)
        self.WhitespaceAndEOL = OptionalNode(ManyNode(OrNode([WhitespaceNode(), EOLNode()])))
    def __repr__(self):
        return "EndNode()"
    def Parse(self, s0):
        self.Parsing()
        s1, res = self.WhitespaceAndEOL.Parse(s0)
        if res != None and s1 == '':
            return self.Parsed(s0, s1)
        else:
            return s0, None
    def GetParsedResult(self):
        return self.Text

class MustBeNamedException(Exception): pass

class SelectNameOneOfOrNoneNode(OptionalNode):
    def __init__(self, namedOptionNodes, name=None):
        L = [n for n in namedOptionNodes if n.Name != None]
        if len(L) != len(namedOptionNodes): raise MustBeNamedException()
        OptionalNode.__init__(self, OrNode(L), name)
    def __repr__(self):
        return "SelectNameOneOfOrNoneNode(" + str(self.Node.Nodes) + ")"
    def GetSelectionName(self):
        """Call this method directly (it isn't recursive) to determine what, if anything, was selected"""
        if self.Text != None and self.Text != "":
            return self.Node.ParsedNode.Name
        else:
            return None

class HashNode(GraphemeNode):
    def __init__(self):
        GraphemeNode.__init__(self, u"#")
    def __repr__(self):
        return "HashNode()"

class UnderscoreNode(GraphemeNode):
    def __init__(self):
        GraphemeNode.__init__(self, u"_")
    def __repr__(self):
        return "UnderscoreNode()"

class ManyEndsWithSubsetNode(ParserNode):
    """e.g. Seq(Many(Alpha), Grapheme(a))... needed because no backtracking normally."""
    def __init__(self, manyOfNode, endsWithNode, backtrackStepSize, name=None):
        ParserNode.__init__(self, name)
        self.Many = ManyNode(manyOfNode)
        self.EndsWith = endsWithNode
        self.BacktrackStepSize = backtrackStepSize
    def __repr__(self):
        vals = [self.Many.Node, self.EndsWith, self.BacktrackStepSize]
        s = ",".join([str(val) for val in vals])
        return "ManyEndsWithSubsetNode(" + s + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedMany = None
        self.ParsedEndsWith = None
        s1, res = self.Many.Parse(s0)
        if res == None: return s0, None
        L = GraphemeSplit(res.Text)
        for backtrack in range(self.BacktrackStepSize, len(L), self.BacktrackStepSize):
            s1a, resa = self.Many.Parse(''.join(L[0:-backtrack]))
            if resa == None: return s0, None
            s1b, resb = self.EndsWith.Parse(''.join(L[-backtrack:]))
            if resb != None:
                self.ParsedMany = resa
                self.ParsedEndsWith = resb
                return self.Parsed(s0, s1b+s1)
        return s0, None
    def GetParsedResult(self):
        if self.ParsedMany == None:
            return None
        else:
            return self.ParsedMany.GetParsedResult() + [self.ParsedEndsWith.GetParsedResult()]
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        results.extend(self.ParsedMany.FindAll(name))
        results.extend(self.ParsedEndsWith.FindAll(name))
        return results
    def ReplaceWith(self, d):
        if self.ParsedMany == None:
            return None
        elif self.Name in d.keys():
            return d[self.Name]
        else:
            return self.ParsedMany.ReplaceWith(d) + self.ParsedEndsWith.ReplaceWith(d)

class GroupNode(SequenceNode):
    def __init__(self, leftGrouperNode, groupedNodes, rightGrouperNode, name=None):
        SequenceNode.__init__(self, [leftGrouperNode, groupedNodes, rightGrouperNode], name)
    def __repr__(self):
        s = ",".join([str(val) for val in self.Nodes])
        return "GroupNode(" + s + ")"

# =================================================
# ================== Testing ======================
# =================================================
    
def MakeTest(env):
    def Test(esPair):
        expect,statement = esPair
        result = eval(statement,env)
        if expect == result:
            if SHOW_PASSES: print "PASS:", statement, " == ", expect
            return True
        else:
            print "FAIL: " + statement
            print "===> expected:", expect
            print "===> actual:", result
            return False
    return Test

def RunTests(env, esPairs):
    return all(map(MakeTest(env), esPairs))

def CheckRepr(node):
    """without loading the node classes into the eval env in MakeTest, we have to do this test seperately"""
    if str(node) == str(eval(str(node))):
        if SHOW_PASSES: print "PASS: str for", str(node)
    else:
        print "FAIL: str for", str(node)

def DoTests():
    p = GraphemeNode(['a','b'])
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,(("e", False), 'p.Recognize(u"e")')
        ])
    CheckRepr(p)

    p = GraphemeNode(u"m̥ɱn̪n̥ŋ̊ɴ")
    RunTests({'p': p}, 
        [ (("", True), u'p.Recognize(u"m̥")')
         ,(("", True), u'p.Recognize(u"ɱ")')
         ,(("", True), u'p.Recognize(u"n̪")')
         ,(("", True), u'p.Recognize(u"n̥")')
         ,(("", True), u'p.Recognize(u"ŋ̊")')
         ,(("", True), u'p.Recognize(u"ɴ")')
         ,((u"̪", False), u'p.Recognize(u"̪")')
         ,((u"̥", False), u'p.Recognize(u"̥")')
         ,((u"̊", False), u'p.Recognize(u"̊")')
         ,(("e", False), u'p.Recognize(u"e")')
        ])
    CheckRepr(p)

    p = OrNode([GraphemeNode("a"), GraphemeNode("b")])
    #print p
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,((u"e", False), 'p.Recognize(u"e")')
        ])
    CheckRepr(p)

    p = WhitespaceNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u" ")')
         ,(("", True), 'p.Recognize(u"  ")')
         ,(("", True), 'p.Recognize(u" \\t  ")')
         ,((u"b", True), 'p.Recognize(u" b")')
         ,((u"b", False), 'p.Recognize(u"b")') # whitespace is not optional
         ,((u"", False), 'p.Recognize(u"")') # whitespace is not optional
        ])
    RunTests({'p': p, 'WHITESPACE_INCLUDES_NEWLINES': True},[(("", True), 'p.Recognize(u" \\n  ")')])
    CheckRepr(p)
    global WHITESPACE_INCLUDES_NEWLINES
    temp = WHITESPACE_INCLUDES_NEWLINES
    WHITESPACE_INCLUDES_NEWLINES = False
    RunTests({'p': p, 'WHITESPACE_INCLUDES_NEWLINES': False},[(("\n  ", True), 'p.Recognize(u" \\n  ")')])
    CheckRepr(p)
    WHITESPACE_INCLUDES_NEWLINES = temp

    p = EOLNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"\\n")')
         ,((" ", True), 'p.Recognize(u"\\n ")')
         ,((" \n", False), 'p.Recognize(u" \\n")')
        ])
    CheckRepr(p)

    p = EndNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"")')
         ,(("", True), 'p.Recognize(u"\\n")')
         ,(("", True), 'p.Recognize(u"\\n ")')
         ,(("", True), 'p.Recognize(u" \\n")')
         ,((" \na", False), 'p.Recognize(u" \\na")')
        ])
    CheckRepr(p)

    p = OptionalWhitespaceNode()
    # print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"")')
         ,(("", True), 'p.Recognize(u" ")')
         ,(("b ", True), 'p.Recognize(u"b ")')
         ,(("b ", True), 'p.Recognize(u" b ")')
        ])
    CheckRepr(p)

    p = OptionalNode(GraphemeNode("a"))
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a")')
         ,((u"b", True), 'p.Recognize(u"b")')
         ,(u"a", 'str(p.Parse(u"a")[1].GetParsedResult())')
        ])
    CheckRepr(p)
    
    p = SequenceNode([
        OrNode([
            GraphemeNode("ab"),
            WhitespaceNode()
        ]),
        OptionalNode(WhitespaceNode()),
        GraphemeNode("cd")
    ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a c")')
         ,(("", True), 'p.Recognize(u" d")')
         ,(("e", True), 'p.Recognize(u" de")')
         ,(("de", False), 'p.Recognize(u"de")')
         ,(("e", False), 'p.Recognize(u"e")')
         ,("[u'a', u'c']", 'str(p.Parse(u"ac")[1].GetParsedResult())')
        ])
    CheckRepr(p)

    p = SequenceNode([
            ManyNode(GraphemeNode("a"))
            , GraphemeNode(["b"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"aab")')
         ,(("", True), 'p.Recognize(u"aaab")')
         ,(("b", False), 'p.Recognize(u"b")')
         ,(("a", False), 'p.Recognize(u"a")')
        ])
    CheckRepr(p)

    p = SeparatedSequenceNode(
            OptionalNode(WhitespaceNode()),
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"a b")')
         ,(("", True), 'p.Recognize(u"a  b")')
         ,((" ", True), 'p.Recognize(u"ab ")') # no sep picked up at end
         ,((" ab", False), 'p.Recognize(u" ab")') # no sep picked up at beginning
        ])
    CheckRepr(p)

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test above)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , initialSep = True)
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("a b ", False), 'p.Recognize(u"a b ")')
         ,(("", True), 'p.Recognize(u" a b")')
         ,(("", True), 'p.Recognize(u" a b")')
         ,((" ", True), 'p.Recognize(u" a b ")')
        ])
    CheckRepr(p)

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test earlier)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , finalSep = True)
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("", True), 'p.Recognize(u"a b ")')
         ,((" a b", False), 'p.Recognize(u" a b")')
         ,((" a b ", False), 'p.Recognize(u" a b ")')
         ,(("a", True), 'p.Recognize(u"a b a")')
        ])
    CheckRepr(p)

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test earlier)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , finalSep = True
            , storeSep = False
        )
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("", True), 'p.Recognize(u"a b ")')
         ,((" a b", False), 'p.Recognize(u" a b")')
         ,((" a b ", False), 'p.Recognize(u" a b ")')
         ,(("a", True), 'p.Recognize(u"a b a")')
        ])
    CheckRepr(p)

    p = SequenceNode([
            OptionalNode(ManyNode(GraphemeNode("e")))
            , GraphemeNode(["f"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ef")')
         ,(("", True), 'p.Recognize(u"eef")')
         ,(("", True), 'p.Recognize(u"eeef")')
         ,(("", True), 'p.Recognize(u"f")')
         ,(("e", False), 'p.Recognize(u"e")')
         ,("[[u'e', u'e'], u'f']", 'str(p.Parse(u"eef")[1].GetParsedResult())')
        ])
    CheckRepr(p)

    p = SequenceNode([
            ManyNode(OptionalNode(GraphemeNode("a")))
            , GraphemeNode(["b"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"aab")')
         ,(("", True), 'p.Recognize(u"aaab")')
         ,(("", True), 'p.Recognize(u"b")')
         ,(("a", False), 'p.Recognize(u"a")')
         ,("[[u'a', u'a'], u'b']", 'str(p.Parse(u"aab")[1].GetParsedResult())')
        ])
    CheckRepr(p)

    p = GraphemeNode(MANNER["nasal"])
    expStr = "GraphemeNode([u'm\u0325', u'm', u'\u0271', u'n\u032a', u'n\u0325', u'n', u'n\u0320', u'\u0273', u'\u0272\u0325', u'\u0272', u'\u014b\u030a', u'\u014b', u'\u0274'])"
    RunTests({'p': p},
        [ (expStr, 'str(p)') ])
    CheckRepr(p)

    p = AlphaNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,((" ", False), 'p.Recognize(u" ")')
         ,(("[", False), 'p.Recognize(u"[")')
        ])
    CheckRepr(p)

    p = SequenceNode([
            ManyNode(OptionalNode(GraphemeNode("a", name="grapheme"), name="optional"), name="many")
            , GraphemeNode(["b"], name="grapheme")
            ]
        , name = "seq")
    #print p
    RunTests({'p': p},
        [ (u'b', 'p.Parse(u"ab")[1].FindAll("seq")[0].FindAll("grapheme")[1].Text')
        ])
    CheckRepr(p)

    p = SeparatedSequenceNode(OptionalWhitespaceNode(), [
            ManyNode(OptionalNode(GraphemeNode("a", name="grapheme"), name="optional"), name="many")
            , GraphemeNode(["b"], name="grapheme")
            ]
        , name = "seq", storeSep = False, initialSep = True, finalSep = True)
    #print p
    RunTests({'p': p},
        [ (u'b', 'p.Parse(u" a b ")[1].FindAll("seq")[0].FindAll("grapheme")[1].Text')
        ])
    CheckRepr(p)

    p = SequenceNode(name="seq", nodes=[
            SeparatedSequenceNode(WhitespaceNode(name="ws"), name="sepseq", sequenceNodes=[
                GraphemeNode(["a"], name="a")
                , GraphemeNode(["b"], name="b")
            ])
            , GraphemeNode(["c"], name="c")
            , OrNode(name="d", nodes=[
                    GraphemeNode("e", name="e")
                    , GraphemeNode("f", name="f")
                ])
        ])
    #print p
    s1,res = p.Parse(u"a bcf")
    RunTests({'res': res},
        [
              (u'* bcf', 'res.ReplaceWith({"a": "*"})')
            , (u'a*bcf', 'res.ReplaceWith({"ws": "*"})')
            , (u'a *cf', 'res.ReplaceWith({"b": "*"})')
            , (u'a b*f', 'res.ReplaceWith({"c": "*"})')
            , (u'a bc*', 'res.ReplaceWith({"d": "*"})')
            , (u'a bcf', 'res.ReplaceWith({"e": "*"})')
            , (u'a bc*', 'res.ReplaceWith({"f": "*"})')
            , (u'*cf', 'res.ReplaceWith({"sepseq": "*"})')
            , (u'*', 'res.ReplaceWith({"seq": "*"})')
            , (u'a *!f', 'res.ReplaceWith({"b": "*","c":"!"})')
        ])
    CheckRepr(p)

    p = SelectNameOneOfOrNoneNode([GraphemeNode("a", name="a"), GraphemeNode("b", name="b")])
    #print p
    RunTests({'p': p},
        [ (u"a", 'p.Parse(u"a")[1].GetSelectionName()')
         ,(u"b", 'p.Parse(u"b")[1].GetSelectionName()')
         ,(None, 'p.Parse(u"c")[1].GetSelectionName()')
        ])
    CheckRepr(p)

    p = UnderscoreNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"_")')
         ,(("b", True), 'p.Recognize(u"_b")')
         ,((" ", False), 'p.Recognize(u" ")')
         ,((" _", False), 'p.Recognize(u" _")')
        ])
    CheckRepr(p)

    p = HashNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"#")')
         ,(("b", True), 'p.Recognize(u"#b")')
         ,((" ", False), 'p.Recognize(u" ")')
         ,((" #", False), 'p.Recognize(u" #")')
        ])
    CheckRepr(p)

    p = ManyEndsWithSubsetNode(AlphaNode(), GraphemeNode("a"), 1)
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"aaaa")')
         ,(("bbb", True), 'p.Recognize(u"aaaabbb")')
         ,(("", True), 'p.Recognize(u"abababa")')
         ,(("a", False), 'p.Recognize(u"a")')
         ,(("bbb", False), 'p.Recognize(u"bbb")')
        ])
    CheckRepr(p)

    p = GroupNode(GraphemeNode('['), ManyNode(AlphaNode()), GraphemeNode(']'))
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"[a]")')
         ,(("", True), 'p.Recognize(u"[ab]")')
         ,(("b", True), 'p.Recognize(u"[b]b")')
         ,(("b[b]b", False), 'p.Recognize(u"b[b]b")')
         ,(("[ b]b", False), 'p.Recognize(u"[ b]b")')
        ])
    CheckRepr(p)

    p = SequenceNode([GroupNode(GraphemeNode('{'),ManyNode(AlphaNode(), name="name"),GraphemeNode('}')), UnderscoreNode()])
    #print p
    RunTests({'p': p},
        [ (("{vowel}", False), 'p.Recognize(u"{vowel}")')
         ,(("", True), 'p.Recognize(u"{vowel}_")')
         ,(u"vowel", 'p.Parse(u"{vowel}_")[1].FindAll("name")[0].Text')
        ])
    CheckRepr(p)

if __name__ == '__main__':
    DoTests()
