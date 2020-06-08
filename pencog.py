from avalon import Session, GameState, Vote
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
        #await ctx.send(self.session)
        #print(self.session)
        print(arg)
        if self.session is not None:
            if arg == 'gamestate':
                await ctx.send(f'Current GameState is {self.session.get_state().name}')
                print(f'Current GameState is {self.session.get_state().name}')
            elif arg == 'players':
                await ctx.send(f'Current players are {self.session.get_players()}')
                print(f'Current players are {self.session.get_players()}')
            else:
                print('Error: Invalid argument.')
        else:
            await ctx.send('No session to debug.')

    @debug.error
    async def debug_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass #needs more than 0 arguments
        else:
            print(error)

    @commands.command(name='gather', help='Starts setup process for game, players can join once this command is executed')
    async def gather(self, ctx):
        author = str(ctx.author)
        await ctx.send('\'gather\' command called')
        await ctx.send(f'Now accepting players into {author}\'s game')
        self.session = Session(author)
        session.add_player(author)

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
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')


    @commands.command(name='leave', help='Removes user from current game session')
    async def unjoin(self, ctx):
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
        if(self.session is not None):
            if len(args) < 1 :
                await ctx.send('Error: Need to nominate at least one player.')
            if len(args) > (self.session.get_questers_required() - len(self.session.get_questers())):
                await ctx.send('Error: attempting to add too many players to quest.')
            for quester in args:
                if not self.session.add_quester(quester):
                    await ctx.send('Error: one of these players have already been added to the quest.')
            if self.session.get_questers_required() == len(self.session.get_questers()):
                #mutex again
                self.session.change_state(GameState.TEAM_VOTE)

    @commands.command(name='startvote', help='Starts the voting for the current quest.')
    async def startvote(self, ctx):
        if self.session.get_state() == GameState.NOMINATE:
            if(len(self.session.get_questers()) != self.session.get_current_quest()):
                await ctx.send('Error: Not enough players to start quest.')
            else:
                self.session.change_state(GameState.TEAM_VOTE)

    @commands.command(name='turn', help='Shows the current turn and turn order.')
    async def turn(self, ctx):
        if(self.session is not None):
            current_turn = self.session.get_turn()
            player_order = ''
            for i in range(0, self.session.get_num_players()):
                if i != current_turn:
                    player_order += f'{self.session.get_players()[i][0]}'
                else:
                    player_order += f'{self.session.get_players()[i][0]} <- current turn'
            await ctx.send(player_order)

    @commands.command(name='lady', help='Uses the Lady of the Lake to reveal an allegiance.')
    async def lady(self, ctx, args):
        await ctx.send('\'lady\' command called')
        if(len(args) != 1):
                await ctx.send('Error: invalid number of arguments for \'lady\' command.')
        elif (self.session is not None and self.session.get_state == GameState.NOMINATE):
            if self.session.get_lady() == ctx.author:
                #message ctx.author the allegiance of args[0]
                self.session.set_lady(args[0])

    @commands.command(name='vote', help='Records responses for the current vote')
    async def vote(self, ctx, *args):
        await ctx.send('\'vote\' command called')
        if(self.session is not None and self.session.get_state == GameState.TEAM_VOTE):
            if(args):
                user_vote = args[0].lower()
            if(ctx.author in self.session.voted):
                await ctx.send('Error: you already voted!')
            if(len(args) != 1):
                await ctx.send('Error: invalid number of arguments for \'vote\' command.')
            if(user_vote is not 'yes' or user_vote is not 'yea' or user_vote is not 'nay' or user_vote is not 'no'):
                await ctx.send('Error: \'vote\' must be yes or no.')
            self.session.votes += self.session.check_user_vote(user_vote)
            self.session.get_voted().append(ctx.author)
            if(self.session.check_voted()):
                await ctx.send('Votes are done!')
                # delete vote command message by user
                if(self.vote_result()):
                    await ctx.send('Vote passes.')
                    self.session.change_state(GameState.QUESTING)
                    self.session.set_doom_counter(0)
                else:
                    if(self.session.get_doom_counter() == 5):
                        await ctx.send('Doom counter is 5, vote passes anyway.')
                        self.session.change_state(GameState.QUESTING)
                        self.session.set_doom_counter(0)
                    else:
                        await ctx.send('Vote fails.')
                        self.session.change_state(GameState.NOMINATE) #from GameState.TEAM_VOTE
                        self.session.increment_turn()
                        self.session.increment_doom_counter()


    