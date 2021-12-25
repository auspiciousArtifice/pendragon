import discord
import os
import logging
from discord.ext import commands
from dotenv import load_dotenv
from pencog import PenCog

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# October 7th, 2020 - Discord mandated the use of intents to get member lists and statuses. The change broke the bot
# in the same day that development interest was revived. There was no notification of such a change given to developers
# to warn of the potential ramifications of said change. This fucked our shit up so badly for a few hours.
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
bot.add_cog(PenCog(bot))
bot.run(TOKEN)