# -*- encoding: utf-8 -*-
###
## Classes to contain and maintain data about language families and the languages therein
DICTIONARY_FILE_EXT = ".dictionary"
ALPHABET_FILE_EXT = ".alphabet"

import ipaParse
import codecs
def ParseDictionaryFile(fileName):
    f = codecs.open(fileName, encoding="utf-8")
    splitlines = [[l.strip() for l in line.split("\t")] for line in f.readlines()]
    d = {}
    for line in splitlines:
        if not(d.has_key(line[0])): d[line[0]] = []
        d[line[0]].append(line[1:])
    return d
def ParseAlphabetFile(fileName):
    lines = [line.strip() for line in codecs.open(fileName, encoding="utf-8").readlines()]
    return [line for line in lines if line != ""]
def DumpAlphabetToFile(alphabet, fileName):
    f = codecs.open(fileName, "w", encoding="utf-8")
    f.writelines([l+"\n" for l in alphabet])

class Language:
    def __init__(self, name, vocabulary, alphabet=None, suspectWords=None):
        self.Name = name
        self.Vocabulary = vocabulary
        self.Graphemes = list(alphabet) if alphabet != None else list()
        self.SuspectWords = set(suspectWords) if suspectWords != None else set()
    def __repr__(self):
        alphabet = ", " + str(len(self.Graphemes)) + " graphemes" if len(self.Graphemes) > 0 else ""
        return self.Name + " (" + str(len(self.Vocabulary.keys())) + " words" + alphabet + ")"
    def FamilyTree(self, indentStr, indentAmount):
        return indentStr*indentAmount + str(self) + "\n"
    def ExtractAlphabet(self):
        graphemes = set()
        for word in self.Vocabulary:
            [graphemes.add(g) for g in ipaParse.GraphemeSplit(word, errorsTo=self.SuspectWords)]
        self.Graphemes = list(graphemes)
        return self.Graphemes
    def SetAlphabet(self, alphabet):
        self.Graphemes = list(alphabet)

class LanguageFamily:
    def __init__(self, name):
        self.SubFamilies = []
        self.Languages = {}
        self.Name = name
    def __repr__(self):
        return self.Name + " (" + str(len(self.AllChildLanguages().keys())) + " languages)"
    def LoadFromPath(self, path):
        import os
        unboundAlphabets = {}
        for entry in os.listdir(path):
            fullPath = os.path.join(path, entry)
            if os.path.isdir(fullPath):
                family = LanguageFamily(entry)
                family.LoadFromPath(fullPath)
                self.SubFamilies.append(family)
            elif entry.lower().endswith(DICTIONARY_FILE_EXT):
                langName = entry[0:-len(DICTIONARY_FILE_EXT)]
                self.Languages[langName] = Language(
                    langName,
                    ParseDictionaryFile(fullPath),
                    alphabet = (unboundAlphabets[langName] if langName in unboundAlphabets else None)
                )
            elif entry.lower().endswith(ALPHABET_FILE_EXT):
                langName = entry[0:-len(ALPHABET_FILE_EXT)]
                alphabet = ParseAlphabetFile(fullPath)
                if langName in self.Languages:
                    self.Languages[langName].SetAlphabet(alphabet)
                else:
                    unboundAlphabets[langName] = alphabet
    def AllChildLanguages(self):
        result = dict(self.Languages)
        for family in self.SubFamilies:
            result = dict(result.items() + family.AllChildLanguages().items())            
        return result
    def FamilyTree(self, indentStr, indentAmount):
        return (indentStr*indentAmount + str(self) + "\n"
            + "".join([l.FamilyTree(indentStr, indentAmount+1) for l in self.Languages.values()])
            + "".join([f.FamilyTree(indentStr, indentAmount+1) for f in self.SubFamilies]))
