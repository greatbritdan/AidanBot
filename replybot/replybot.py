# inspired by NH's reply bot, don't give me any credit for the idea.

import discord
import discord.ext.commands as CM

import os, json, re, emoji, datetime
from random import choice, randint

from utils.checks import ab_check_ctx

# Holds data about states
class replyBotState():
    def __init__(
            self, contain:list[str]|bool=False, containall:list[list[str]]|bool=False, doesntcontain:list[str]|bool=False, afterstate:list[str]|bool=False, ignorereplies:bool=False, ignorementions:bool=False, 
            messagetype:str|bool="message", reply:dict[list[str]]|bool=False, replystartchance:int=1, replyendchance:int=1, replystart:dict[list[str]]|bool=False, replyend:dict[list[str]]|bool=False,
            customformat:dict[list[str|int]]|bool=False, punctuation:dict[list[str]]|bool=False, changefocus:str|bool=False, changemood:str|bool=False
        ):
        self.contain = contain
        self.containall = containall
        self.doesntcontain = doesntcontain
        self.afterstate = afterstate

        self.ignorereplies = ignorereplies
        self.ignorementions = ignorementions
        self.messagetype = messagetype

        self.reply = reply
        self.replystartchance = replystartchance
        self.replystart = replystart
        self.replyendchance = replyendchance
        self.replyend = replyend

        self.customformat = customformat

        self.punctuation = punctuation

        self.changefocus = changefocus
        self.changemood = changemood

# Holds local data for a guild
class replyBotGuild():
    def __init__(self, guild:discord.Guild):
        self.guild = guild

        self.mood:str = False
        self.focus:discord.Member = False
        self.moodchange:datetime.datetime = False
        self.focuschange:datetime.datetime = False
        self.lastmessage:datetime.datetime = False
        self.lastreply:datetime.datetime = False
        self.laststate:str = False

class replyBot():
    def __init__(self, client:CM.Bot):
        self.client = client

        self.guilds:dict[str,replyBotGuild] = {}

        self.statenames = ["greetings","farewell","howareyou","whatswrong","yousure","whenwill","whendid","doyoulike","didyoulike","whatsup","why","hateyou"]
        self.states = {}
        for filename in os.listdir('./replybot/states'):
            with open(f"./replybot/states/{filename}") as file:      
                data = json.load(file)
                self.states[filename[:-5]] = replyBotState(**data)

        self.punctuationcheck = [".",",","!","?",":","<",">","(",")","/"]
        self.moods = ["happy","neutral","sad","angry"]
        self.commands = ["list","info","print","listmoods","changemood","resetmood","changefocus","resetfocus"]

        self.emojilist = [
            ":face_holding_back_tears:",":joy:",":upside_down:",":slight_smile:",":smirk:",":unamused:",":pensive:",":weary:",":pleading_face:",":scream:",":nauseated_face:",":face_vomiting:",":smiling_imp:",
            ":imp:",":poop:",":skull:",":skull_crossbones:",":robot:",":thumbsup:",":thumbsdown:",":index_pointing_at_the_viewer:",":middle_finger:",":face_with_raised_eyebrow:",":sunglasses:"
        ]

        self.losemoodtime = 180
        self.losefocustime = 5
        self.ignoretime = 90
        self.ignoremaxtime = 600

    # when message is received, main client handdles channel checking.
    async def on_message(self, msg:discord.Message):
        ctx = await self.client.get_context(msg)

        if str(ctx.guild.id) not in self.guilds:
            self.guilds[str(ctx.guild.id)] = replyBotGuild(ctx.guild)
        g = self.guilds[str(ctx.guild.id)]

        author, message = msg.author, msg.clean_content.lower()
        messagewords = message.replace("."," ").replace(","," ").replace("!"," ").replace("?"," ").replace(":"," ").replace("-"," ").replace("/"," ").replace("'","") # It got too long
        messagewords = messagewords.replace("aidanbetabot","").replace("aidan betabot","").replace("aidan beta bot","").replace("betabot","").replace("beta bot","").replace("aidanbot","").replace("aidan bot","").split()
        now = datetime.datetime.now()

        # commands for monotring replybots activity
        if len(messagewords) >= 1 and messagewords[0] == "replybot":
            if not await ab_check_ctx(ctx, self.client, is_guild=True, has_mod_role=True):
                return

            if len(messagewords) >= 2:
                if messagewords[1] == "list":
                    await ctx.send(f"```Commands are {', '.join(self.commands)}```")
                elif messagewords[1] == "info":
                    await ctx.send(f"```- Welcome to the new and improved replybot! -\nRewritten from the ground up to be less dumb, featuring context and moods, this is still new so keep in mind things are still set to change.```")
                elif messagewords[1] == "print":
                    await ctx.send(f'''```
Version:      V1
----------------------------------------------------
= Local =
Mood:         {g.mood}
Mood change:  {g.moodchange}
Focus:        {str(g.focus)}
Focus change: {g.focuschange}
Last message: {g.lastmessage}
Last state:   {g.laststate}
Last reply:   {g.lastreply}
----------------------------------------------------
= Global =
Amount of time before he changes his mood.
Change Mood Time: {self.losemoodtime}
Amount of time before he loses focus of someone.
Lose Focus Time:  {self.losefocustime}
Amount of time after his last reply so he can mention it.
Ignore Time:      {self.ignoretime}
Maximum amount of time after his last reply, if higher the replytime will just reset.
Ignore Max Time:  {self.ignoremaxtime}
```''')
                elif messagewords[1] == "listmoods":
                    await ctx.send(f"```Current moods: {', '.join(self.moods)}```")
                elif messagewords[1] == "changemood" and len(messagewords) >= 3:
                    if messagewords[2] in self.moods:
                        g.mood = messagewords[2]
                        g.moodchange = now
                        await ctx.send(f"```Mood changed to {g.mood}```")
                    else:
                        await ctx.send(f"```{messagewords[2]} is not a valid mood```")
                elif messagewords[1] == "resetmood":
                    g.mood = False
                    g.moodchange = now
                    await ctx.send(f"```Mood reset```")
                elif messagewords[1] == "changefocus" and len(messagewords) >= 3:
                    user = await ctx.guild.fetch_member(int(messagewords[2]))
                    if user:
                        g.focus = user
                        g.focuschange = now
                        await ctx.send(f"```Focus changed to {str(user)}```")
                    else:
                        await ctx.send(f"```{messagewords[2]} is not a valid user ID```")      
                elif messagewords[1] == "resetfocus":
                    g.focus = False
                    g.focuschange = now
                    await ctx.send(f"```Focus reset```")
            return

        # changes aidanbots mood
        if (not g.mood) or (g.moodchange and (now - g.moodchange).seconds > self.losemoodtime):
            g.mood = choice(self.moods)
            g.moodchange = now

        # reset aidanbots focus
        if (g.focuschange and (now - g.focuschange).seconds > self.losefocustime):
            g.focus = False
            g.focuschange = now

        # Works out what is being said and returns a state
        state = "none"
        for st in self.statenames:
            if st in self.states:
                s:replyBotState = self.states[st]
                if s.afterstate and g.laststate not in s.afterstate:
                    continue
                if s.doesntcontain and containsWord(messagewords, s.doesntcontain):
                    continue
                if (s.contain and containsWord(messagewords, s.contain)) or (s.containall and containsWordAll(messagewords, s.containall)):
                    # Basically, if he shouldn't reply if the user is replying to someone else.
                    if s.ignorereplies and msg.type == discord.MessageType.reply:
                        rmsg:discord.Message = await ctx.channel.fetch_message(msg.reference.message_id)
                        if rmsg.author != self.client.user:
                            continue
                    # Basically, if he shouldn't reply if the user doesn't ping them and pings someone else.
                    if s.ignorementions and len(msg.mentions) > 0 and (self.client.user not in msg.mentions):
                        continue
                    state = st
                    break
        
        # How dare you disrupt him
        if state != "none" and g.focus and author != g.focus:
            state = "disrupt"

        # Just post random crap...
        if state == "none" and ((not g.focus and randint(1,6) == 6) or (g.focus and randint(1,9) == 9)):
            state = "random"

        #If last reply more than 3 minutes ago and last message less than 7 and a half minutes
        if state == "none" and g.lastreply and (now - g.lastreply).seconds > self.ignoretime:
            if (now - g.lastmessage).seconds <= self.ignoremaxtime:
                g.lastreply = now - datetime.timedelta(seconds = self.ignoretime-30) # adds a little delay before the next one.

                oldmood = g.mood
                if g.mood == "happy":
                    g.mood = "neutral"
                elif g.mood == "neutral":
                    g.mood = choice(["sad","angry"])
                elif g.mood == "sad":
                    g.mood = "angry"

                if oldmood != g.mood:
                    g.moodchange = now
                state = "ignored"
            else:
                g.lastreply = False #Resets if it has been too long

        # Update last message
        g.lastmessage = now

        # If a state isn't chosen, don't reply
        if state == "none":
            return False
        
        # Update last reply
        g.lastreply = now
        g.laststate = state
        
        s:replyBotState = self.states[state]

        # This used to be so simple...
        # Generates the reply
        txt:str = ""
        if isinstance(s.reply, dict):
            if g.mood in s.reply:
                txt = choice(s.reply[g.mood])
            elif "_all" in s.reply:
                txt = choice(s.reply["_all"])
        else:
            txt = choice(s.reply)

        nostart, noend = False, False
        if txt == "":
            await ctx.send(f"```Error: no reply was generated.```")
            return False
        else:
            if txt[0] == "^":
                txt, nostart = txt[1:], True
            if txt[-1] == "^":
                txt, noend = txt[:-1], True
        
        if (not nostart) and s.replystart and randint(1,s.replystartchance) == 1:
            c = ""
            if isinstance(s.replystart, dict):
                if g.mood in s.replystart:
                    c = choice(s.replystart[g.mood])
                elif "_all" in s.replystart:
                    c = choice(s.replystart["_all"])
            else:
                c = choice(s.replystart)
            if c != "":
                if txt[1].isupper():
                    txt = f"{c} {txt[0].lower()}{txt[1:]}" # just lower first character
                else:
                    txt = f"{c} {txt}"

        if (not noend) and s.replyend and txt[-1] not in self.punctuationcheck and randint(1,s.replyendchance) == 1:
            c = ""
            if isinstance(s.replyend, dict):
                if g.mood in s.replyend:
                    c = choice(s.replyend[g.mood])
                elif "_all" in s.replyend:
                    c = choice(s.replyend["_all"])
            else:
                c = choice(s.replyend)
            if c != "":
                skippunc = False
                if c[0] == "%":
                    c, skippunc = c[1:], True
                if skippunc or c[1] in self.punctuationcheck:
                    txt = f"{txt} {c}"
                else:
                    txt = f"{txt}, {c}"

        emoji = ""
        nitroemoji, nitroemoji2, nitroemoji3 = "", "", ""
        if "{emoji}" in txt:
            if randint(1,2) == 2:
                emoji = choice(self.emojilist)
            else:
                emoji = choice(ctx.guild.emojis)
        if "{nitroemoji}" in txt:
            nitroemoji =  choice([emoji for emoji in ctx.guild.emojis if emoji.animated])
            nitroemoji2 = choice([emoji for emoji in ctx.guild.emojis if emoji.animated])
            nitroemoji3 = choice([emoji for emoji in ctx.guild.emojis if emoji.animated])

        stickers = None
        if "{sticker}" in txt:
            txt = ""
            stickers = [ choice(ctx.guild.stickers) ]

        data = { "author_displayname": author.display_name, "emoji": emoji, "nitroemoji": nitroemoji, "nitroemoji2": nitroemoji2, "nitroemoji3": nitroemoji3 }
        if g.focus:
            data["focus_displayname"] = g.focus.display_name
        if s.customformat:
            for form in s.customformat:
                if type(form[0]) == int:
                    data[form] = randint(s.customformat[form][0], s.customformat[form][1])
                else:
                    data[form] = choice(s.customformat[form])

        txt = txt.format(**data)

        if txt != "" and txt[-1] not in self.punctuationcheck:
            if isinstance(s.punctuation, dict):
                if g.mood in s.punctuation:
                    txt = f"{txt}{choice(s.punctuation[g.mood])}"
            else:
                txt = f"{txt}{choice(s.punctuation)}"

        # change focus?
        if not g.focus:
            g.focus = author
            g.focuschange = now
        elif s.changefocus and s.changefocus == "reset":
            g.focus = False
            g.focuschange = now

        # change mood?
        if s.changemood:
            c, m = False, False
            if isinstance(s.changemood, dict):
                if g.mood in s.changemood:
                    c = s.changemood[g.mood]
                elif "_all" in s.changemood:
                    c = s.changemood["_all"]
            else:
                c = s.changemood

            if isinstance(c, list):
                c = choice(c)
            if c == "reset":
                m = False
            elif c in self.moods:
                m = c

            if m:
                g.mood = m
                g.moodchange = now

        #if randint(1,1000) == 1000:
        #    txt = "Look, i may be stupid but... what the fuck!?!"
        
        # Time to send!
        if s.messagetype == "reply":
            await ctx.reply(txt, stickers=stickers, mention_author=False, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        elif s.messagetype == "message":
            await ctx.send(txt, stickers=stickers, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        else:
            print(txt)
        return True

# general functions #

def containsWord(messagewords, words):
    for word in words:
        # multi word
        if " " in word:
            if containsWords(messagewords, word.split()):
                return True
        # single word
        if (word in messagewords):
            return True
    return False

def containsWordAll(messagewords, wordgroups):
    for words in wordgroups:
        if not containsWord(messagewords, words):
            return False
    return True

def containsWords(messagewords, words):
    i = 0
    for word in messagewords:
        if word == words[i]:
            i += 1
            if i >= len(words):
                return True
        else:
            i = 0
    return False

# other functions #

def getEmojiFromMsg(client, message):
    # default
    defemojis = emoji.core.distinct_emoji_lis(message.clean_content)
    # custom
    emojis = re.findall(r'<a?:\w*:\d*>', message.content) # spoopy regex
    emojis = [int(e.split(':')[2].replace('>', '')) for e in emojis]
    emojis = [client.get_emoji(e) for e in emojis]
    return emojis+defemojis