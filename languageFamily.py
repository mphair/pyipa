# -*- encoding: utf-8 -*-
###
## Classes to contain and maintain data about language families and the languages therein

def ParseDictionaryFile(fileName):
    f = open(fileName)
    splitlines = [[l.strip() for l in line.split("\t")] for line in f.readlines()]
    d = {}
    for line in splitlines:
        if not(d.has_key(line[0])): d[line[0]] = []
        d[line[0]].append(line[1:])
    return d

class Language:
    def __init__(self, name, vocabulary):
        self.Name = name
        self.Vocabulary = vocabulary
    def __repr__(self):
        return self.Name + " (" + str(len(self.Vocabulary.keys())) + " words)"
    def FamilyTree(self, indentStr, indentAmount):
        return indentStr*indentAmount + str(self) + "\n"

class LanguageFamily:
    def __init__(self, name):
        self.SubFamilies = []
        self.Languages = {}
        self.Name = name
    def __repr__(self):
        return self.Name + " (" + str(len(self.AllChildLanguages().keys())) + " languages)"
    def LoadFromPath(self, path):
        import os
        for entry in os.listdir(path):
            fullPath = os.path.join(path, entry)
            if os.path.isdir(fullPath):
                family = LanguageFamily(entry)
                family.LoadFromPath(fullPath)
                self.SubFamilies.append(family)
            else:
                self.Languages[entry] = Language(entry, ParseDictionaryFile(fullPath))
    def AllChildLanguages(self):
        result = dict(self.Languages)
        for family in self.SubFamilies:
            result = dict(result.items() + family.AllChildLanguages().items())            
        return result
    def FamilyTree(self, indentStr, indentAmount):
        return (indentStr*indentAmount + str(self) + "\n"
            + "".join([l.FamilyTree(indentStr, indentAmount+1) for l in self.Languages.values()])
            + "".join([f.FamilyTree(indentStr, indentAmount+1) for f in self.SubFamilies]))

