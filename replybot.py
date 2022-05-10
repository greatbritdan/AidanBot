# inspired by NH's reply bot, don't give me any credit for the idea.

import re, emoji
from random import choice, randint

class replyBot():
    def __init__(self, client):
        self.client = client
        self.states = {}

        self.states["hello"] = replyBotState( matchwords=["hey","hi","hello","ey"],
            reply=["Hey","Hi","Hello"], replybefore=["","","","Oh uhh ","Yo! "], replyafter=["","",""," :wave:"," {name}",", ig..."] )
        self.states["bye"] = replyBotState( matchwords=["bye","goodbye","bubye","cya","gtg"],
            reply=["Bye","Goodbye","Bubye","Bye","Cya l8r"], replybefore=["","","Awww, "], replyafter=["","",""," :wave:"," {name}"] )
        self.states["questionwhen"] = replyBotState( findwords=["how long", "when will"],
            replytype="reply", reply=[":soon:","Sooner than you want","Tomorrow","Next week","This year","Not anytime soon","Maybe never","100% never","You can't escape me {name}."], replyafter=["","",""," maybe..."," at least!", " at most."] )
        self.states["questionwhendid"] = replyBotState( findwords=["how long ago", "when did"],
            replytype="reply", reply=["long ago", "just last month", "last week i thing", "yesterday", "not yet", "not yet, but it'll happen soon..."], replyafter=["","",""," maybe..."," i think."] )
        self.states["questiondoyou"] = replyBotState( findwords=["do you", "did you"],
            replytype="reply", reply=["Yes, 100%", "Yep", "I'm sure", "I think so", "uhhh idk", "i donb't think so", "nahhh", "nope", "NEVER!"], replyafter=["","",""," maybe..."," i think."] )
        self.states["respond"] = replyBotState( findwords=["you sure"],
            reply=["i know so.", "i think so", "i'm very sure man.", "now that i think about it... i don't know..."] )

        self.states["funny"] = replyBotState( matchwords=["lol","lmao","ha"], reply=["lol","lmao","ha","What's so funny?"], noendpunc=True )
        self.states["uwu"] = replyBotState( findwords=["uwu","owo",":3","nya"], reply=["uwu","owo",":3","~nya"], replychance=2 )
        self.states["sus"] = replyBotState( findwords=["sus","sussy","amogus","amongus","among us","among","vent"], reply=["AMOGUS!","Oh god... sus","SUSSY BAKA?","Tha's sus","{name} vented."], replychance=2 )
        self.states["sorry"] = replyBotState( matchwords=["sorry","sry"], reply=["it's ok.","All is forgiven :)","screw you.","fine"] )
        self.states["like"] = replyBotState( matchwords=["good","like","great","cool"], reply=["Thanks","You too","You think so?","That's nice of you!"] )
        self.states["love"] = replyBotState( matchwords=["love","cute","luve"], reply=["Thanks","You too",":flushed:","You think so?",":heart:","That's nice of you!"] )
        self.states["hate"] = replyBotState( matchwords=["bad","dislike","hate","suck","sucks","ugly","dumbass","stupid"], reply=["That's not nice",":(","Please don't say things like that","Bruh","+ratio",":("] )
        self.states["unsad"] = replyBotState( matchwords=["sad","cry","depressed","depression",":("], reply=["Aww, everything will be ok","I'm here for you",":heart:","chear up :p"] )
        self.states["thanks"] = replyBotState( matchwords=["thanks","thank you"], reply=["yw","you're welcome","anytime",":thumbsup:"] )

        self.states["else"] = replyBotState(
            alwaystrigger=True, replychance=4,
            replybefore=["","","","Hey, ","Oy, ","Uhh... ","Hear me out. ","Hold up!... "],
            reply=["Wanna say that to my face?","Wanna repeat yourself?","Who asked lmao.","BRUH","I'm sorry what?","That's cringe","I wish i cared.","What if... You shut up?","LMAO","+ ratio","\*yawn*",""]
        )
        self.states["rareelse"] = replyBotState(
            alwaystrigger=True, replychance=12,
            reply=["Look, i may be stupid but... what the fuck!?!","This is going in my cringe collection!","Caught yo ass in 4K."]
        )

        self.statemanager = ["^questionwhendid|questionwhen|questiondoyou", "hello|bye|sorry|respond", "*funny|uwu|sus|like|love|hate|unsad|thanks", "rareelse|else"]

        self.punctuation = [".",",","!","?",":"]
        self.endpunctuation = [".","!"]

    # what states does the message trigger
    def get_state(self, message):
        message = message.clean_content.lower()
        messagewords = message.replace("."," ").replace(","," ").replace("!"," ").replace("?"," ").replace(":"," ").split()

        states = []
        for name in self.states:
            if self.states[name].state_match(message, messagewords):
                states.append(name)
        return states

    # when message is received, main client handdles channel checking.
    async def on_message(self, message):
        states = self.get_state(message)

        txt = ""
        laststate = False
        breakpls = False
        replied = False
        for entry in self.statemanager:
            merge, single = False, False
            if entry.startswith("*"):
                merge, entry = True, entry[1:]
            if entry.startswith("^"):
                single, entry = True, entry[1:]
            if "|" in entry:
                entry = entry.split("|")
            else:
                entry = [entry]

            for state in entry:
                if state in states and (txt == "" or merge):
                    replystate = self.states[state]
                    if (not replystate.replychance) or randint(1,replystate.replychance) == 1:
                        replied = True
                        if txt != "":
                            if self.ends_in_punct(txt):
                                txt += " " # punctuation next to eachover is weird
                            else:
                                txt += ", "

                        laststate = state
                        if replystate.replybefore:
                            txt += choice(replystate.replybefore)
                        txt += choice(replystate.reply)
                        if replystate.replyafter:
                            txt += choice(replystate.replyafter)

                        if merge or single:
                            breakpls = True
            if breakpls:
                break

        if not replied:
            await self.on_message_noreply(message)
            return
        else:
            if self.states[laststate].endpunc and (not self.ends_in_punct(txt)) and randint(1,2) == 2:
                txt += choice(self.endpunctuation)
            ctx = await self.client.get_context(message)
            if self.states[laststate].replytype == "reply":
                await ctx.reply(txt.format(name=message.author.display_name), mention_author=False)
            else:
                await ctx.send(txt.format(name=message.author.display_name))

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
        self.replytype = kwargs.get('replytype',"send")
        self.endpunc = kwargs.get('noendpunc',True)

        self.alwaystrigger = kwargs.get('alwaystrigger',False)

    # if the message fits the states checks
    def state_match(self, message, messagewords):
        if self.alwaystrigger:
            return True

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