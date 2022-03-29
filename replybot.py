# inspired by NH's reply bot, don't give me any credit for the idea.

from discord.ext import tasks
import re, emoji
from random import choice, randint

class replyBot():
    def __init__(self, client):
        self.client = client
        self.states = {}

        self.states["hello"] = replyBotState(
            matchwords=["hey","hi","hello","ey"],
            reply=["Hey","Hi","Hello"], replybefore=["","","","Oh uhh ","Yo! "], replyafter=["","",""," :wave:"," {name}",", ig..."]
        )
        self.states["bye"] = replyBotState(
            matchwords=["bye","goodbye","bubye","cya","gtg"],
            reply=["Bye","Goodbye","Bubye","Bye","Cya l8r"], replybefore=["","","Awww, "], replyafter=["","",""," :wave:"," {name}"]
        )
        self.states["questionwhen"] = replyBotState(
            findwords=["how long", "when will"],
            reply=[":soon:","Sooner than you want","Tomorrow","Next week","This year","Not anytime soon","Maybe never","100% never","You can't escape me {name}."], replyafter=["","",""," maybe..."," at least!", " at most."]
        )
        self.states["questionwhendid"] = replyBotState(
            findwords=["how long ago", "when did"],
            reply=["long ago", "just last month", "last week i thing", "yesterday", "not yet", "not yet, but it'll happen soon..."], replyafter=["","",""," maybe..."," i think."]
        )
        self.states["respond"] = replyBotState(
            findwords=["you sure"],
            reply=["i know so.", "i think so", "i'm very sure man.", "now that i think about it... i don't know..."]
        )

        self.states["funny"] = replyBotState( matchwords=["lol","lmao","ha"], reply=["lol","lmao","ha","What's so funny?"], noendpunc=True )
        self.states["uwu"] = replyBotState( findwords=["uwu","owo",":3","nya"], reply=["uwu","owo",":3","~nya"], replychance=2 )
        self.states["sorry"] = replyBotState( matchwords=["sorry","sry"], reply=["it's ok.","All is forgiven :)","fuck you.","fine"] )
        self.states["like"] = replyBotState( matchwords=["good","like","great","cool"], reply=["Thanks","You too","","You think so?","That's nice of you!"] )
        self.states["love"] = replyBotState( matchwords=["love","cute","luve"], reply=["Thanks","You too",":flushed:","You think so?",":heart:","That's nice of you!"] )
        self.states["hate"] = replyBotState( matchwords=["bad","dislike","hate","suck","sucks","ugly","dumbass","stupid"], reply=["That's not nice",":(","Please don't say things like that","Bruh","+ratio",":("] )
        self.states["unsad"] = replyBotState( matchwords=["sad","cry","depressed","depression",":("], reply=["Aww, everything will be ok","I'm here for you",":heart:","chear up :p"] )
        self.states["thanks"] = replyBotState( matchwords=["thanks","thank you"], reply=["yw","you're welcome","anytime",":thumbsup:"] )

        self.statemanager = ["hello|bye|sorry|respond", "^questionwhendid|questionwhen", "*funny|uwu|like|love|hate|unsad|thanks"]

        self.punctuation = [".",",","!","?",":"]
        self.endpunctuation = [".","!"]

    # what states does the message trigger
    def get_state(self, message):
        message = message.clean_content.lower()
        messagewords = message.replace("."," ").replace(","," ").replace("!"," ").replace("?"," ").replace(":"," ").split() # dirty but idc

        states = []
        for name in self.states:
            if self.states[name].state_match(message, messagewords):
                states.append(name)
        return states

    # when message is received, main client handdles channel checking.
    async def on_message(self, message):
        states = self.get_state(message)
        if len(states) == 0:
            await self.on_message_noreply(message)
            return

        txt = ""
        laststate = False
        finished = False
        for entry in self.statemanager:
            canmerge, dontmerge = False, False
            if entry.startswith("*"): # merge key
                canmerge, entry = True, entry[1:]
            if entry.startswith("^"): # single key
                dontmerge, entry = True, entry[1:]
            if "|" in entry: # split key
                entry = entry.split("|")
            else:
                entry = [entry]
            for state in entry:
                if state in states and (txt == "" or (canmerge)): # message passed checks for this reply
                    stateobj = self.states[state]
                    if (not stateobj.replychance) or randint(1,stateobj.replychance) == 1:
                        if txt != "":
                            if self.ends_in_punct(txt):
                                txt += " " # punctuation next to eachover is weird
                            else:
                                txt += ", "

                        laststate = state

                        if stateobj.replybefore:
                            txt += choice(stateobj.replybefore)
                        txt += choice(stateobj.reply)
                        if stateobj.replyafter:
                            txt += choice(stateobj.replyafter)

                        if canmerge or dontmerge:
                            finished = True
                # this is going in my cringe collection
                if finished:
                    break

        if laststate and self.states[laststate].endpunc and (not self.ends_in_punct(txt)) and randint(1,2) == 2:
            txt += choice(self.endpunctuation)

        if txt != "":
            await message.channel.send(txt.format(name=message.author.display_name))

    # all messages that invoke no reply
    async def on_message_noreply(self, message):
        emoji = getEmojiFromMsg(self.client, message)
        if len(emoji) > 0 and emoji[0]:
            await message.channel.send(emoji[0])
        return

    def ends_in_punct(self, txt):
        for punc in self.punctuation:
            if txt.endswith(punc):
                return True
        return False

# gets emoji for messag- CAN YOU FUCKING READ?
def getEmojiFromMsg(client, message):
    # default
    defemojis = emoji.core.distinct_emoji_lis(message.clean_content)

    # custom
    emojis = re.findall(r'<a?:\w*:\d*>', message.content) # spoopy regex
    emojis = [int(e.split(':')[2].replace('>', '')) for e in emojis]
    emojis = [client.get_emoji(e) for e in emojis]

    return emojis+defemojis

# each state, like greeting, determans what type of message was sent
class replyBotState():
    def __init__(self, **kwargs):
        self.matchwords = kwargs.get('matchwords',False)
        self.findwords = kwargs.get('findwords',False)
        self.startswith = kwargs.get('startswith',False)
        self.endswith = kwargs.get('endswith',False)

        self.reply = kwargs.get('reply',["default"])
        self.replychance = kwargs.get('replychance',1)
        self.replybefore = kwargs.get('replybefore',False)
        self.replyafter = kwargs.get('replyafter',False)
        self.endpunc = kwargs.get('noendpunc',True)

    # if the message fits the states checks
    def state_match(self, message, messagewords):
        def func_word(word):
            return (word in messagewords)
        def func_find(word):
            return (word in message)
        def func_starts(word):
            return (message.startswith(word))
        def func_ends(word):
            return (message.endswith(word))
            
        passed, passed2 = False, False

        # either work, don't need both
        if self.matchwords:
            passed = self.func_check(self.matchwords, func_word)
        if self.findwords:
            passed2 = self.func_check(self.findwords, func_find)
        if passed2:
            passed = True

        if passed and self.startswith:
            passed = self.func_check(self.startswith, func_starts)
        if passed and self.endswith:
            passed = self.func_check(self.endswith, func_ends)
    
        return passed

    def func_check(self, words, func):
        for word in words:
            if func(word):
                return True
        return False
