import discord
from discord.ext import commands

from .kvstore import *

"""
WIP: 
Figure out command groups
Figure out user information
Figure out global vs server tags
"""


class Tagging(commands.Cog):
    """Keyword tagging, WIP"""

    def __init__(self, bot):
        self.bot = bot
        self.lookup = DictKeyValueStore()
        self.usage = None  # TODO

    @commands.command()
    async def create(self, ctx):
        """Creates a new tag"""
        await ctx.send('tagging.create called')

    @commands.command()
    async def list(self, ctx):
        """Lists out all tags."""
        await ctx.send('tagging.list called')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            words = self._parse_message(message)
            for word in words:
                if word in self.lookup:
                    await message.channel.send(self.lookup.get(word))
                    self._mark_usage(message, word)
                    break  # only allow one match per message

    def _parse_message(self, message):
        return message.content.split(' ')

    def _mark_usage(self, message, word):
        pass
