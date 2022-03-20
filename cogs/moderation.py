import discord
from discord.ext import commands
from discord.utils import get
import datetime

from functions import argsToTime, areyousure

class ModerationCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 3)
	async def kick(self, ctx, user:discord.Member=None, *, reason=None):
		if not ctx.channel.permissions_for(ctx.author).kick_members:
			return await ctx.send(f"You don't have permission scrubb :sunglasses: (Missing kick_members)")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if not ctx.channel.permissions_for(clientmember).kick_members:
			return await ctx.send(f"I don't have permissions noooooooo! (Missing kick_members)")
		if not user:
			return await ctx.send("Give me a name and I end their game.")
		
		if await areyousure(self.client, ctx, f"Are you sure you want to kick {user.display_name}?"):
			try:
				await ctx.guild.kick(user, reason=reason)
				await ctx.send(f"Kicked **{user.mention}**.")
			except:
				return await ctx.send(f"They're too good for me :(")

	@commands.command()
	@commands.cooldown(1, 3)
	async def ban(self, ctx, user:discord.Member=None, days:int=0, *, reason=None):
		if not ctx.channel.permissions_for(ctx.author).ban_members:
			return await ctx.send(f"You don't have permission scrubb :sunglasses: (Missing ban_members)")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if not ctx.channel.permissions_for(clientmember).ban_members:
			return await ctx.send(f"I don't have permissions noooooooo! (Missing ban_members)")
		if not user:
			return await ctx.send("Give me a name and I end their game. But this time they don't come back lol.")
		
		if await areyousure(self.client, ctx, f"Are you sure you want to ban {user.display_name}?"):
			try:
				await ctx.guild.ban(user, reason=reason, delete_message_days=days)
				await ctx.send(f"banned **{user.mention}**.")
			except:
				return await ctx.send(f"They're too good for me :(")

	@commands.command()
	@commands.cooldown(1, 3)
	async def slowmode(self, ctx, seconds:int=0):
		if not ctx.channel.permissions_for(ctx.author).moderate_members:
			return await ctx.send(f"Set the slowmode to 'nice try' seconds in {ctx.channel.mention}! (Missing moderate_members)")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if not ctx.channel.permissions_for(clientmember).manage_channels:
			return await ctx.send(f"I don't have permissions noooooooo! (Missing manage_channels)")

		await ctx.channel.edit(slowmode_delay=seconds)
		if seconds == 0:
			await ctx.send(f"Removed the slowmode in {ctx.channel.mention}!")
		else:
			await ctx.send(f"Set the slowmode to {seconds} seconds in {ctx.channel.mention}!")

	@commands.command()
	@commands.cooldown(1, 3)
	async def clear(self, ctx, limit:int=1):
		if not ctx.channel.permissions_for(ctx.author).manage_messages:
			return await ctx.send(f"Clear-ly you don't know how permissions work :| (Missing manage_messages)")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if not ctx.channel.permissions_for(clientmember).manage_messages:
			return await ctx.send(f"I don't have permissions noooooooo! (Missing manage_messages)")

		await ctx.channel.purge(limit=limit+1)

	@commands.command()
	@commands.cooldown(1, 3)
	async def timeout(self, ctx, user:discord.Member=None, *times):
		if not ctx.channel.permissions_for(ctx.author).moderate_members:
			return await ctx.send(f"How about you time out deez nuts. (Missing moderate_members)")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if not ctx.channel.permissions_for(clientmember).moderate_members:
			return await ctx.send(f"I don't have permissions noooooooo! (Missing moderate_members)")

		t, txt = argsToTime(times)
		time = datetime.datetime.now() + datetime.timedelta( seconds=t["s"], minutes=t["m"], hours=t["h"], days=t["d"] )
		await user.timeout(time)
		if txt == "":
			await ctx.send(f"Removed timeout for {user.mention}.")
		else:
			await ctx.send(f"Timed out {user.mention} for {txt}.")

	@commands.command()
	@commands.has_permissions(view_audit_log=True)
	@commands.cooldown(1, 5)
	async def auditbackup(self, ctx, limit:int=5, member:discord.Member=None):
		with open("temp.txt", "w", encoding="utf-8") as f:
			time = datetime.datetime.now().strftime("%d/%m/%Y at %H:%M")
			if member:
				f.write(f"Audit log enteries for {ctx.guild.name} done by {member.name} from before {time}. All times are in UTC.\n\n")
			else:
				f.write(f"Audit log enteries for {ctx.guild.name} from before {time}. All times are in UTC.\n\n")

			async for entry in ctx.guild.audit_logs(limit=limit, user=member):
				action, target, before, after = str(entry.action), entry.target, entry.before, entry.after

				# guild shit
				if action == "AuditLogAction.guild_update":
					f.write(f"- {entry.user} updated the server.")
					f.write(self.auditbackupchanges(entry))

				# channel shit
				elif action == "AuditLogAction.channel_create":
					f.write(f"- {entry.user} created a new {after.type} channel. #{after.name}")
				elif action == "AuditLogAction.channel_update":
					f.write(f"- {entry.user} updated a {before.type} channel. #{before.name}")
					f.write(self.auditbackupchanges(entry))
				elif action == "AuditLogAction.channel_delete":
					f.write(f"- {entry.user} deleted a {before.type} channel. #{before.name}")

				# channel permission shit
				elif action == "AuditLogAction.overwrite_create":
					f.write(f"- {entry.user} created new overwrites in #{target.name} for '{entry.extra.name}'.")
					f.write(self.auditbackupoverwrites(entry))
				elif action == "AuditLogAction.overwrite_update":
					f.write(f"- {entry.user} updated channel overwrites in #{target.name} for '{entry.extra.name}'.")
					f.write(self.auditbackupoverwrites(entry))
				elif action == "AuditLogAction.overwrite_delete":
					f.write(f"- {entry.user} deleted channel overwrites in #{target.name} for '{entry.extra.name}'.")
					f.write(self.auditbackupoverwrites(entry))

				# user shit
				elif action == "AuditLogAction.kick":
					f.write(f"- {target} was kicked.")
				elif action == "AuditLogAction.ban":
					f.write(f"- {target} was banned.")
				elif action == "AuditLogAction.unban":
					f.write(f"- {target} was unbanned.")
				elif action == "AuditLogAction.member_prune":
					f.write(f"- {entry.user} pruned {entry.extra.members_removed} members who didn't log in for a while.")
				elif action == "AuditLogAction.member_update":
					f.write(f"- {entry.user} updated {target}.")
					f.write(self.auditbackupchanges(entry))
				
				# role shit
				elif action == "AuditLogAction.role_create":
					f.write(f"- {entry.user} created a new role. @{after.name}")
				elif action == "AuditLogAction.role_update":
					f.write(f"- {entry.user} updated the @{before.name} role.")
					f.write(self.auditbackupchanges(entry))
				elif action == "AuditLogAction.role_delete":
					f.write(f"- {entry.user} deleted the @{before.name} role.")
				elif action == "AuditLogAction.member_role_update":
					f.write(f"- {entry.user} updated the roles of {target} (Exact roles coming soon).")

				# invite shit (update is basically useless)
				elif action == "AuditLogAction.invite_create":
					f.write(f"- {entry.user} created a new invite. {after.code}")
				elif action == "AuditLogAction.invite_delete":
					f.write(f"- {entry.user} deleted an invite. {before.code}")

				# emoji shit (I'll still call them emotes)
				elif action == "AuditLogAction.emoji_create":
					f.write(f"- {entry.user} created a new emote. :{after.name}:")
				elif action == "AuditLogAction.emoji_update":
					f.write(f"- {entry.user} updated the :{before.name}: emote.")
					f.write(self.auditbackupchanges(entry))
				elif action == "AuditLogAction.emoji_delete":
					f.write(f"- {entry.user} deleted the :{before.name}: emote.")

				# sticker shit
				elif action == "AuditLogAction.sticker_create":
					f.write(f"- {entry.user} created a new sticker. '{after.name}'")
				elif action == "AuditLogAction.sticker_update":
					f.write(f"- {entry.user} updated the '{before.name}' sticker.")
					f.write(self.auditbackupchanges(entry))
				elif action == "AuditLogAction.sticker_delete":
					f.write(f"- {entry.user} deleted the '{before.name}' sticker.")

				# other shit
				elif action == "AuditLogAction.bot_add":
					f.write(f"- {entry.user} added a new bot. {target}")

				else:
					f.write(f"- {entry.user} did {action} to {target}") # if all else fails, fall on ye olde reliable
					
				etime = entry.created_at.strftime("%d/%m/%Y at %H:%M")
				f.write(f"\n[ Created on {etime} ]\n\n")

		await ctx.channel.send(file=discord.File("temp.txt", "auditlogs.txt"))

	# get all the changes
	def auditbackupchanges(self, entry):
		changesafter = []
		changesbefore = []
		for change in entry.changes.after:
			if change[1] == None or type(change[1]) == str or type(change[1]) == int or type(change[1]) == bool:
				changesafter.append(change)
		for change in entry.changes.before:
			if change[1] == None or type(change[1]) == str or type(change[1]) == int or type(change[1]) == bool:
				changesbefore.append(change)

		txt = ""
		if len(changesafter) > 0:
			for i in range(0,len(changesafter)):
				txt += f" ({changesafter[i][0].capitalize()} changed from '{changesbefore[i][1]}' to '{changesafter[i][1]}')"
		return txt

	# for checking overwrite changes
	def auditbackupoverwrites(self, entry):
		try:
			for perm in entry.changes.after.allow:
				value = True
			for perm in entry.changes.after.deny:
				value = True
		except TypeError:
			return ""

		allows = []
		for perm in entry.changes.after.allow:
			if perm[1]:
				allows.append(perm[0])
		denys = []
		for perm in entry.changes.after.deny:
			if perm[1]:
				denys.append(perm[0])
		txt = "\n"
		if len(allows) > 0:
			txt += f"    - Allowed " + ", ".join(allows) + "\n"
		if len(denys) > 0:
			txt += f"    - Denied " + ", ".join(denys) + "\n"
		return txt[:-1]

def setup(client):
	client.add_cog(ModerationCog(client))