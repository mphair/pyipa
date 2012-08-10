# -*- encoding: utf-8 -*-
###
## Classes to contain and maintain data about language families and the languages therein
DICTIONARY_FILE_EXT = ".dictionary"
ALPHABET_FILE_EXT = ".alphabet"
CORPUS_FILE_EXT = ".corpus"

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
def SaveDictionaryToFile(d, fileName):
    f = codecs.open(fileName, "w", encoding="utf-8")
    for word in d.keys():
        for definition in d[word]:
            f.write('\t'.join([word]+definition)+"\n")

def ParseAlphabetFile(fileName):
    lines = [line.strip() for line in codecs.open(fileName, encoding="utf-8").readlines()]
    return [line for line in lines if line != ""]
def DumpAlphabetToFile(alphabet, fileName):
    f = codecs.open(fileName, "w", encoding="utf-8")
    f.writelines([l+"\n" for l in alphabet])

def ParseCorpusFile(fileName):
    return [[chunk.strip() for chunk in line.strip().split("=")] for line in codecs.open(fileName, encoding="utf-8").readlines()]
def DumpCorpusToFile(corpus, fileName):
    f = codecs.open(fileName, "w", encoding="utf-8")
    f.writelines([" = ".join(lineChunks)+"\n" for lineChunks in corpus])

def AddToAlphabetIfNeeded(existingAlphabet, extractedAlphabet):
    a_set = set(existingAlphabet)
    result = list(existingAlphabet)
    for g in extractedAlphabet:
        if not(g in a_set):
            a_set.add(g)
            result.append(g)
    return result

def ExtractAlphabet(vocab, corpus):
    graphemes = set()
    suspectWords = set()
    for word in vocab:
        [graphemes.add(g) for g in ipaParse.GraphemeSplit(word, errorsTo=suspectWords) if g in ipaParse.ALL_ALPHA]
    for line in corpus:
        [graphemes.add(g) for g in ipaParse.GraphemeSplit(line[0], errorsTo=suspectWords) if g in ipaParse.ALL_ALPHA]
    return (list(graphemes), suspectWords)

class Language:
    def __init__(self, name, vocabulary, alphabet=None, suspectWords=None, corpus=None):
        if not(isinstance(vocabulary, dict)): raise Exception("Language expects a dict for vocabulary, got a: " + str(type(vocabulary)))
        self.Name = name
        self.Vocabulary = vocabulary
        self.Graphemes = list(alphabet) if alphabet != None else list()
        self.SuspectWords = set(suspectWords) if suspectWords != None else set()
        self.Corpus = list(corpus) if corpus != None else list()
    def __repr__(self):
        alphabet = ", " + str(len(self.Graphemes)) + " graphemes" if len(self.Graphemes) > 0 else ""
        corpus = ", " + str(len(self.Corpus)) + " corpus entries" if len(self.Corpus) > 0 else ""
        return self.Name + " (" + str(len(self.Vocabulary.keys())) + " words" + alphabet + corpus + ")"
    def FamilyTree(self, indentStr, indentAmount):
        return indentStr*indentAmount + str(self) + "\n"
    def ExtractAlphabet(self):
        graphemes, suspectWords = ExtractAlphabet(self.Vocabulary, self.Corpus)
        self.Graphemes = graphemes
        for word in suspectWords:
            self.SuspectWords.add(word)
        return self.Graphemes
    def SetAlphabet(self, alphabet):
        self.Graphemes = list(alphabet)
    def Save(self, path):
        import os
        target = os.path.join(path, self.Name)
        SaveDictionaryToFile(self.Vocabulary, target + DICTIONARY_FILE_EXT)
        if len(self.Graphemes) > 0: DumpAlphabetToFile(self.Graphemes, target + ALPHABET_FILE_EXT)
        if len(self.Corpus) > 0: DumpCorpusToFile(self.Corpus, target + CORPUS_FILE_EXT)

    @staticmethod
    def FromSoundChange(languageIn, newName, soundChangeFunc):
        vocab = {soundChangeFunc(word)[-1]:entry for (word,entry) in languageIn.Vocabulary.items()}
        corpus = [[soundChangeFunc(s[0])[-1]]+s[1:] for s in languageIn.Corpus]
        extractedAlphabet, suspectWords = ExtractAlphabet(vocab, corpus)
        alphabet = AddToAlphabetIfNeeded([soundChangeFunc(letter)[-1] for letter in languageIn.Graphemes], extractedAlphabet)
        return Language(newName, vocab, alphabet, suspectWords=languageIn.SuspectWords.union(suspectWords), corpus=corpus)

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
        unboundCorpuses = {}
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
                    alphabet = (unboundAlphabets[langName] if langName in unboundAlphabets else None),
                    corpus = (unboundCorpuses[langName] if langName in unboundCorpuses else None)
                )
            elif entry.lower().endswith(ALPHABET_FILE_EXT):
                langName = entry[0:-len(ALPHABET_FILE_EXT)]
                alphabet = ParseAlphabetFile(fullPath)
                if langName in self.Languages:
                    self.Languages[langName].SetAlphabet(alphabet)
                else:
                    unboundAlphabets[langName] = alphabet
            elif entry.lower().endswith(CORPUS_FILE_EXT):
                langName = entry[0:-len(CORPUS_FILE_EXT)]
                corpus = ParseCorpusFile(fullPath)
                if langName in self.Languages:
                    print "setting corpus"
                    self.Languages[langName].SetCorpus(corpus)
                else:
                    print "unbound corpus"
                    unboundCorpuses[langName] = corpus
            else:
                print "unknown filetype:", entry
    def __getitem__(self, key):
        return self.AllChildLanguages()[key]
    def __setitem__(self, key, value):
        # don't know where else to add the language at this point, so stick at root
        self.Languages[key] = value
    def __contains__(self, key):
        return key in self.AllChildLanguages()
    def AllChildLanguages(self):
        result = dict(self.Languages)
        for family in self.SubFamilies:
            result = dict(result.items() + family.AllChildLanguages().items())            
        return result
    def FamilyTree(self, indentStr, indentAmount):
        return (indentStr*indentAmount + str(self) + "\n"
            + "".join([l.FamilyTree(indentStr, indentAmount+1) for l in self.Languages.values()])
            + "".join([f.FamilyTree(indentStr, indentAmount+1) for f in self.SubFamilies]))
