import discord
import os
from avalon import Session
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pen = commands.Bot(command_prefix='$')

session = None

@pen.event
async def on_ready():
    print(f'We have logged in as {pen.user.name}')

@pen.command(name='rules', help='Displays the rules of the game')
async def rules(ctx):
    await ctx.send('Here is a link to the rules: https://tinyurl.com/ycf4jttk')

@pen.command(name='gather', help='Starts setup process for game, players can join once this command is executed')
async def gather(ctx):
    global session
    author = str(ctx.author)
    await ctx.send('\'gather\' command called')
    await ctx.send(f'Now accepting players into {author}\'s game')
    session = Session(author)

@pen.command(name='disband', help='Disbands current game session')
async def disband(ctx):
    global session
    author = str(ctx.author)
    await ctx.send('\'disband\' command called')
    if author == session.get_host():
        await ctx.send(f'{author}\'s game has been disbanded')
    else:
        await ctx.send(f'{author}, you have not yet created a game session. Please use the \'gather\' command to create one.')

@pen.command(name='begin', help='Begins game session if enough players have joined')
async def begin(ctx):
    await ctx.send('\'begin\' command called')
    # TODO: Implement state transition of session to PICK_QUEST if session exists

@pen.command(name='join', help='Adds user to current game session')
async def join(ctx):
    global session
    await ctx.send('\'join\' command called')
    if not session is None:
        player = str(ctx.author)
        if not player in session.get_players():
            session.add_player(player)
        else:
            await ctx.send(f'{player} is already in the game! Use the command $leave to leave the game.')
    else:
        await ctx.send('Session hasn\'t been created yet! Use the \'gather\' command to create one.')


@pen.command(name='leave', help='Removes user from current game session')
async def unjoin(ctx):
    global session
    await ctx.send('\'leave\' command called')
    author = str(ctx.author)
    if not session is None:
        if author == session.get_host():
            await ctx.send(f'{author} can\'t leave the game, as they are the host')
        elif author in players:
            players.remove(author)
        else:
            await ctx.send(f'{author} is not in the game! Use the command $join to join the game.')

@pen.command(name='players', help='Lists the players in the current game session')
async def players(ctx):
    global session
    await ctx.send('\'players\' command called')
    if not session is None:
        await ctx.send(str(session.get_players()))
    else:
        await ctx.send('No game session created yet.')

pen.run(TOKEN)