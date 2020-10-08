import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from pencog import PenCog

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
# October 7th, 2020 - Discord mandated the use of intents to get member lists and statuses. The change broke the bot
# in the same day that development interest was revived. There was no notification of such a change given to developers
# to warn of the potential ramifications of said change. This fucked our shit up so badly for a few hours.
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

bot.add_cog(PenCog(bot))
bot.run(TOKEN)