from avalon import Session, GameState, Vote, Role
from discord.ext import commands

class PenCog(commands.Cog):
    def __init__(self, pen):
        self.pen = pen
        self.session = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.pen.user.name}')

    @commands.command(name='rules', help='Displays the rules of the game')
    async def rules(self, ctx):
        await ctx.send('Here is a link to the rules: https://tinyurl.com/ycf4jttk')

    @commands.command(name='debug')
    async def debug(self, ctx, arg):
        await ctx.send('\'debug\' command called')
        if self.session is not None:
            if arg is not None or arg is 'gamestate':
                await ctx.send('Current GameState is ' + self.session.get_state())
        else:
            await ctx.send('No session to debug.')

    @debug.error
    async def debug_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass #needs more than 0 arguments

    @commands.command(name='gather', help='Starts setup process for game, players can join once this command is executed')
    async def gather(self, ctx):
        author = str(ctx.author)
        await ctx.send('\'gather\' command called')
        await ctx.send(f'Now accepting players into {author}\'s game')
        self.session = Session(author)

    @commands.command(name='disband', help='Disbands current game session')
    async def disband(self, ctx):
        author = str(ctx.author)
        await ctx.send('\'disband\' command called')
        if author == self.session.get_host():
            await ctx.send(f'{author}\'s game has been disbanded')
            #This is fine for now because we have one game per bot for now. This will be changed once we have more games/sessions.
            self.session = None
        else:
            await ctx.send(f'{author}, you have not yet created a game session. Please use the \'gather\' command to create one.')

    @commands.command(name='begin', help='Begins game session if enough players have joined')
    async def begin(self, ctx):
        await ctx.send('\'begin\' command called')
        if self.session is not None:
            if self.session.start_game():
                await ctx.send(f'{self.session.get_host()}\'s game has begun!')
                for player in self.session.players:
                    role = self.session.players[player]
                    role_name = role.name.lower().replace('_', ' ')
                    if role == Role.GOOD_GUY:
                        role_name = 'a ' + role_name
                    elif role == Role.EVIL_GUY:
                        role_name = 'an ' + role_name
                    else:
                        role_name = role_name.capitalize()
                    await ctx.send(f'{player}, you are {role_name}')
                    if role == Role.MERLIN:
                        await ctx.send(f'The list of bad players (excluding Mordred) is {self.session.merlins_watch_list}')
                    if player in self.session.evil_watch_list:
                        other_evil_guys = list(self.session.evil_watch_list)
                        other_evil_guys.remove(player)
                        await ctx.send(f'The list of other bad players (excluding Oberon) is {other_evil_guys}')
            else:
                await ctx.send('Game could not be started')

    @commands.command(name='join', help='Adds user to current game session')
    async def join(self, ctx):
        await ctx.send('\'join\' command called')
        if not self.session is None:
            author = str(ctx.author)
            if not author in self.session.get_players():
                if self.session.add_player(author):
                    await ctx.send(f'{author} was successfully added to {self.session.get_host()}\'s game.')
                else:
                    await ctx.send(f'Game is already in session. Can not join {self.session.get_host()}\'s game.')
            else:
                await ctx.send(f'{author} is already in the game! Use the command $leave to leave the game.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'gather\' command to create one.')


    @commands.command(name='leave', help='Removes user from current game session')
    async def leave(self, ctx):
        await ctx.send('\'leave\' command called')
        author = str(ctx.author)
        if self.session is not None:
            if author == self.session.get_host():
                await ctx.send(f'{author} can\'t leave the game, as they are the host')
            elif author in self.session.get_players():
                if self.session.remove_player(author):
                    await ctx.send(f'{author} was successfully removed from {self.session.get_host()}\'s game.')
                else:
                    await ctx.send(f'Game is already in session. Can not join {self.session.get_host()}\'s game.')
            else:
                await ctx.send(f'{author} is not in the game! Use the command $join to join the game.')

    @commands.command(name='players', help='Lists the players in the current game session')
    async def players(self, ctx):
        await ctx.send('\'players\' command called')
        if self.session is not None:
            await ctx.send(str(list(self.session.get_players().keys())))
        else:
            await ctx.send('No game session created yet.')

    @commands.command(name='nominate', help='Nominates players towards current quest.')
    async def nominate(self, ctx, *args):
        if self.session is not None:
            if str(ctx.author) != self.session.get_king():
                await ctx.send('Error: Only the king can nominate playres.')
            elif len(args) < 1 :
                await ctx.send('Error: Need to nominate at least one player.')
            elif len(args) > (self.session.current_quest - len(self.session.questers)):
                await ctx.send('Error: attempting to add too many players to quest.')
            else:
                for quester in args:
                    if(quester in self.session.questers):
                        await ctx.send(f'Error: {quester} has already been added to the quest. Skipping.')
                    else:
                        self.session.questers.append(quester)

    @commands.command(name='startvote', help='Starts the voting for the current quest.')
    async def startvote(self, ctx):
        if self.session is not None :
            if len(self.session.questers) != self.session.current_quest :
                await ctx.send('Error: Not enough players to start quest.')
            else:
                self.session.change_state(GameState.TEAM_VOTE)
                #move state to voting state
                #game logic loop here

    @commands.command(name='vote', help='Records responses for the current vote')
    async def vote(self, ctx, *args):
        await ctx.send('\'vote\' command called')
        if self.session is not None and self.session.get_state == GameState.TEAM_VOTE:
            if args:
                user_vote = args[0].lower()
            if ctx.author in self.session.voted:
                await ctx.send('Error: you already voted!')
            elif len(args) != 1:
                await ctx.send('Error: invalid number of arguments for \'vote\' command.')
            elif user_vote is not 'yes' or user_vote is not 'yea' or user_vote is not 'nay' or user_vote is not 'no':
                await ctx.send('Error: \'vote\' must be yes or no.')
            else:
                self.session.votes += check_user_vote(user_vote)
                self.session.voted.append(ctx.author)
            if check_voted():
                await ctx.send('Votes are done!')
                # delete vote command message by user
                if(vote_result):
                    self.session.change_state(GameState.QUESTING)
                else:
                    self.session.change_state(GameState.NOMINATE) #from GameState.TEAM_VOTE
                    #TODO: implement King
                    #TODO: implement doom counter
        else:
            pass #no vote in progress

    async def check_user_vote(self, user_vote):
        if(user_vote == 'yes' or user_vote == 'yea'):
            return Vote.YEA
        else:
            return Vote.NAY

    async def check_voted(self):
        self.session.voting.acquire()
        try:
            if len(self.session.voted) == len(self.session.players): #everyone voted
                #Reset state back to original
                self.session.voted = 0
                result = True #votes are done
            else:
                result = False #votes are still being taken
        finally:
            self.session.voting.release()
            return result

    async def vote_result(self):
        result = (self.session.votes > 0)
        self.session.votes = 0
        return result
