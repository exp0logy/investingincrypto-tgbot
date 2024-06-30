import sqlite3
import discord
from discord.ext import commands


class Strings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def word(self, ctx):
        pass

    @word.command()
    async def add(self, ctx, *kwargs):
        args = " ".join(kwargs)
        insert = ("INSERT INTO strings VALUES ('{}')".format(args))
        conn = sqlite3.connect("db.db")
        cur = conn.cursor()
        cur.executescript(insert)
        conn.commit()
        conn.close()
        await ctx.reply("Successfully Added Phrase '{}'".format(args))


    @word.command()
    async def remove(self, ctx, *kwargs):
        args = " ".join(kwargs)
        remove = ("DELETE FROM strings WHERE str_from ='{}'".format(args))
        conn = sqlite3.connect("db.db")
        cur = conn.cursor()
        cur.executescript(remove)
        conn.commit()
        conn.close()
        await ctx.reply("Successfully Removed Phrase {}".format(args))

    @word.command()
    async def list(self, ctx):
        e = discord.Embed(title="Currently Replaced", description="\u200b")
        if len(self.bot.strings) == 0:
            e.add_field(name="No Values Registered!", value="\u200b", inline=False)
        else:
            strings = "\n".join(self.bot.strings)
            e.add_field(name="\u200b", value=strings, inline=False)
        e.set_footer(text="Hosted By Azoria",
                     icon_url="https://cdn.discordapp.com/icons/830056678988447744/eb3b69c9f2556186c8f55db4e0e1403e"
                              ".webp?size=128")
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Strings(bot))
