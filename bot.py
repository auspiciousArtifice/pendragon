import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

@bot.command(name='gather', help='Starts setup process for game, players can join once this command is executed')
async def gather(ctx):
    await ctx.send('\'gather\' command called')

@bot.command(name='begin', help='Begins game session if enough players have joined')
async def begin(ctx):
    await ctx.send('\'begin\' command called')

@bot.command(name='join', help='Adds user to current game session')
async def join(ctx):
    await ctx.send('\'join\' command called')

@bot.command(name='unjoin', help='Removes user from current game session')
async def unjoin(ctx):
    await ctx.send('\'unjoin\' command called')

bot.run(TOKEN)