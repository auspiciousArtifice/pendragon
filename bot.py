import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pen = commands.Bot(command_prefix='$')

game_created = False
host = None
players = []

@pen.event
async def on_ready():
    print(f'We have logged in as {pen.user.name}')

@pen.command(name='rules', help='Displays the rules of the game')
async def rules(ctx):
    await ctx.send('Here is a link to the rules: https://tinyurl.com/ycf4jttk')

@pen.command(name='gather', help='Starts setup process for game, players can join once this command is executed')
async def gather(ctx):
    author = str(ctx.author)
    await ctx.send('\'gather\' command called')
    await ctx.send(f'Now accepting players into {author}\'s game')
    game_created = True
    host = author
    players = [author]

@pen.command(name='begin', help='Begins game session if enough players have joined')
async def begin(ctx):
    await ctx.send('\'begin\' command called')

@pen.command(name='join', help='Adds user to current game session')
async def join(ctx):
    await ctx.send('\'join\' command called')
    if game_created:
        player = str(ctx.author)
        if not player in players:
            players.append(player)
        else:
            await ctx.send(f'{player} is already in the game! Use the command $leave to leave the game.')


@pen.command(name='leave', help='Removes user from current game session')
async def unjoin(ctx):
    await ctx.send('\'leave\' command called')
    author = str(ctx.author)
    if game_created and not author == host:
        if author in players:
            players.remove(author)
        else:
            await ctx.send(f'{author} is not in the game! Use the command $join to join the game.')
    elif game_created and author == host:
        await ctx.send(f'{author} can\'t leave the game, as they are the host')

@pen.command(name='players', help='Lists the players in the current game session')
async def players(ctx):
    await ctx.send('\'players\' command called')
    if game_created:
        await ctx.send(str(players))
    else:
        await ctx.send('No game session created yet.')

pen.run(TOKEN)