import discord
from discord.ext import commands


class Misc(commands.Cog):
    """Miscellaneous minor commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def echo(self, ctx, content):
        await ctx.send(content)


def setup(bot):
    bot.add_cog(Misc(bot))
