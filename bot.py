from cogs import webserver
from discord.ext import commands
import discord
import logging
import os

bot = commands.Bot(command_prefix='z!')

extensions = [
    'cogs.misc',
    'cogs.tagging',
    'cogs.twitcasting'
]


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    if ctx.cog:
        if commands.Cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
            return

    logger.warning('%s - %s', ctx.message.content, error)
    await ctx.send(f"{error}\nType `z!help` for usage details.")


@bot.event
async def on_ready():
    print('Logged in as: ', bot.user)
    print('Discord.py version: ', discord.__version__)


@bot.event
async def on_message(message):
    await bot.process_commands(message)

if __name__ == '__main__':
    logger = logging.getLogger('zhenpai')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='[%(asctime)s] %(name)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    for ext in extensions:
        bot.load_extension(ext)
        logger.debug('Loaded extension: %s', ext)

    webserver.start_server()

if os.environ.get('DISCORD_BOT_TOKEN'):
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
else:
    import config
    bot.run(config.bot_token)
