# -*- encoding: utf-8 -*-
###
# IPA-based parser
#  Understands multi-codepoint graphemes

import copy
import unicodedata
SHOW_PASSES = False

NASAL = u'm̥mɱn̪n̥nn̠ɳɲ̥ɲŋ̊ŋɴ'
PLOSIVE = u'pbp̪b̪t̪d̪tdʈɖcɟkɡqɢʡʔ'
FRICATIVE = u'ɸβfvθðszʃʒʂʐçʝxɣχʁħʕʜʢhɦ'
APPROXIMANT = u'ʋɹɻjɰʁʕʢhɦ'
TRILL = u'ʙrʀя' # does not include retroflex because of unsupported glyph stuff
FLAP_OR_TAP = u'ⱱ̟ⱱɾɽɢ̆ʡ̯'
LATERAL_FRIC = u'ɬɮɭ˔̊ʎ̥˔ʟ̝̊ʟ̝'
LATERAL_APPROX = u'lɭʎʟ'
LATERAL_FLAP = u'ɺɺ̠ʎ̯'

MANNERS = {"nasal": NASAL,
           "plosive": PLOSIVE,
           "fricative": FRICATIVE,
           "approximant": APPROXIMANT,
           "trill": TRILL,
           "flap_or_tap": FLAP_OR_TAP,
           "lateral_fric": LATERAL_FRIC,
           "lateral_approx": LATERAL_APPROX,
           "lateral_flap": LATERAL_FLAP}

class ParserNode:
    def Recognize(self, s0):
        s1, res = self.Parse(s0)
        return s1, res != None
    def Parsed(self, s0, s1):
        n = copy.copy(self)
        n.Text = s0[:len(s0)-len(s1)]
        return s1, n
    def Parsing(self):
        self.Text = None

class SequenceNode (ParserNode):
    def __init__(self, nodes):
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
    
class OrNode (ParserNode):
    def __init__(self, nodes):
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

def CombiningCategory(c):
    cat = unicodedata.category(c)
    return cat[0] == 'M' or cat == 'Lm' or cat == 'Sk'

def NextGrapheme(s):
    if len(s) == 0: return None
    elif len(s) == 1: return s
    elif CombiningCategory(s[0]):
        raise Exception("Should not have a combining as first codepoint in grapheme")
    else:
        for ii in range(len(s[1:])):
            if not(CombiningCategory(s[1+ii])):
                return s[:ii+1]
        return s

class GraphemeNode (ParserNode):
    def __init__(self, graphemes):
        s = u''.join(graphemes)
        self.Graphemes = []
        while len(s) > 0:
            g = NextGrapheme(s)
            s = s[len(g):]
            self.Graphemes.append(g)
    def __repr__(self):
        return "GraphemeNode(" + str(self.Graphemes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedGrapheme = None
        if len(s0) == 0: return s0, None
        g = NextGrapheme(s0)
        if g in self.Graphemes:
            self.ParsedGrapheme = g
            return self.Parsed(s0, s0[len(g):])
        return s0, None
    def GetParsedResult(self):
        return self.ParsedGrapheme

class WhitespaceNode (ParserNode):
    def __init__(self):
        pass
    def __repr__(self):
        return "WhitespaceNode()"
    def Parse(self, s0):
        self.Parsing()
        for ii in range(len(s0)):
            if not(s0[ii].isspace()):
                if ii > 0:
                    return self.Parsed(s0, s0[ii:])
                else: return s0, None
        return self.Parsed(s0, u'')
    def GetParsedResult(self):
        return self.Text

class OptionalNode (ParserNode):
    def __init__(self, node):
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

class ManyNode (ParserNode):
    def __init__(self, node):
        self.Node = node
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

def DoTests():
    p = GraphemeNode(['a','b'])
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,(("e", False), 'p.Recognize(u"e")')
        ])

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

    p = OrNode([GraphemeNode("a"), GraphemeNode("b")])
    #print p
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,((u"e", False), 'p.Recognize(u"e")')
        ])

    p = WhitespaceNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u" ")')
         ,(("", True), 'p.Recognize(u"  ")')
         ,(("", True), 'p.Recognize(u" \\t  ")')
         ,(("", True), 'p.Recognize(u" \\n  ")')
         ,((u"b", True), 'p.Recognize(u" b")')
         ,((u"b ", False), 'p.Recognize(u"b ")')
        ])

    p = OptionalNode(GraphemeNode("a"))
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a")')
         ,((u"b", True), 'p.Recognize(u"b")')
         ,(u"a", 'str(p.Parse(u"a")[1].GetParsedResult())')
        ])
    
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

    p = GraphemeNode(NASAL)
    expStr = "GraphemeNode([u'm\u0325', u'm', u'\u0271', u'n\u032a', u'n\u0325', u'n', u'n\u0320', u'\u0273', u'\u0272\u0325', u'\u0272', u'\u014b\u030a', u'\u014b', u'\u0274'])"
    RunTests({'p': p},
        [ (expStr, 'str(p)') ])

if __name__ == '__main__':
    DoTests()
