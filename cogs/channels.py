import sqlite3

import discord
from discord.ext import commands


class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_role("Server Admin")
    async def channel(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply("No subcommand supplied.")

    @channel.command()
    async def add(self, ctx, chatId):
        insert = ("INSERT INTO providers VALUES ('{}')".format(chatId))
        conn = sqlite3.connect("db.db")
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()
        cur.executescript(insert)
        conn.commit()
        conn.close()
        await ctx.send("Successfully Added '{}'".format(chatId))

    @channel.command()
    async def remove(self, ctx, chatId):
        remove = ("DELETE FROM providers WHERE channel_id =('{}')".format(chatId))
        conn = sqlite3.connect("db.db")
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()
        cur.executescript(remove)
        conn.commit()
        conn.close()
        await ctx.send("Successfully Removed {}".format(chatId))


    @channel.command()
    async def list(self, ctx):
        ch_list = self.bot.providers
        if len(ch_list) == 0:
            e = discord.Embed(title="Currently Monitored Channels",
                              description="No Channels Registered!")
        else:
            e = discord.Embed(title="Currently Monitored Channels",
                              description=ch_list)
        e.set_footer(text="Hosted By Azoria",
                     icon_url="https://cdn.discordapp.com/icons/830056678988447744/eb3b69c9f2556186c8f55db4e0e1403e.webp?size=128")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Channels(bot))
