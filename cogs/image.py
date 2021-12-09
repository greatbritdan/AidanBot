import discord
from discord.ext import commands

from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageEnhance

import io, datetime, math

from functions import ComError

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class ImageCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["emu"])
	@commands.cooldown(1, 5)
	async def emu(self, ctx, text="text", text2=None):
		image = await getImage(ctx)
		w, h = image.size
		textsize = 128
		while ((w/4)*3 < len(text)*textsize) or ((h/8) < textsize):
			textsize -= 8
		if text2:
			while (w/4)*3 < len(text2)*textsize:
				textsize -= 8
		if textsize == 0:
			await ComError(ctx, self.client, "Image too small, try to make it bigger!")
			return

		font = ImageFont.truetype("assets/emulogic.ttf", textsize)
		draw = ImageDraw.Draw(image)
		gap = textsize/8

		top, bottom = (gap*5), h-(gap*16)
		pos = (w/2)-((len(text)*textsize)/2)
		draw = backtext(draw, pos, top, text, gap, font)
		if text2:
			pos2 = (w/2)-((len(text2)*textsize)/2)
			draw = backtext(draw, pos2, bottom, text2, gap, font)

		await sendImage(ctx, image)

	@commands.command(description=DESC["killoverlay"])
	@commands.cooldown(1, 5)
	async def killoverlay(self, ctx, name="minecraft"):
		types = ["minecraft", "darksouls", "ass", "gta"]
		typ = 0
		try:
			typ = types.index(name) + 1
		except ValueError:
			await ComError(ctx, self.client, "Not a valid type!")
			return
		
		image = await getImage(ctx)
		over = Image.open(f"assets/deathoverlay{typ}.png")

		nwidth = math.ceil(image.width/(image.height/over.height))
		image = image.resize((nwidth, over.height))
		if typ == 2:
			image = ImageEnhance.Color(image).enhance(0.35)
		if typ == 4:
			image = ImageEnhance.Color(image).enhance(0)

		image.paste(over, (-math.ceil((over.width-nwidth)/2),0), over)
		if nwidth > over.width:
			overcopy = Image.open(f"assets/deathoverlay{typ}.png")
			overcopy = overcopy.crop((0,0,12,over.height))
			overcopy = overcopy.resize((math.ceil((image.width-over.width)/2), over.height))

			# extra = Image.new("RGBA", (math.ceil((image.width-over.width)/2), over.height), (191,0,0,127))
			image.paste(overcopy, (0,0), overcopy)
			image.paste(overcopy, (image.width-math.ceil((image.width-over.width)/2),0), overcopy)

		await sendImage(ctx, image.convert("RGB"))

	@commands.command(aliases=["quote"], description=DESC["quoted"])
	@commands.cooldown(1, 5)
	async def quoted(self, ctx, *, text="text"):
		await self.gen_quote(ctx, ctx.author, text, False)

	@commands.command(description=DESC["quotel"])
	@commands.cooldown(1, 5)
	async def quotel(self, ctx, *, text="text"):
		await self.gen_quote(ctx, ctx.author, text, True)

	@commands.command()
	@commands.is_owner()
	async def quoteo(self, ctx, text="text", user:discord.Member=None, light:bool=False):
		if not user:
			user = ctx.author
		await self.gen_quote(ctx, user, text, light)

	async def gen_quote(self, ctx, user, text, lightmode=False):
		backcol, textcol, alttextcol = (54,57,63), (255,255,255), (116, 127, 141)
		if lightmode:
			backcol, textcol, alttextcol = (255,255,255), (46, 51, 56), (114, 118, 125)

		font = ImageFont.truetype("assets/whitneymedium.ttf", 16)
		fontbold = ImageFont.truetype("assets/whitneysemibold.ttf", 16)
		fontsmall = ImageFont.truetype("assets/whitneymedium.ttf", 10)
		time = datetime.datetime.now()

		col = user.color
		name = user.display_name
		textsize = font.getsize(text)[0]
		namesize = fontbold.getsize(name)[0]

		maxwidth = textsize
		if maxwidth < namesize:
			maxwidth = namesize

		image = Image.new("RGBA", (40+(12*3)+maxwidth,40+(12*2)), backcol)
		pfp = Image.open(io.BytesIO(await user.display_avatar.read())).resize((40,40))

		mask = Image.open("assets/mask.png").convert("L").resize((40,40))
		newpfp = ImageOps.fit(pfp, (40,40), centering=(0.5, 0.5))
		newpfp.putalpha(mask)

		draw = ImageDraw.Draw(image)

		image.paste(newpfp, (12, 12), newpfp)
		draw.text((12+40+16, 9), name, font=fontbold, fill=(col.r, col.g, col.b))
		draw.text((12+40+namesize+24, 15), text="Today at " + time.strftime("%H:%M"), font=fontsmall, fill=alttextcol)
		draw.text((12+40+16, 33), text=text, font=font, fill=textcol)

		await sendImage(ctx, image)

def backtext(draw, x, y, text, gap, font):
	draw.text((x-gap, y), text, font=font, fill="black")
	draw.text((x+gap, y), text, font=font, fill="black")
	draw.text((x, y-gap), text, font=font, fill="black")
	draw.text((x, y+gap), text, font=font, fill="black")
	draw.text((x, y), text, font=font, fill="white")
	return draw

async def getImage(ctx):
	img = ""
	if len(ctx.message.attachments) > 0:
		img = await ctx.message.attachments[0].read()
	elif ctx.message.reference is not None:
		if ctx.message.reference.message_id:
			msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			if len(msg.attachments) > 0:
				img = await msg.attachments[0].read()
	else:
		img = await ctx.author.display_avatar.read()

	img = Image.open(io.BytesIO(img)).convert("RGBA")
	return img

async def sendImage(ctx, image):
	b = io.BytesIO()
	image.save(b, format="png")
	b.seek(0)
	await ctx.send(file=discord.File(b, "converted_image.png"))

def setup(client):
	client.add_cog(ImageCog(client))