import atexit
import typing
from pathlib import Path
from os import path
from discord.ext import commands
from discord.embeds import Embed

from .kvstore import *
from .constants import *

"""
WIP: 
Figure out command groups
Figure out user information
Figure out global vs server tags
"""


class Tagging(commands.Cog):
    """Keyword tagging, WIP"""

    def __init__(self, bot):
        Path(IMAGES_PATH).mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).mkdir(parents=True, exist_ok=True)
        self.bot = bot
        self.lookup = DictKeyValueStore().load(path.join(DB_PATH, DB_FILENAME))
        self.usage = None  # TODO
        atexit.register(self.cleanup)

    @commands.command()
    async def create(self, ctx: commands.Context, *args):
        """
        Creates and links a tag to an image.
        Valid command formats:
            "z!create foo" with an attachment of an image named bar
            "z!create foo https://path.to/bar.png"
        """
        attachments = ctx.message.attachments
        if args and attachments:
            attachment = attachments[0]
            command_name = args[0]
            local_url = path.join(IMAGES_PATH, attachment.filename)
            await attachment.save(local_url)
            self.lookup[command_name] = TaggingItem(url=attachment.url,
                                                    local_url=local_url,
                                                    creator_id=ctx.message.author.id)
            await ctx.send(content='Successfully created ' + command_name + ' linked to ' + self.lookup[command_name].local_url)
        elif args:
            if len(args) >= 2:
                pass
                # TODO: sanitize and check that the second argument is an URL.
        else:
            await ctx.send('Usage: z!create <tag name: str> with an attachment')

    @commands.command()
    async def list(self, ctx):
        """Lists out all tags."""
        embed = Embed(title='List of Registered Tags')
        for k, v in self.lookup:
            creator = await self.bot.fetch_user(v.creator_id)
            embed = embed.add_field(name=k, value="[Link]({link})\nCreator: {creator}\nNumber of Times Used: {num}"
                                    .format(link=v.url, creator=creator.name, num=v.counter))
        await ctx.send(embed=embed)

    @commands.command()
    async def debug(self, ctx):
        """Used for debugging"""
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            words = self._parse_message(message)
            for word in words:
                if word in self.lookup:
                    await message.channel.send(embed=Embed().set_image(url=self.lookup.get(word).url))
                    self._mark_usage(message, word)
                    break  # only allow one match per message

    def cleanup(self):
        self.lookup.save(path.join(DB_PATH, DB_FILENAME))

    def _parse_message(self, message):
        return message.content.split(' ')

    def _mark_usage(self, message, word):
        self.lookup[word].counter += 1
        pass


