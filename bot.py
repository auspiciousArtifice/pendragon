import discord
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print('Discord channel sent this message: ' + message.content)
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(TOKEN)