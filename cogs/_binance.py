import binance
import discord
import requests
from discord.ext import commands


class Binance(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("Platinum Member")
    @commands.command()
    async def price(self, ctx, ticker="BTCUSDT"):
        ticker = ticker.upper()
        prices = binance.prices()
        if ticker not in prices:
            e = discord.Embed(title=ticker, description="Invalid Ticker Entered. Please try again.")
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title=ticker, description=f'Currently trading at: {prices[ticker]}')
            await ctx.send(embed=e)

    @commands.has_role("Platinum Member")
    @commands.command()
    async def hist(self, ctx, ticker="BTCUSDT", interval="12h"):
        ticker = ticker.upper()
        price = binance.tickers()
        if ticker not in price:
            e = discord.Embed(title=ticker, description="Invalid Ticker Entered. Please try again.")
            await ctx.send(embed=e)
        else:
            price = binance.prices()
            price = price[ticker]
            params = {"symbol": ticker}
            data = request("GET", "https://www.binance.com/api/v3/ticker/24hr", params=params)
            e = discord.Embed(title=ticker, description=f'Current trading price: {price}')
            e.add_field(name=f'24 Hour High:', value=data["highPrice"])
            e.add_field(name=f'24 Hour Low:', value=data["lowPrice"])
            await ctx.send(embed=e)


def request(method, path, params=None):
    resp = requests.request(method, path, params=params)
    return resp.json()


def setup(bot):
    bot.add_cog(Binance(bot))
