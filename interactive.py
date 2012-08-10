# -*- encoding: utf-8 -*-
###
## Interactive console for language construction

from dictionaryManager import *
import soundChange
import cmd

class Interactive(cmd.Cmd):
    def preloop(self):
        self.prompt = "[] > "
        print "Loading families..."
        self.AllFamilies = LoadFromDefault()
        allChildLanguages = self.AllFamilies.AllChildLanguages()
        if len(allChildLanguages.keys()) == 0:
            print "*"*80
            print "You don't seem to have any languages"
            print "*"*80
            print BaseDictionaryHowTo
        else:
            print self.AllFamilies.FamilyTree("*", 0)
        self.CurrentLangName = ""
    def emptyline(self):
        pass
    def do_fams(self, line):
        print self.AllFamilies.FamilyTree("*", 0)
    def do_addsc(self, line):
        line = line.decode('raw_unicode_escape')
        self.LoadSoundChange(line)
        for rule in self.SoundChanges[-1].OrigRules(): print rule
    def do_insertsc(self, line):
        line = line.decode('raw_unicode_escape')
        lineparts = line.split(" ")
        try:
            pos = int(lineparts[0])
            self.LoadSoundChange(' '.join(lineparts[1:]), pos)
            for rule in self.SoundChanges[pos - 1].OrigRules(): print rule
        except:
            print "syntax: insertsc [index] [soundchange]"
    def do_listsc(self, line):
        if not (hasattr(self, "SoundChanges")):
            print "please add sound changes with addsc or loadsc"
        else:
            self.LastList = []
            for sc in self.SoundChanges:
                for rule in sc.OrigRules():
                    print rule
                    self.LastList.append(rule)

    def LoadSoundChange(self, rule, pos=None):
        try:
            sc = soundChange.SoundChange([rule], {"vowel": ipaParse.ALL_VOWELS})
            if not(hasattr(self, "SoundChanges")) or self.SoundChanges == None:
                self.SoundChanges = []
            if pos == None:
                self.SoundChanges.append(sc)
            else:
                self.SoundChanges.insert(pos - 1, sc)
        except:
            print "ADD SOUND CHANGE FAILED"
    def do_applysc(self, line):
        args = line.split(" ")
        source = self.AllFamilies[args[0]]
        destName = args[1]
        if destName in self.AllFamilies:
            print destName, "already exists."
        else:
            sc = soundChange.SoundChange.FromSoundChangeList(self.SoundChanges)
            self.AllFamilies[destName] = Language.FromSoundChange(source, destName, sc.Apply)
            print destName, "added."
    def getChangesAndSame(self, source):
        sc = soundChange.SoundChange.FromSoundChangeList(self.SoundChanges)
        changes = []
        same = []
        for word in source.Vocabulary.keys():
            result = sc.Apply(word)[-1]
            if word == result:
                same.append(word)
            else:
                changes.append(word + u"->" + result)
        return changes, same

    def LangFromLineOrCurrent(self, line):
        args = line.split(" ")
        lang = args[0].strip()
        if len(lang) == 0 and len(self.CurrentLangName) > 0:
            lang = self.CurrentLangName
        if lang not in self.AllFamilies:
            print lang, "does not exist."
            return None
        else:
            return self.AllFamilies[lang]

    def do_listcorpus(self, line):
        source = self.LangFromLineOrCurrent(line)
        if source != None:
            self.LastList = []
            for line in source.Corpus:
                print " = ".join(line)
                self.LastList.append(line[0])

    def do_listalphabet(self, line):
        source = self.LangFromLineOrCurrent(line)
        if source != None:
            self.LastList = []
            for line in source.Graphemes:
                print line
                self.LastList.append(line)

    def do_showchanges(self, line):
        source = self.LangFromLineOrCurrent(line)
        if source != None:
            self.LastList = []
            for word in self.getChangesAndSame(source)[0]:
                print word
                self.LastList.append(word)

    def do_showsame(self, line):
        source = self.LangFromLineOrCurrent(line)
        if source != None:
            self.LastList = []
            for word in self.getChangesAndSame(source)[1]:
                print word
                self.LastList.append(word)

    def do_loadsc(self, line):
        import codecs
        inFile = codecs.open(line+".soundchange", encoding="utf-8")
        self.SoundChanges = None
        for line in inFile.readlines():
            self.LoadSoundChange(line.strip())

    def do_savesc(self, line):
        soundChange.SoundChange.FromSoundChangeList(self.SoundChanges).Save(line+".soundchange")
        print "saved."

    def do_enum(self, line):
        for item in enumerate(self.LastList):
            print item[0]+1,":",item[1]

    def do_pick(self, line):
        try:
            index = int(line) - 1
            self.CurrentItem = self.LastList[index]
            print "selected:", self.CurrentItem
        except ValueError:
            print line, "is not a numerical index. Use enum to find an index."
        except IndexError:
            print line, "is out of range. Use enum to find an index."
    def do_picklang(self, line):
        try:
            index = int(line) - 1
            self.SetCurLang(self.LastList[index])
        except ValueError:
            print line, "is not a numerical index. Use enum to find an index."
        except IndexError:
            print line, "is out of range. Use enum to find an index."

    def do_decode(self, line):
        if not(hasattr(self, "CurrentItem")):
            print "No current item. Use enum and pick to get one."
        else:
            for c in self.CurrentItem:
                print c,"=",hex(ord(c))[2:]

    def do_showchar(self, line):
        line = line.decode('raw_unicode_escape')
        if len(line) > 0:
            self.showchar(line)
        elif len(self.CurrentItem) > 0:
            self.showchar(self.CurrentItem)
        else:
            print "please pass a value or select a current item with enum and pick"

    def showchar(self, line):
        graphemes = ipaParse.GraphemeSplit(line)
        for g in graphemes:
            if g in ipaParse.ConsonantData:
                print g,":",ipaParse.ConsonantData[g]
            elif g in ipaParse.VowelData:
                print g,":",ipaParse.VowelData[g]
            else:
                print g,": currently unknown."

    def SetCurLang(self, langName):
        lang = self.AllFamilies[langName]
        print "selected:", lang
        self.CurrentLangName = langName
        self.prompt = langName + " > "

    def do_lang(self, line):
        lang = line.strip()
        if lang in self.AllFamilies:
            self.SetCurLang(lang)
        else:
            print lang, "not found."
    def do_listlang(self, line):
        allChildLanguages = self.AllFamilies.AllChildLanguages()
        self.LastList = []
        for langName in allChildLanguages.keys():
            lang = allChildLanguages[langName]
            print lang
            self.LastList.append(lang.Name)

    def do_lookup(self, line):
        if len(self.CurrentLangName) == 0:
            print "please select a current language with lang"
        elif len(self.CurrentItem) == 0:
            print "please select a current item with enum and pick"
        lang = self.AllFamilies[self.CurrentLangName]
        if self.CurrentItem in lang.Vocabulary:
            print self.CurrentItem,":",lang.Vocabulary[self.CurrentItem]
        else:
            print self.CurrentItem,"not in",lang

    def do_savecurlang(self, line):
        if len(self.CurrentLangName) == 0:
            print "please select a current language with lang"
        lang = self.AllFamilies[self.CurrentLangName]
        lang.Save("")
        print "saved."

    def do_quit(self, line):
        return True

if __name__ == '__main__':
    interact = Interactive()
    interact.cmdloop()
