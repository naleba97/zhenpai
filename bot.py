import discord
from discord.ext import commands
import config

bot = commands.Bot(command_prefix='z!')

extensions = ['cogs.misc']

@bot.event
async def on_ready():
	print('Logged in as: ', bot.user)
	print('Discord.py version: ', discord.__version__)

@bot.event
async def on_message(message):
	await bot.process_commands(message)

if __name__ == '__main__':
	for ext in extensions:
		bot.load_extension(ext)
		print('Loaded extension: ', ext)

bot.run(config.bot_token)