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
        self.CurrentItem = ""
        self.LastList = []
        self.SoundChanges = []
        self.SoundChangeSets = self.AllFamilies.AllAvailableSoundChanges()
    def emptyline(self):
        pass
    def do_fams(self, line):
        print self.AllFamilies.FamilyTree("*", 0)
    def help_addsc(self):
        print "addsc <rule> - add a new soundchange, format X > Y / C unicode character format is \\uXXXX"
    def do_addsc(self, line):
        line = line.decode('raw_unicode_escape')
        try:
            if (self.LoadSoundChange(line)):
                for rule in self.SoundChanges[-1].OrigRules(): print rule
        except UnicodeDecodeError:
            print "unicode character format is \\uXXXX"
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
        if (len(self.SoundChanges) == 0):
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
            if pos == None:
                self.SoundChanges.append(sc)
            else:
                self.SoundChanges.insert(pos - 1, sc)
            return True
        except:
            print "ADD SOUND CHANGE FAILED"
            return False
    def do_applysc(self, line):
        args = line.split(" ")
        sourceName = args[0]
        if sourceName not in self.AllFamilies:
            print sourceName, "doesn't exist"
            return
        source = self.AllFamilies[sourceName]
        destName = args[1]
        if destName in self.AllFamilies:
            print destName, "already exists."
        else:
            sc = soundChange.SoundChange.FromSoundChangeList(self.SoundChanges)
            self.AllFamilies[destName] = Language.FromSoundChange(source, destName, sc.Apply)
            print destName, "added."
    def getChangesAndSame(self, source):
        changes = []
        same = []
        for (word,result) in self.yieldFromSoundChange(source):
            if word == result:
                same.append(word)
            else:
                changes.append(word + u"->" + result)
        return changes, same
    def yieldChangeOrSameFromSoundChange(self, isChange, source):
        for (word,result) in self.yieldFromSoundChange(source):
            if (word == result and not(isChange)) or (word != result and isChange):
                yield (word,result)
    def yieldFromSoundChange(self, source):
        sc = soundChange.SoundChange.FromSoundChangeList(self.SoundChanges)
        for word in source.Vocabulary.keys():
            result = sc.Apply(word)[-1]
            yield (word, result)

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

    def help_listwords(self):
        print "listwords [lang] - list the vocabulary of a language"
    def do_listwords(self, line):
        source = self.LangFromLineOrCurrent(line)
        if source != None:
            self.LastList = []
            for key in source.Vocabulary.keys():
                print key, ":", str(source.Vocabulary[key])
                self.LastList.append(key)


    def help_showchanges(self):
        print "showchanges [limit [skip]] - show words affected by soundchange, at most limit entries displayed, skipping skip"
    def do_showchanges(self, line):
        self.showsameordiff(line, True)

    def help_showsame(self):
        print "showsame [limit [skip]] - show words unaffected by soundchange, at most limit entries displayed, skipping skip"
    def do_showsame(self, line):
        self.showsameordiff(line, False)

    def parseLimitSkip(self, line):
        limit = 0
        skip = 0
        try:
            limit = int(line.strip().split(" ")[0])
            skip = int(line.strip().split(" ")[1])
        except (IndexError,ValueError):
            pass
        return limit, skip

    def showsameordiff(self, line, isShowDiff):
        limit,skip = self.parseLimitSkip(line)
        source = self.LangFromLineOrCurrent('') # no lang from line
        if source != None:
            self.LastList = []
            count = 0
            for (orig,word) in take(self.yieldChangeOrSameFromSoundChange(isShowDiff, source),skip):
                count += 1
                if (isShowDiff): print orig, "->",
                print word
                self.LastList.append(word)
                if (limit != 0 and count >= limit):
                    break

    def help_showcc(self):
        print "showcc [limit [skip]] - show words with two consonants in a row after soundchange, at most limit entries displayed, skipping skip"
    def do_showcc(self, line):
        limit,skip = self.parseLimitSkip(line)
        source = self.LangFromLineOrCurrent('') # no lang from line
        if source != None:
            self.LastList = []
            for (orig, word) in take(self.yieldFromSoundChange(source),skip):
                gs = ipaParse.GraphemeSplit(word)
                for pair in [(gs[ii],gs[ii+1]) for ii in range(len(gs)-1)]:
                    if pair[0] in ipaParse.ALL_CONSONANTS and pair[1] in ipaParse.ALL_CONSONANTS:
                        print word
                        self.LastList.append(word)
                        break
                if limit > 0 and len(self.LastList) >= limit: break

    def help_loadscfrompath(self):
        print "loadscfrompath /full/path/to/file - load a soundchange file directly"
    def do_loadscfrompath(self, line):
        try:
            self.SoundChanges = soundChange.GetSoundChanges(line)
        except:
            print "error loading", line

    def help_listscsets(self):
        print "listscsets - list available sound change sets"
    def do_listscsets(self, line):
        self.LastList = []
        for name in self.SoundChangeSets.keys():
            print name
            self.LastList.append(name)

    def help_loadsc(self):
        print "loadsc [sound change name] - load a sound change from (optionally) a sound change name or (by default) the current item"
    def do_loadsc(self, line):
        scName = ""
        if (line != ""):
            if (line in self.SoundChangeSets.keys()):
                scName = line
            else:
                print "no such sound change set available:", line
                return
        else:
            print 'using current item', self.CurrentItem
            if (self.CurrentItem in self.SoundChangeSets.keys()):
                scName = self.CurrentItem
            else:
                print "no such sound change set available:", self.CurrentItem
                return
        self.SoundChanges = [sc for sc in self.SoundChangeSets[scName]]
        print "Loaded", len(self.SoundChanges), "sound changes."

    def help_savesc(self):
            print "savesc <full_path_to_sc_file_including_.soundchange> - save a soundchange file"
    def do_savesc(self, line):
        soundChange.SoundChange.FromSoundChangeList(self.SoundChanges).Save(line)
        print "saved."
        #TODO: Extract the filename and then put this in the list of available sound change sets

    def help_enum(self):
        print "enum - enumerate the last list so that you can pick one with pick"
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

    def do_splitcur(self, line):
        if len(self.CurrentItem) == 0:
            print "please pick a current item with enum and pick"
        self.LastList = []
        for word in self.CurrentItem.split(" "):
            print word
            self.LastList.append(word)

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

    def help_lookup(self):
        print "lookup - lookup current item in dictionary"
    def do_lookup(self, line):
        if len(self.CurrentLangName) == 0:
            print "please select a current language with lang"
            return
        elif len(self.CurrentItem) == 0:
            print "please select a current item with enum and pick"
            return
        lang = self.AllFamilies[self.CurrentLangName]
        if self.CurrentItem in lang.Vocabulary:
            for definition in lang.Vocabulary[self.CurrentItem]:
                byAttrib = paddedZip(lang.Attributes[1:], "?", definition, "?")
                print self.CurrentItem,":"
                for attrib,value in byAttrib:
                    print " ",attrib + ":",value
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

def take(gen, count):
    zip(range(count),gen)
    return gen

def padded(l, pad):
    for x in l: yield x
    while True: yield pad
def paddedZip(L1,P1,L2,P2):
    if len(L1) == len(L2):
        return zip(L1,L2)
    elif len(L1) > len(L2):
        return zip(L1, padded(L2,P2))
    else:
        return zip(padded(L1,P1), L2)

if __name__ == '__main__':
    interact = Interactive()
    interact.cmdloop()
