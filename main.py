import re
import asyncio
import discord
import logging
import sqlite3
from datetime import datetime
from discord.utils import get
from discord.ext import commands, tasks
from telethon import TelegramClient, events, utils

# Create Loggings
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Start Telegram Listener
tclient = TelegramClient('Repeater', CLIENTID, 'CLIENT SECRET')
tclient.start()

# Declare Global Variables For cogs


# Connect to Database and create tables if they don't exist
conn = sqlite3.connect("db.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS channels (channel_name text)")
cur.execute("CREATE TABLE IF NOT EXISTS discord (dest bigint)")
cur.execute("CREATE TABLE IF NOT EXISTS translate (name_from text PRIMARY KEY, name_to text)")
cur.execute("CREATE TABLE IF NOT EXISTS strings (str_from text)")
cur.execute("CREATE TABLE IF NOT EXISTS bot (user_id int, date_time text)")
cur.execute("CREATE TABLE IF NOT EXISTS bot_trial (user_id int, time int)")
cur.execute("CREATE TABLE IF NOT EXISTS blacklist (user_id int)")
cur.execute("CREATE TABLE IF NOT EXISTS providers (channel_id int)")
conn.close()

# Announce Discord Bot Intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=".", description='Investing In Crypto Signals Bot', intents=intents)
bot.remove_command(name="help")

# Load Extensions
extensions = ['cogs.channels', 'cogs.utils', 'cogs._binance', 'cogs.strings']

for ext in extensions:
    bot.load_extension(ext)

oldcontent = ""
bot.channels = []
bot.translate = {}
bot.trials = {}
bot.trans = []
bot.subs = {}
bot.strings = []


@tasks.loop(minutes=5)
async def update():
    con = sqlite3.connect("db.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Update Trials.
    cur.execute("SELECT * from bot_trial")
    temps = cur.fetchall()
    bot.trial = dict(temps)

    # Retrieve Current Subs
    cur.execute("SELECT * from BOT")
    temp = cur.fetchall()
    bot.subs = dict(temp)

    # Update Translate.
    cur.execute('SELECT * FROM translate')
    temp = cur.fetchall()
    bot.translate = dict(temp)

    # Update Channels.
    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()
    cur.execute("SELECT * FROM channels")
    temp = cur.fetchall()
    bot.channels = list(temp)

    # Update Strings.
    cur.execute('SELECT * FROM strings')
    temp = cur.fetchall()
    bot.strings = list(temp)

    # Get Blacklist
    cur.execute("SELECT * FROM providers")
    temp = cur.fetchall()
    bot.providers = list(temp)

    # Remove Trials If Expired.
    now = datetime.now()
    expires = now.strftime("%H%M%S")
    for key, value in bot.trial.items():
        if int(expires) > int(value):
            guild = get(bot.guilds, id=123456789)
            role = get(guild.roles, id=123456789)
            member = get(guild.members, id=int(key))
            await member.remove_roles(role)

    # Remove Subs If Expired
    now = datetime.now()
    exp = now.strftime("%H%M%d%m%y")
    for key, value in bot.subs.items():
        if exp > value:
            guild = get(bot.guilds, id=123456789)
            role = get(guild.roles, id=123456789)
            member = get(guild.members, id=int(key))
            await member.remove_roles(role)


@update.before_loop
async def wait():
    await bot.wait_until_ready()

# UPDATE MEMBER COUNTS
@tasks.loop(minutes=10)
async def member_checker():
    guild = bot.get_guild(123456789)
    member_channel = guild.get_channel(123456789)
    mod_role = discord.utils.get(guild.roles, name="Moderator")
    mod_count = 0
    for member in guild.members:
        if mod_role in member.roles:
            if member.status != discord.Status.offline:
                mod_count += 1
    mod_channel = guild.get_channel(123456789)
    member_count = guild.member_count - mod_count
    await member_channel.edit(name=f'Members: {member_count}')
    await mod_channel.edit(name=f'Mods Online: {mod_count}')


@member_checker.before_loop
async def before_looping_occur():
    await bot.wait_until_ready()


# Tell user bot is Ready and print Channels
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Telegram Messages!'))
    print(f'Logged in as: {bot.user.name} - Exp0logy\'s Investing In Crypto Bot\nServer Started.')


async def replace(content):
    for x in bot.strings:
        if x in content:
            content = re.sub(x, "", content, flags=re.IGNORECASE)
            return content
    return content


@tclient.on(events.NewMessage)
async def my_event_handler(event):
    global oldcontent
    content = event.message.message
    chat_from = event.chat if event.chat else (await event.get_chat())  # telegram MAY not send the chat entity
    title = utils.get_display_name(chat_from)
    chat_id = utils.get_peer_id(chat_from)
    is_reply = event.is_reply
    is_photo = event.message.photo
    if chat_id in bot.providers:
        await tclient.forward_messages(-123456789, event.message)
        if is_reply:  # SEND REPLY
            reply_message = await event.get_reply_message()
            reply_text = reply_message.text
            reply_text = await replace(reply_text)
            e = discord.Embed(title=title, description=content)
            if len(reply_text) > 2:
                e.add_field(name='Original Message', value=reply_text)
            e.set_footer(text="Hosted and Coded By Azoria",
                            icon_url='https://cdn.discordapp.com/icons/830056678988447744'
                                    '/eb3b69c9f2556186c8f55db4e0e1403e.webp?size=128')
            channel = bot.get_channel(123456789)
            async with channel.typing():
                await channel.send(embed=e)
        if is_photo:  # SEND PHOTO
            await tclient.download_media(message=event.message, file='iic.jpg')
            file = discord.File("iic.jpg", filename="iic.png")
            e = discord.Embed(title=title, description=content)
            e.set_image(url="attachment://iic.jpg")
            e.set_footer(text="Hosted and Coded By Azoria",
                            icon_url="https://cdn.discordapp.com/icons/830056678988447744"
                                    "/eb3b69c9f2556186c8f55db4e0e1403e.webp?size=128")
            channel = bot.get_channel(123456789)
            async with channel.typing():
                await channel.send(file=file, embed=e)
        if not is_reply and not is_photo:  # SEND TEXT
            e = discord.Embed(title=title, description=content)
            e.set_footer(text="Hosted and Coded By Azoria",
                            icon_url="https://cdn.discordapp.com/icons/830056678988447744"
                                    "/eb3b69c9f2556186c8f55db4e0e1403e.webp?size=128")
            channel = bot.get_channel(123456789)
            async with channel.typing():
                await channel.send(embed=e)
    else:
        return

member_checker.start()
update.start()
bot.run("abcdefghijklmnopqrstuvwxyz123456789")
asyncio.get_event_loop().run_forever()
