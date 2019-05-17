import discord
import os
import random
from discord.ext import commands
import logging

logging.basicConfig(level=logging.DEBUG)
bot = commands.Bot(command_prefix='>')
bot.remove_command('help')

class AnonUser:
  id = None
  color = discord.Color(int("%06x" % random.randint(0, 0xFFFFFF), 16))
  alias = None
  blacklisted = False

anon_users = []
past_messages = []

anon_channel = 549005138581389333
rel_channel = 546410155793973249
serious_channel = 546392923093336094

def get_user(identifier):
  for u in anon_users:
    if u.id == identifier:
      return u
  for j in anon_users:
    if j.alias == identifier:
      return j

def create_user(ctx):
  poss_id = random.randint(0, 999)
  if len(anon_users) > 999:
    poss_id = len(anon_users) + 1
  while any(x.alias == poss_id for x in anon_users):
    poss_id = random.randint(0, 999)
  if get_user(ctx.message.author.id) == None:
    user = AnonUser()
    user.id = ctx.message.author.id
    anon_users.insert(0, user)
  get_user(ctx.message.author.id).alias = poss_id
  get_user(ctx.message.author.id).color = discord.Color(int("%06x" % random.randint(0, 0xFFFFFF), 16))

def grab(ctx):
  if get_user(ctx.message.author.id) == None:
    create_user(ctx)
  user = get_user(ctx.message.author.id)
  return user

@bot.command()
async def help(ctx):
  embed = discord.Embed(title = "boundlessbot help", color = discord.Color.red())
  embed.add_field(name = ">ping", value = "pong")
  embed.add_field(name = ">newid", value = "select a new alias for speaking anonymously")
  embed.add_field(name = ">set_color <hex>", value = "select the color for your embeds when speaking with the bot")
  embed.add_field(name = ">anon <message>", value = "send <message> to #anonymous under your id")
  embed.add_field(name = ">rel <message>", value = "send <message> to #relationships under your id. alternate commmand `>relationships <message>`")
  embed.add_field(name = ">serious <message>", value = "send <message> to #serious under your id")
  embed.add_field(name = ">message <id> <message>", value = "send <message> to another anon user with id <id>")
  embed.add_field(name = ">blacklist <message id>", value = "blacklist a user, <message id> being the discord id of a message sent by the anon user you wish to blacklist")
  embed.add_field(name = ">unblacklist <message id>", value = "unblacklist a user, <message id> being the discord id of a message sent by the anon user you wish to unblacklist")
  await bot.get_user(ctx.message.author.id).send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def newid(ctx):
  user = grab(ctx)
  if user.blacklisted == False:
    create_user(ctx)
    await ctx.send('you are now speaking under id ' + str(get_user(ctx.message.author.id).alias))
  else:
    await ctx.send('you are blacklisted')

@bot.command()
async def set_color(ctx, arg: str):
  user = grab(ctx)
  if user.blacklisted == False:
    user.color = discord.Colour(int(arg.replace('#', ''), 16))
    embed = discord.Embed(color = user.color)
    embed.add_field(name = user.alias, value='color set')
    await ctx.send(embed=embed)
  else:
    await ctx.send("you are blacklisted")

@bot.command()
async def anon(ctx, message):
  text = ctx.message.content
  await send_message(ctx, text[5:len(text)], anon_channel)

@bot.command()
async def rel(ctx, message):
  text = ctx.message.content
  await send_message(ctx, text[4:len(text)], rel_channel)

@bot.command()
async def relationships(ctx, message):
  text = ctx.message.content
  await send_message(ctx, text[14:len(text)], rel_channel)
  
@bot.command()
async def serious(ctx, message):
  text = ctx.message.content
  await send_message(ctx, text[8:len(text)], serious_channel)

async def send_message(ctx, message, channel):
  user = grab(ctx)
  if user.blacklisted == False:
    embed = discord.Embed(color = user.color)
    embed.add_field(name = user.alias, value = message)
    await bot.get_channel(channel).send(embed=embed)
    past_messages.insert(0, [bot.get_channel(channel).last_message_id, user])
  else:
    await ctx.send("you are blacklisted")

@bot.command()
async def message(ctx, id: int, *message):
  user = grab(ctx)
  if user.blacklisted == False:
    recipient = get_user(id)
    embed = discord.Embed(color = user.color)
    embed.add_field(name = user.alias, value = (" ".join(message)))
    await bot.get_user(get_user(id).id).send(embed=embed)
  else:
    await ctx.send("you are blacklisted")

@bot.command()
async def blacklist(ctx, message_id: str):
  if ctx.message.author.guild_permissions.kick_members:
    for x in past_messages:
      if x[0] == int(message_id):
        x[1].blacklisted = True
        await ctx.send(str(x[1].alias) + " was blacklisted")
  else:
    await ctx.send("only mods may use blacklist")

@bot.command()
async def unblacklist(ctx, message_id: str):
  if ctx.message.author.guild_permissions.kick_members:
    for x in past_messages:
      if x[0] == int(message_id):
        x[1].blacklisted = False
        await ctx.send(str(x[1].alias) + " was unblacklisted")
  else:
    await ctx.send("only mods may use unblacklist")

bot.run(os.getenv("TOKEN"))
