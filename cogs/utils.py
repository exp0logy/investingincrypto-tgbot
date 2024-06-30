import sqlite3
import time
import datetime
import discord
from discord.ext import commands


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def donate(self, ctx):
        e = discord.Embed(title="Donation/Subscription Details",
                          description="Any funds towards Server Development and Hosting are appreciated.")
        e.add_field(name="BTC (BSC):", value="0x39f404F34b1Af562514c97EfC54668B6A4F4d818", inline=False)
        e.add_field(name="ETH (ERC20):", value="0x39f404F34b1Af562514c97EfC54668B6A4F4d818", inline=False)
        e.add_field(name="USDT (ERC20):", value="0x39f404F34b1Af562514c97EfC54668B6A4F4d818", inline=False)
        e.add_field(name="BNB (BSC):", value="0x39f404F34b1Af562514c97EfC54668B6A4F4d818", inline=False)
        e.set_footer(text="Hosted and Coded By Azoria",
                     icon_url="https://cdn.discordapp.com/icons/830056678988447744/"
                              "eb3b69c9f2556186c8f55db4e0e1403e"".webp?size=128")
        await ctx.send(embed=e)

    @commands.command()
    @commands.has_role("Premium Member")
    async def trial(self, ctx):
        print(ctx.author.id)
        conn = sqlite3.connect("db.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * from bot_trial")
        temp = cur.fetchall()
        trials = dict(temp)
        print(trials)
        if ctx.author.id in trials:
            await ctx.reply("You have used your trial period.\nPlease run .subscribe to purchase Premium Bot Usage.")
        else:
            await ctx.reply("Trial is a one time offer and only claimable once. Agree? (Y/N)")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check)
            msg = msg.content
            if msg == "Y":
                now = datetime.now()
                current = now.strftime("%d/%m/%Y %H:%M:%S")
                insert = f"INSERT INTO bot_trial VALUES ('{ctx.author.id}', '{current}')"
                cur.executescript(insert)
                conn.commit()
                conn.close()
                bot_role = discord.utils.get(ctx.guild.roles, name="Platinum Member")
                user = ctx.guild.get_member(ctx.author.id)
                await user.add_roles(bot_role)
                await ctx.reply("Role Applied!\nPlease see #🚀-slacktoshi-bot-signals")
            else:
                await ctx.reply("Trial Cancelled")

    @commands.command()
    @commands.has_role("Premium Member")
    async def subscribe(self, ctx):
        await ctx.reply("You've Paid for 30 Days of Bot Premium\nTransactions are checked often, if you have not paid "
                        "and\n then subscribed you will be banned from using bot services. Agree? (Y/N)")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check)
        msg = msg.content
        if msg == "Y":
            await ctx.reply("Please Send Transaction ID:")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check)
            txnid = msg.content
            insert = f"INSERT INTO bot VALUES ('{datetime.datetime.now}', '{ctx.author.id}', '{txnid}')"
            conn = sqlite3.connect("db.db")
            cur = conn.cursor()
            cur.executescript(insert)
            conn.commit()
            conn.close()
            bot_role = discord.utils.get(ctx.guild.roles, name="Platinum Member")
            user = ctx.author.id
            await user.add_roles(bot_role)
            await ctx.reply("Role Applied!\nPlease see #🚀-slacktoshi-bot-signals")
            payments = discord.utils.get(ctx.guild.channels, name="haxbi-payments")
            await payments.send(
                f"@Haxbi\nNew Payment Made By '{ctx.author}'\nTXN ID:'{txnid}' At '{datetime.datetime.now}'")
        else:
            await ctx.reply("Transaction Cancelled.")

    @commands.group()
    @commands.has_role("Server Admin")
    async def util(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply("No Subcommand Parsed.\nAvailable Subcommands:\nOnline, Purge, Reload, Dest")

    @util.command()
    async def purge(self, ctx, num: int):
        if num is None:
            await ctx.reply("No Number Parsed. Please provide amount of messages to purge.")
        channel = ctx.channel
        await channel.purge(limit=num)
        time.sleep(1)
        msg = await ctx.send(f"Deleted {num} Messages")
        time.sleep(3)
        await msg.delete()


def setup(bot):
    bot.add_cog(Utilities(bot))
