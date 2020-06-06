import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from pencog import PenCog

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')
bot.add_cog(PenCog(bot))
bot.run(TOKEN)
