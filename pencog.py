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
    async def debug(self, ctx, *args):
        await ctx.send('\'debug\' command called')
        #await ctx.send(self.session)
        #print(self.session)
        print(args)
        if self.session:
            if args[0] == 'gamestate':
                await ctx.send(f'Current GameState is {self.session.get_state().name}')
                print(f'Current GameState is {self.session.get_state().name}')
            elif args[0] == 'players':
                await ctx.send(f'Current players are {self.session.get_players()}')
                print(f'Current players are {self.session.get_players()}')
            elif args[0] == 'nominated':
                await ctx.send(f'Current questers nominated are {self.session.get_questers()}')
                print(f'Current questers nominated are {self.session.get_questers()}')
            elif args[0] == 'host':
                await ctx.send(f'Current host is {self.session.get_host()}')
                print(f'Current host is {self.session.get_host()}')
            elif args[0] == 'king':
                await ctx.send(f'Current king is {self.session.get_king()}')
                print(f'Current host is {self.session.get_king()}')
            elif args[0] == 'set_questers_required':
                self.session.set_questers_required(int(args[1]))
            elif args[0] == 'set_role':
                #self.session.set_questers_required(Roles[args[1]])
                pass
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
        #TODO: Mutex needed here to bind to text channel
        author_id = str(ctx.author.id)
        await ctx.send('\'gather\' command called')
        await ctx.send(f'Now accepting players into {ctx.author.name}\'s game')
        self.session = Session(author_id)
        self.session.add_player(author_id)

    @commands.command(name='disband', help='Disbands current game session')
    async def disband(self, ctx):
        author = str(ctx.author.id)
        await ctx.send('\'disband\' command called')
        if self.session:
            if author == self.session.get_host():
                await ctx.send(f'{ctx.author.name}\'s game has been disbanded')
                #This is fine for now because we have one game per bot for now. This will be changed once we have more games/sessions.
                self.session = None
            else:
                await ctx.send(f'{ctx.author.name}, you have not yet created a game session. Please use the \'gather\' command to create one.')
        else:
            await ctx.send('No session to disband! Use the \'$gather\' command to create one.')

    @commands.command(name='begin', help='Begins game session if enough players have joined')
    async def begin(self, ctx):
        await ctx.send('\'begin\' command called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                try:
                    if self.session.start_game():
                        await ctx.send(f'{self.session.get_host()}\'s game has begun!')
                    else:
                        await ctx.send('Game could not be started')
                finally:
                    self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t start the game.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='join', help='Adds user to current game session')
    async def join(self, ctx):
        await ctx.send('\'join\' command called')
        author = str(ctx.author.id)
        if self.session:
            host = await commands.UserConverter().convert(self.session.get_host())
            self.session.joining.acquire()
            try:
                if self.session.get_player(author) is None:
                    if self.session.add_player(author):
                        await ctx.send(f'{ctx.author.name} was successfully added to {host.name}\'s game.')
                    else:
                        await ctx.send(f'Game is already in session. Can not join {host.name}\'s game.')
                else:
                    await ctx.send(f'{ctx.author.name} is already in the game! Use the command $leave to leave the game.')
            finally:
                self.session.joining.release()
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')


    @commands.command(name='leave', help='Removes self from current game session')
    async def unjoin(self, ctx):
        await ctx.send('\'leave\' command called')
        author = str(ctx.author.id)
        if self.session:
            host = await commands.UserConverter().convert(self.session.get_host())
            self.session.joining.acquire()
            try:
                if author == self.session.get_host():
                    await ctx.send(f'{ctx.author.name} can\'t leave the game, as they are the host.')
                elif self.session.get_player(author):
                    if self.session.remove_player(author):
                        await ctx.send(f'{ctx.author.name} was successfully removed from {host.name}\'s game.')
                    else:
                        await ctx.send(f'Can not leave {host.name}\'s game.')
                else:
                    await ctx.send(f'{ctx.author.name} is not in the game! Use the command $join to join the game.')
            finally:
                self.session.joining.release()
        else:
            pass #No game in progress, deliberate separation for no message

    @commands.command(name='kick', help='Removes user from current game session')
    async def kick(self, ctx, *args):
        await ctx.send('\'kick\' command called')
        author = str(ctx.author.id)
        if len(args) < 1:
            await ctx.send('Error: need more arguments to kick players.')
            return
        if self.session:
            print(args[0])
            host = await commands.UserConverter().convert(self.session.get_host())
            if self.session.get_state() == GameState.CREATED:
                self.session.joining.acquire()
                try:
                    player = await commands.MemberConverter().convert(ctx, args[0])
                    if self.session.get_host() == player.id:
                        await ctx.send('Error: Cannot kick host. Use the disband command instead.')
                        return
                    elif author == self.session.get_host():
                        if self.session.get_player(player.id):
                            if self.session.remove_player(player.id):
                                await ctx.send(f'{player.name} was successfully removed from {host.name}\'s game.')
                            else:
                                await ctx.send(f'Can not kick {player.name} from {host.name}\'s game.')
                        else:
                            await ctx.send(f'Could not find {player.name} in session.')
                    else:
                        await ctx.send(f'{host.name} is not the host! Cannot kick {player.name}.')
                finally:
                    self.session.joining.release()
            else:
                await ctx.send('Cannot kick anyone after the game has started.')
        else:
            pass #No game in progress, deliberate separation for no message


    @commands.command(name='players', help='Lists the players in the current game session')
    async def players(self, ctx):
        await ctx.send('\'players\' command called')
        if self.session:
            player_list = ''
            for player in self.session.get_players():
                player_user = await commands.UserConverter().convert(player[0])
                player_list += f'{player_user.name}\n' 
            await ctx.send(player_list)
        else:
            await ctx.send('No game session created yet.')

    @commands.command(name='nominate', help='Nominates players towards current quest.')
    async def nominate(self, ctx, *args):
        if self.session:
            if self.session.get_state() == GameState.NOMINATE:
                if ctx.author.id != self.session.get_king()[0]:
                    await ctx.send('You are not the king! You cannot nominate.')
                    return
                if len(args) < 1 :
                    await ctx.send('Error: Need to nominate at least one player.')
                    return
                if len(args) > (self.session.get_questers_required() - len(self.session.get_questers())):
                    await ctx.send('Error: attempting to add too many players to quest.')
                    return
                else:
                    for quester in args:
                        self.session.nominating.acquire()
                        print(quester) #DEBUG: remove later
                        try:
                            quester = await commands.MemberConverter().convert(ctx, quester)
                            print(quester.id)
                            if self.session.add_quester(quester.id):
                                await ctx.send(f'Added {quester.name} to quest.')
                            else:
                                await ctx.send(f'Error: could not add {quester.name} to quest.')
                        finally:
                            self.session.nominating.release()
            else:
                await ctx.send('We are currently not picking any players for the quest!')
        else:
            pass #No game in progress, deliberate separation for no message

    @commands.command(name='startvote', help='Starts the voting for the current quest.')
    async def startvote(self, ctx):
        if self.session:
            if self.session.get_state() == GameState.NOMINATE:
                if self.session.get_king()[0] == ctx.author.id:
                    if self.session.get_questers_required() == len(self.session.get_questers()):
                        self.session.set_state(GameState.TEAM_VOTE)
                        await ctx.send('Enough players have been nominated. Voting starts now.')
                    else:
                        await ctx.send('Not enough players to start vote.')
                else:
                    await ctx.send('Error: you cannot start the vote unless you are the King.')
            else:
                await ctx.send('We are currently not picking any players for the quest!')
        else:
            pass #No game in progress, deliberate separation for no message

    @commands.command(name='turn', help='Shows the current turn and turn order.')
    async def turn(self, ctx):
        if self.session:
            if self.session.get_state() != GameState.CREATED:
                current_turn = self.session.get_turn()
                player_order = ''
                for i in range(0, self.session.get_num_players()):
                    player_user = await commands.UserConverter().convert(self.session.get_players()[i][0])
                    if i != current_turn:
                        player_order += f'{player_user.name}\n'
                    else:
                        player_order += f'{player_user.name} <- current turn\n'
                await ctx.send(player_order)
            else:
                await ctx.send('Game hasn\'t started yet. No turn order yet.')
        else:
            pass #No game in progress, deliberate separation for no message

    @commands.command(name='lady', help='Uses the Lady of the Lake to reveal an allegiance.')
    async def lady(self, ctx, *args):
        #No mutex needed here because of almost idempotence... probably :)
        await ctx.send('\'lady\' command called')
        if self.session:
            if len(args) != 1:
                    await ctx.send('Error: invalid number of arguments for \'lady\' command.')
            elif self.session.get_state() == GameState.NOMINATE:
                if self.session.get_lady() == ctx.author.id:
                    player_user = await commands.UserConverter().convert(args[0])
                    role = self.session.get_player(args[0])[1]
                    if role:
                        lady_message = f'{player_user.name} is '
                        lady_message += 'Evil' if role.value <= 0 else 'Good'
                        await ctx.message.author.send(lady_message)
                        self.session.set_lady(player_user.id)
                    else:
                        await ctx.send(f'Error: could not get allegiance of {player_user.name}')
                else:
                    await ctx.send('Error: you do not have the Lady of the Lake.')
        else:
            pass #No game in progress, deliberate separation for no message

    @commands.command(name='vote', help='Records responses for the current vote')
    async def vote(self, ctx, *arg):
        await ctx.send('\'vote\' command called')
        if self.session:
            if self.session.get_state() == GameState.TEAM_VOTE:
                if arg:
                    user_vote = arg.lower()
                if self.session.get_voter(ctx.author.id):
                    await ctx.send('Error: you already voted!')
                user_vote = self.session.check_user_vote(user_vote)
                if user_vote is None:
                    await ctx.send('Error: invalid vote string.')
                    return
                self.session.voting.acquire()
                try:
                    self.session.votes += user_vote
                    self.session.get_voted().append(ctx.author.id)
                    if self.session.check_voted():
                        await ctx.send('Votes are done!')
                        # delete vote command message by user
                        if(self.vote_result()):
                            await ctx.send('Vote passes.')
                            self.session.set_state(GameState.QUESTING)
                            self.session.set_doom_counter(0)
                        else:
                            if(self.session.get_doom_counter() == 5):
                                await ctx.send('Doom counter is 5, vote passes anyway.')
                                self.session.set_state(GameState.QUESTING)
                                self.session.set_doom_counter(0)
                            else:
                                await ctx.send('Vote fails.')
                                self.session.set_state(GameState.NOMINATE) #from GameState.TEAM_VOTE
                                self.session.increment_turn()
                                self.session.increment_doom_counter()
                finally:
                    self.session.voting.release()
            else:
                ctx.send('No voting in progress.')
        else:
            pass #No game in progress, deliberate separation for no message

    @vote.error
    async def debug_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print('Error: vote command received no arguments.') #needs only 1 argument
        if isinstance(error, commands.TooManyArguments):
            print('Error: vote command received too many arguments.') #needs only 1 argument
        else:
            print(error)