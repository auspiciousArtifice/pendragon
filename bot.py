import discord
import threading
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pen = commands.Bot(command_prefix='$')

game_created = False
host = None
players = []
voting = threading.Lock()
questers = []
voted = []
votes = 0

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
        if player in players:
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

@pen.command(name='nominate', help='Nominates players towards current quest.')
async def nominate(ctx, *args):
    global game_created
    if(game_created):
        if(len(args) < 1):
            await ctx.send('Error: Need to nominate at least one player.')
            return
        if(len(args) > (current_quest.LENGTH - len(questers)) ):
            await ctx.send('Error: attempting to add too many players to quest.')
            return
        for quester in args: 
            if(quester in questers):
                await ctx.send('Error: one of these players have already been added to the quest.')
                return
            else:
                questers.append(quester)

@pen.command(name='startvote', help='Starts the voting for the current quest.')
async def startvote(ctx):
    global game_created
    if(game_created):
        if(len(questers) != current_quest.LENGTH):
            await ctx.send('Error: Not enough players to start quest.')
            return
        else:
            #move state to voting state
            #game logic loop here
            return

@pen.command(name='vote', help='Records responses for the current vote')
async def vote(ctx, *args):
    global game_created
    global voting
    global votes
    global voted
    await ctx.send('\'vote\' command called')
    if(game_created and voting):
        if(args):
            user_vote = args[0].lower()
        if(ctx.author in voted):
            await ctx.send('Error: you already voted!')
            return
        if(len(args) != 1):
            await ctx.send('Error: invalid number of arguments for \'vote\' command.')
            return
        if(user_vote is not 'yes' or user_vote is not 'no'):
            await ctx.send('Error: \'vote\' must be yes or no.')
            return 
        votes += check_user_vote(user_vote)
        voted.append(ctx.author)
        if(check_voted()):
            await ctx.send('Votes are done!')
            # delete vote command message by user
            # logic here for game loop
            # return vote_result()
            return
    else:
        pass #no vote in progress

async def check_user_vote(user_vote):
    #convert user_vote to enum
    #return Vote.PASS or Vote.FAIL
    pass

async def check_voted():
    global voting
    global voted
    global players
    voting.acquire()
    try:        
        if(len(voted) == len(players)): #everyone voted
            #Reset state back to original
            voted = 0 
            result = True #votes are done
        else:
            result = False #votes are still being taken
    finally:
        voting.release()
        return result

async def vote_result():
    global votes
    result = (votes > 0)
    votes = 0
    return result


pen.run(TOKEN)