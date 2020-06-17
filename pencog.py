from avalon import Session, GameState, Vote, Role
from discord.ext import commands

class PenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user.name}')

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
            elif args[0] == 'nominated' or args[0] == 'questers':
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
            elif args[0] == 'voted' or args[0] == 'voters':
                await ctx.send(f'Current voters are {self.session.get_voted()}')
                print(f'Current voters are {self.session.get_voted()}')
            elif args[0] == 'votes':
                await ctx.send(f'Current vote total is {self.session.get_votes()}')
                print(f'Current vote count is {self.session.get_votes()}')
            elif args[0] == 'quest':
                await ctx.send(f'Current quest result is {self.session.get_quest_result()}')
                print(f'Current quest result is {self.session.get_quest_result()}')
            elif args[0] == 'turn':
                await ctx.send(f'Current turn is {self.session.get_turn()}')
                print(f'Current turn is {self.session.get_turn()}')
            elif args[0] == 'set_role':
                #self.session.set_questers_required(Roles[args[1]])
                pass
            elif args[0] == 'dummies' and self.session.get_state() == GameState.CREATED:
                for i in range(0, int(args[1])):
                    self.session.add_player(f'{731+i}')
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
        author_id = int(ctx.author.id)
        await ctx.send('\'gather\' command called')
        await ctx.send(f'Now accepting players into {ctx.author.name}\'s game')
        self.session = Session(author_id)
        self.session.add_player(author_id)

    @commands.command(name='disband', help='Disbands current game session')
    async def disband(self, ctx):
        author = int(ctx.author.id)
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

    @commands.command(name='percival', help='Toggles whether Percival should be added or not. Off by default')
    async def percival(self, ctx):
        await ctx.send('\'percival\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                self.session.toggle_percival()
                await ctx.send('Percival is now '+('removed','added')[self.session.get_add_percival()])
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add/remove Percival.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='morgana', help='Toggles whether Morgana should be added or not. Off by default')
    async def morgana(self, ctx):
        await ctx.send('\'morgana\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                self.session.toggle_morgana()
                await ctx.send('Morgana is now '+('removed','added')[self.session.get_add_morgana()])
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add/remove Morgana.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='mordred', help='Toggles whether Mordred should be added or not. Off by default')
    async def mordred(self, ctx):
        await ctx.send('\'mordred\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                self.session.toggle_mordred()
                await ctx.send('Mordred is now '+('removed','added')[self.session.get_add_mordred()])
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add/remove Mordred.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='oberon', help='Toggles whether Oberon should be added or not. Off by default')
    async def oberon(self, ctx):
        await ctx.send('\'oberon\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                self.session.toggle_oberon()
                await ctx.send('Oberon is now '+('removed','added')[self.session.get_add_oberon()])
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add/remove Oberon.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='lancelot', help='Toggles whether Lancelots should be added or not. Off by default')
    async def lancelot(self, ctx):
        await ctx.send('\'lancelot\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                self.session.toggle_lancelot()
                await ctx.send('Lancelots are now '+('removed','added')[self.session.get_add_lancelot()])
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add/remove Lancelots.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='all_roles', help='Puts all roles into the game. Note: 1 villain role must be removed')
    async def all_roles(self, ctx):
        await ctx.send('\'all_roles\' called')
        if self.session:
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                if not self.session.get_add_percival():
                    self.session.toggle_percival()
                if not self.session.get_add_morgana():
                    self.session.toggle_morgana()
                if not self.session.get_add_mordred():
                    self.session.toggle_mordred()
                if not self.session.get_add_oberon():
                    self.session.toggle_oberon()
                if not self.session.get_add_lancelot():
                    self.session.toggle_lancelot()
                await ctx.send('All roles are added. Please remove roles as there will be too many villains.')
                self.session.joining.release()
            else:
                await ctx.send('You are not the host! You can\'t add all special roles.')
        else:
            await ctx.send('Session hasn\'t been created yet! Use the \'$gather\' command to create one.')

    @commands.command(name='begin', help='Begins game session if enough players have joined')
    async def begin(self, ctx):
        await ctx.send('\'begin\' command called')
        if self.session:
            host = ctx.guild.get_member(self.session.get_host())
            if(ctx.author.id == self.session.get_host()):
                self.session.joining.acquire()
                try:
                    if self.session.start_game():
                        await ctx.send(f'{host.name}\'s game has begun!')
                        await self.turn(ctx)
                        for player in self.session.get_players():
                            player_role = player[1] # gets role
                            if player_role == Role.MERLIN:
                                m_list = []
                                for p in self.session.get_players():
                                    if self.session.get_role(p[0]).value < -1:
                                        m_list.append(p[0])
                                await ctx.send(f'{player[0]}, here are the list of evil player(s) you can see: {m_list}')
                            elif player_role.value < 0 and player_role.value != Role.EVIL_LANCELOT:
                                e_list = []
                                for p in self.session.get_players():
                                    if self.session.get_role(p[0]).value < 0 and p != player:
                                        e_list.append(p[0])
                                await ctx.send(f'{player[0]}, here are the other villain(s): {e_list}')
                            elif player_role == Role.PERCIVAL:
                                p_list = []
                                for p in self.session.get_players():
                                    if abs(self.session.get_role(p[0]).value) == 2:
                                        p_list.append(p[0])
                                if len(p_list) == 1:
                                    await ctx.send(f'{player[0]}, {p_list[0]} is Merlin')
                                elif len(p_list) == 2:
                                    await ctx.send(f'{player[0]}, one of these 2 is Merlin: {p_list}')
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
        author = int(ctx.author.id)
        if self.session:
            host = ctx.guild.get_member(self.session.get_host())
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


    @commands.command(name='leave', help='Removes user from current game session')
    async def leave(self, ctx):
        await ctx.send('\'leave\' command called')
        author = int(ctx.author.id)
        if self.session:
            host = ctx.guild.get_member(self.session.get_host())
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
        author = int(ctx.author.id)
        if len(args) < 1:
            await ctx.send('Error: need more arguments to kick players.')
            return
        if self.session:
            host = ctx.guild.get_member(self.session.get_host())
            if self.session.get_state() == GameState.CREATED:
                self.session.joining.acquire()
                try:
                    player = await commands.UserConverter().convert(ctx, str(args[0])) # Converts mention so have to use UserConverter
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
                player_user = ctx.guild.get_member(player[0])
                player_list += f'{player_user.name}\n' 
            await ctx.send(player_list)
        else:
            await ctx.send('No game session created yet.')

    @commands.command(name='nominate', help='Nominates players towards current quest.')
    async def nominate(self, ctx, *args):
        if self.session:
            if self.session.get_state() == GameState.NOMINATE:
                if ctx.author.id != self.session.get_king():
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
                        try:
                            quester = await commands.UserConverter().convert(ctx, str(quester)) # Converts mention so have to use UserConverter
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

    @commands.command(name='remove', help='Remove players from current quest.')
    async def remove(self, ctx, *args):
        if self.session:
            if self.session.get_state() == GameState.NOMINATE:
                if ctx.author.id != self.session.get_king():
                    await ctx.send('You are not the king! You cannot remove.')
                    return
                if len(args) < 1 :
                    await ctx.send('Error: Need to remove at least one player.')
                    return
                if len(args) > len(self.session.get_questers()):
                    await ctx.send('Error: attempting to remove too many players from quest.')
                    return
                else:
                    for quester in args:
                        self.session.nominating.acquire()
                        try:
                            quester = await commands.UserConverter().convert(ctx, str(quester)) # Converts mention so have to use UserConverter
                            if self.session.remove_quester(quester.id):
                                await ctx.send(f'Removed {quester.name} from quest.')
                            else:
                                await ctx.send(f'Error: could not remove {quester.name} from quest.')
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
                if self.session.get_king() == ctx.author.id:
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
                    player_user = ctx.guild.get_member(self.session.get_players()[i][0])
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
                    player_user = await commands.UserConverter().convert(ctx, str(args[0])) # Converts mention so have to use UserConverter
                    role = self.session.use_lady(player_user.id)
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
    async def vote(self, ctx, *args):
        await ctx.send('\'vote\' command called')
        if len(args) > 1:
            await ctx.send('Error: too many arguments for vote command.')
        if self.session:
            if not self.session.get_player(ctx.author.id):
                await ctx.send('Error: you are not in this game!')
                return
            if self.session.get_state() == GameState.TEAM_VOTE:
                if args[0]:
                    user_vote = args[0].lower()
                if self.session.get_voter(ctx.author.id):
                    await ctx.send('Error: you already voted!')
                    return
                user_vote = self.session.check_user_vote(user_vote)
                if user_vote is None:
                    await ctx.send('Error: invalid vote string.')
                    return
                self.session.voting.acquire()
                try:
                    self.session.set_votes(self.session.get_votes() + user_vote.value)
                    self.session.get_voted().append(ctx.author.id)
                    if self.session.check_voted():
                        await ctx.send('Votes are done!')
                        if(self.session.vote_result()):
                            await ctx.send('Vote passes. :)')
                            await self.questing(ctx)
                        else:
                            if(self.session.get_doom_counter() == 5):
                                await ctx.send('Doom counter is 5, vote passes anyway.')
                                await self.questing(ctx)
                            else:
                                await ctx.send('Vote fails. :(')
                                self.session.increment_doom_counter()
                                self.session.set_state(GameState.NOMINATE) #from GameState.TEAM_VOTE
                        self.session.increment_turn()
                        await self.turn(ctx)
                finally:
                    self.session.voting.release()
            else:
                await ctx.send('No voting in progress.')
        else:
            pass #No game in progress, deliberate separation for no message

    async def questing(self, ctx):
        self.session.set_state(GameState.QUESTING)
        quest = await self.start_quest(ctx)
        if(quest[0]):
            await ctx.send('Quest passes. :)')
            self.session.increment_quest_passed()
        else:
            await ctx.send(f'Quest fails... by {quest[1]} fails. :(')
            self.session.increment_quest_failed()
        if self.session.get_quests_passed() >= 3:
            self.last_stand(ctx)
        elif self.session.get_quests_failed() >= 3:
            self.game_over(ctx, False) # Bad guys win
        else:
            self.session.increment_current_quest()
            self.session.set_doom_counter(0)
            self.session.set_state(GameState.NOMINATE)

    async def start_quest(self, ctx):
        for quester in self.session.get_questers():
            self.session.questing.acquire()
            try:
                await self.quest_action(ctx, quester)
            finally:
                self.session.questing.release()
        quest_tuple = (self.session.check_quest(), self.session.get_quest_result())
        return quest_tuple

    @commands.Cog.listener()
    async def quest_action(self, ctx, quester):

        member = ctx.guild.get_member(quester)        
        await member.send('Add that 👍 or 👎 reaction to this message.')

        def check(reaction, user):
            return user == member and str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if reaction.emoji == '👎':
                self.session.set_quest_result(self.session.get_quest_result() - 1)
                #TODO: delete DM message with their reaction... or maybe not?
            await member.send('I\'ve recorded your response. 👍')
        except Exception as e:
            print(e)

    @vote.error
    async def vote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print('Error: vote command received no arguments.') #needs only 1 argument
        if isinstance(error, commands.TooManyArguments):
            print('Error: vote command received too many arguments.') #needs only 1 argument
        else:
            print(error)

    async def last_stand(self, ctx):
        self.session.set_state(GameState.LAST_STAND)
        await ctx.send('One last chance for the bad guys to win. Assassinate Merlin!')

    @commands.command(name='assassinate', help='Assassinates a player. Intended for Merlin.')
    async def assassinate(self, ctx, *args):
        if self.session:
            if len(args) != 1:
                await ctx.send('Insufficient number of arguments. Please target 1 player.')
            elif self.session.get_state() == GameState.LAST_STAND:
                role = self.session.get_role(ctx.author.id) 
                if role == Role.ASSASSIN:
                    target = ctx.guild.get_member(int(args[0]))
                    if assassinate(target):
                        await ctx.send(f'The assassination attempt succeeded!')
                        await self.game_over(ctx, False)
                    else:
                        merlin = self.session.get_merlin()
                        merlin_player = ctx.guild.get_member(int(merlin[0]))
                        await ctx.send(f'The assassination attempt failed! {merlin_player} is Merlin!')
                        await self.game_over(ctx, True)
                else:
                    await ctx.send(f'You are not the assassin!')
            else:
                await ctx.send(f'We are not on the last stand!')
        else:
            pass #No game in progress, deliberate separation for no message
    
    @assassinate.error
    async def assassinate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            print('Error: vote command received no arguments.') #needs only 1 argument
        if isinstance(error, commands.TooManyArguments):
            print('Error: vote command received too many arguments.') #needs only 1 argument
        else:
            print(error)

    async def game_over(self, ctx, allegiance):
        self.session.set_state(GameState.GAME_OVER)
        await ctx.send(('Good','Bad')[allegiance] + 'guys win!') # ternary for printing out result of game
        await ctx.send('Game over!')
        #TODO: dispose session properly