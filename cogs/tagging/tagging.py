import atexit
import logging
import os
from pathlib import Path
from discord import File
from discord.ext import commands
from discord.embeds import Embed

from .kvstore import *
from .database import TaggingDatabase
from . import constants
from . import taggingutils

"""
WIP: 
Figure out command groups
Figure out user information
Figure out global vs server tags
"""


class Tagging(commands.Cog):
    """
    The Tagging cog allows users to associate a tag or keyword with a file, usually an image or gif.
    """

    def __init__(self, bot):
        if not os.path.exists(constants.KV_FOLDER_NAME):
            os.makedirs(constants.KV_FOLDER_NAME)
        if not os.path.exists(constants.IMAGES_FOLDER_NAME):
            os.makedirs(constants.IMAGES_FOLDER_NAME)

        self.logger = logging.getLogger('zhenpai.tagging')
        self.bot = bot
        self.lookup = DictKeyValueStore()
        # self.lookup = RedisKeyValueStore(ip='localhost', port=6379)
        self.usage = None  # TODO
        atexit.register(self.cleanup)

    @commands.group()
    async def tag(self, ctx):
        if ctx.invoked_subcommand is None:
            help_text = ""
            for command in self.walk_commands():
                if not isinstance(command, commands.Group) and not command.hidden:
                    help_text += f'{command}: {command.help}\n'
            await ctx.send(f'```{help_text}```')

    @tag.error
    async def on_command_error(self, ctx, error):
        self.logger.warning('%s - %s', ctx.message.content, error)
        await ctx.send(f"{error}\nType `z!tag help` for usage details.")

    @tag.command()
    async def create(self, ctx: commands.Context, tag_name: str, link: str = None):
        """
        Creates and links a tag to an file, usually an image, on a server.
            Usage: "z!create foo" with an attachment of an image named bar
                   "z!create foo https://path.to/bar.png"
        """
        attachments = ctx.message.attachments
        if tag_name and attachments:
            attachment = attachments[0]
            command_name = taggingutils.sanitize(tag_name)
            guild_id = ctx.guild.id
            key = taggingutils.create_kv_key(guild_id, command_name)
            server_path = path.join(constants.IMAGES_FOLDER_NAME, str(guild_id))
            Path(server_path).mkdir(parents=True, exist_ok=True)
            local_url = path.join(server_path, attachment.filename)
            await attachment.save(local_url)
            self.logger.info("Saved image to %s", local_url)
            self.lookup[key] = TaggingItem(name=command_name,
                                           url=attachment.url,
                                           local_url=local_url,
                                           creator_id=ctx.message.author.id)
            self.lookup.save()
            await ctx.send(
                content='Successfully created ' + command_name + ' linked to ' + self.lookup[key].local_url)
            self.logger.info('Successfully created %s linked to %s', command_name, self.lookup[key].local_url)
        elif tag_name and link:
            pass
            # TODO: sanitize and check that the second argument is an URL.
        else:
            await ctx.send(f'```{ctx.command.help}```')

    @tag.command()
    async def list(self, ctx):
        """
        Lists out all tags belonging to a server.
            Usage: "z!tag list"
        """
        embed = Embed(title='List of Registered Tags')
        if isinstance(self.lookup, DictKeyValueStore):
            for k, v in self.lookup.get_paged(server_id=str(ctx.guild.id)).items():
                creator = self.bot.get_user(int(v.creator_id))
                embed = embed.add_field(name='--------------------------------',
                                        value=f"[{v.name}]({v.url})\nBy: {creator.name}",
                                        inline=False)
        elif isinstance(self.lookup, RedisKeyValueStore):
            cursor, keys = self.lookup.get_paged(server_id=ctx.guild.id)
            for k in keys:
                v = self.lookup[k]
                creator = self.bot.get_user(int(v.creator_id))
                embed = embed.add_field(name='--------------------------------',
                                        value=f"[{v.name}]({v.url})\nBy: {creator.name}",
                                        inline=False)
        await ctx.send(embed=embed)

    @tag.command()
    async def delete(self, ctx: commands.Context, *args):
        """
        Deletes tags from the server.
            Usage: "z!tag delete <tag-name1> <tag-name2> ..."
        """
        for tag_name in args:
            key = taggingutils.create_kv_key(ctx.guild.id, tag_name)
            if self.lookup.delete(key):
                await ctx.send(f'Deleted tag: `{tag_name}`')
            else:
                await ctx.send(f'Could not find tag: `{tag_name}`')
            self.lookup.save()
    
    @tag.command(hidden=True)
    async def debug(self, ctx):
        """Used for debugging"""
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            words = taggingutils.parse_message(message)
            for word in words:
                word = taggingutils.sanitize(word)
                key = taggingutils.create_kv_key(message.guild.id, word)
                if key in self.lookup:
                    embed_dict = {
                        'image': {'url': self.lookup[key].url}
                    }
                    embed = Embed.from_dict(embed_dict)
                    await message.channel.send(embed=embed)
                    # await message.channel.send(file=File(self.lookup[key].local_url))
                    self.mark_usage(key)
                    break  # only allow one match per message

    def mark_usage(self, tag):
        pass

    def cleanup(self):
        self.lookup.save()
