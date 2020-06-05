import discord
import os
from avalon import Session, GameState, Vote
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pen = commands.Bot(command_prefix='$')

voting = threading.Lock()
questers = []
voted = []
votes = 0
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
        #This is fine for now because we have one game per bot for now. This will be changed once we have more games/sessions.
        session = None 
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
        elif author in session.get_players():
            session.remove_player(author)
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

@pen.command(name='nominate', help='Nominates players towards current quest.')
async def nominate(ctx, *args):
    if(session is not None):
        if(len(args) < 1):
            await ctx.send('Error: Need to nominate at least one player.')
            return
        if(len(args) > (session.current_quest - len(session.questers)) ):
            await ctx.send('Error: attempting to add too many players to quest.')
            return
        for quester in args:
            if(quester in session.questers):
                await ctx.send('Error: one of these players have already been added to the quest.')
                return
            else:
                session.questers.append(quester)

@pen.command(name='startvote', help='Starts the voting for the current quest.')
async def startvote(ctx):
    if(session is not None):
        if(len(session.questers) != session.current_quest):
            await ctx.send('Error: Not enough players to start quest.')
            return
        else:
            session.change_state(GameState.TEAM_VOTE)
            #move state to voting state
            #game logic loop here
            return

@pen.command(name='vote', help='Records responses for the current vote')
async def vote(ctx, *args):
    await ctx.send('\'vote\' command called')
    if(session is not None and session.get_state == GameState.TEAM_VOTE):
        if(args):
            user_vote = args[0].lower()
        if(ctx.author in session.voted):
            await ctx.send('Error: you already voted!')
            return
        if(len(args) != 1):
            await ctx.send('Error: invalid number of arguments for \'vote\' command.')
            return
        if(user_vote is not 'yes' or user_vote is not 'yea' or user_vote is not 'nay' or user_vote is not 'no'):
            await ctx.send('Error: \'vote\' must be yes or no.')
            return
        session.votes += check_user_vote(user_vote)
        session.voted.append(ctx.author)
        if(check_voted()):
            await ctx.send('Votes are done!')
            # delete vote command message by user
            if(vote_result):
                session.change_state(GameState.QUESTING)
            else:
                session.change_state(GameState.NOMINATE) #from GameState.TEAM_VOTE
                #implement King
                #implement doom counter
            return
    else:
        pass #no vote in progress

async def check_user_vote(user_vote):
    if(user_vote == 'yes' or user_vote == 'yea'):
        return Vote.YEA
    else:
        return Vote.NAY

async def check_voted():
    session.voting.acquire()
    try:
        if(len(session.voted) == len(session.players)): #everyone voted
            #Reset state back to original
            session.voted = 0
            result = True #votes are done
        else:
            result = False #votes are still being taken
    finally:
        session.voting.release()
        return result

async def vote_result():
    result = (votes > 0)
    session.votes = 0
    return result


pen.run(TOKEN)