import random
import json
from enum import Enum
from threading import Lock

class GameState(Enum):
    CREATED = 0     # Game made, players can join and leave, game start goes to NOMINATE
    NOMINATE = 1    # 'King' nominates team for current quest, goes to TEAM_VOTE
    TEAM_VOTE = 2   # Everyone votes on nominated team, if pass go to QUESTING, else go back to NOMINATE
    QUESTING = 3    # Nominated team chooses to pass/fail quest, if 3 quests passed, goes to LAST_STAND, else NOMINATE
    LAST_STAND = 4  # Assassin chooses player to kill, bad guys win if Merlin is killed
    GAME_OVER = 5   # Can view stats from game, goes back to CREATED if wants new players else NOMINATE

class Vote(Enum):
    NAY = -1
    YEA = 1

class Role(Enum):
    '''
    Enum that represents the role of a player. Good guys have positive values, bad guys have non-positive values.

    More details provided in comments of the class.
    '''

    # Good Guy Roles (value > 0)
    GOOD_LANCELOT = 4
    PERCIVAL = 3    # Knows who Merlin is (if Morgana is in play, can't tell between Merlin and Morgana)
    MERLIN = 2      # Knows all bad guys (except Oberon and Mordred if in play)
    GOOD_GUY = 1    # No special properties
    # Bad Guy Roles (value <= 0)
    OBERON = 0      # Unknown to Merlin AND bad guys
    MORDRED = -1    # Unknown to Merlin
    MORGANA = -2    # Appears to be Merlin to Percival
    ASSASSIN = -3   # Has chance to kill Merlin if 3 quests pass
    EVIL_LANCELOT = -4
    EVIL_GUY = -5   # No special properties

    # Simplified conditions for role checks
    # if player_role.value < -1 # Used by Merlin, reveals bad guys (except Mordred and Oberon if in play)
    # if player_role.value < 0 # Used by bad guys, reveals bad guys (except Oberon if in play)
    # if player_role.value > 0 # Good, unused (for good reason)
    # if abs(player_role.value) == 2 # Used by Percival, reveals Merlin (and Morgana if in play)

class Session:
    def __init__(self, host=None):
        self.host = int(host)
        self.players = []
        self.joining = Lock()

        self.__king = None
        self.__lady = None
        self.__turn = 0
        self.state = GameState.CREATED

        self.quests_passed  = 0
        self.quests_failed = 0
        self.current_quest = 0
        self.double_fail = False
        self.quest_result = 0
        self.questing = Lock()

        self.questers_required = 0
        self.questers = []
        self.nominating = Lock()
        self.doom_counter = 0

        self.votes = 0
        self.voted = []
        self.voting = Lock()
        self.merlins_watch_list= []
        self.evil_watch_list = []
        self.add_percival = False
        self.add_morgana = False
        self.add_mordred = False
        self.add_oberon = False
        self.add_lancelot = False
        self.lancelot_swaps = []
        self.settings = [] # Settings will change based on # of players after game starts
        with open('settings.json') as json_file:
            self.settings = json.load(json_file)['game_configs'] # Currently sets settings to all settings in settings.json

    class Player:
        def __init__(self, name=None, id=None, role=None):
            self.Name = name
            self.id = id
            self.Role = role
        def __repr__(self) -> str:
            return f"{{Name: {self.Name}, ID: {self.id}, Role: {self.Role}}}"

    @property
    def turn(self):
        return self.__turn % len(self.players)

    @turn.setter
    def turn(self, turn_num):
        self.__turn = turn_num

    @property
    def lady(self):
        return self.lady

    @lady.setter
    def lady(self, player_id):
        self.__lady = int(player_id)

    @property
    def king(self):
        return self.__king

    @king.setter
    def king(self, player_id):
        self.__king = int(player_id)

    def get_player(self, id):
        '''
        Retrieves Player object via player_id.
        '''
        id = int(id)
        for i in range(0, len(self.players)):
            # player_id = int(self.players[i][0])
            # if player_id == id:
            #     return self.players[i]
            player_id = self.players[i].id
            if player_id == id:
                return self.players[i]
        return None

    def get_merlin(self):
        '''
        Retrieves Player object representing Merlin.
        '''
        for i in range(0, len(self.players)):
            role = self.players[i].role
            if role == Role.MERLIN:
                return self.players[i]
        return None

    def get_role(self, player_id):
        '''
        Retrieves player's role via player_id.
        '''
        return self.get_player(player_id).role

    def set_role(self, player_id, player_role):
        '''
        Sets player's role by provided player_id and role.
        '''
        player_id = int(player_id)
        # for i in range(0, len(self.players)):
        #     player_id = int(self.players[i][0])
        #     if player_id == id:
        #         self.players[i] = (id, role)
        current_player = self.get_player(player_id)
        if current_player is not None:
            current_player.role = player_role

    def num_players(self):
        '''
        Returns number of players in game.
        '''
        return len(self.players)

    def toggle_percival(self):
        self.add_percival = not self.add_percival

    def toggle_morgana(self):
        self.add_morgana = not self.add_morgana

    def toggle_mordred(self):
        self.add_mordred = not self.add_mordred

    def toggle_oberon(self):
        self.add_oberon = not self.add_oberon

    def toggle_lancelot(self):
        self.add_lancelot = not self.add_lancelot

    # DEBUG: Unneccessary function due to next_quest() - Shamee
    # def pass_quest(self):
    #     self.quests_passed += 1

    # DEBUG: Unneccessary function due to next_quest() - Shamee
    # def fail_quest(self):
    #     self.quests_failed += 1

    # DEBUG: Unneccessary function due to next_quest() - Shamee
    # Don't think this is necessary given the next_quest() function
    # def increment_current_quest(self):
    #     self.current_quest += 1
    #     self.questers_required = self.settings[f'Q{self.current_quest+1}']

    def next_quest(self, passed):
        '''
        Receives the result of the current quest, and increments the quest counter.
        Also increments the quests passed or quests failed counters.
        Also sets the number of questers required for the next quest from the settings.
        '''
        if passed:
            self.quests_passed += 1
        else:
            self.quests_failed += 1
        self.current_quest += 1
        self.questers_required = self.settings[f'Q{self.current_quest+1}']

    def reset_doom_counter(self):
        '''
        Resets the doom counter to 0.
        '''
        self.doom_counter = 0

    def increment_doom_counter(self):
        '''
        Increments the doom counter by 1.
        '''
        self.doom_counter += 1

    def increment_turn(self):
        '''
        Increments the turn counter.
        Also sets the new king (turn leader),
        as well as empties the voted and questers array,
        and sets the votes back to 0.
        '''
        self.turn += 1
        self.king = self.players[self.turn].id
        self.voted = []
        self.questers = []
        self.votes = 0

    def check_vote_result(self):
        '''
        Returns true if the vote passed.
        Returns false if the vote failed.
        (Breaking even in a vote is a fail.)
        '''
        return self.votes > 0

    def check_user_vote(self, user_vote):
        '''
        Checks the user's vote string to see if it's a valid vote.
        Returns Vote.YEA if it is a yes vote.
        Returns Vote.NAY if it is a no vote.
        Returns None if the string is not valid.
        '''
        if(user_vote == 'yes' or user_vote == 'yea' or user_vote == 'y'):
            return Vote.YEA
        elif(user_vote == 'no' or user_vote == 'nay' or user_vote == 'n'):
            return Vote.NAY
        else:
            return None

    def check_if_voted(self, player_id):
        '''
        Returns if player already voted. 
        True means the player has already voted. 
        False means the player has not voted yet.
        '''
        return player_id in self.voted

    def tally_votes(self):
        '''
        Returns True if all players have voted.
        Returns False otherwise.
        '''
        return len(self.voted) == len(self.players) # True == Everyone Voted

    def add_player(self, player_id):
        '''
        Adds player to game with player id.
        Returns true if successful, and false otherwise.
        Will fail on duplicates.
        '''
        if self.state == GameState.CREATED:
            if self.get_player(player_id) is None:
                # TODO: Add player name to arguments - Shamee
                player = self.Player('', player_id)
                self.players.append(player)
                return True
        return False
    
    def add_player(self, player_id, player_name):
        '''
        Adds player to game with player id and player name.
        Returns true if successful, and false otherwise.
        Will fail on duplicates.
        '''
        if self.state == GameState.CREATED:
            if self.get_player(player_id) is None:
                # print(player_name)
                # print(player_id)
                player = self.Player(player_name, player_id)
                # print(player, player_name, player_id)
                self.players.append(player)
                return True
        return False

    def add_dummy(self, dummy_id):
        dummy_id = int(dummy_id)
        if self.state == GameState.CREATED:
            dummy_player = self.Player('Dummy', dummy_id)
            self.players.append(dummy_player)
        else:
            print('Game state is not \'Created\'')

    def remove_player(self, player_id):
        '''
        Removes player from game.
        '''
        if self.state == GameState.CREATED:
            for i in range(0, len(self.players)):
                if int(self.players[i].id) == int(player_id):
                    del self.players[i]
                    return True
        return False

    def add_quester(self, player_id):
        '''
        Adds a quester based on a player id.
        Returns true if successful, and false otherwise.
        Will fail on duplicates.
        '''
        player_id = int(player_id)
        if self.state == GameState.NOMINATE:
            if self.get_player(player_id):
                quester = int(player_id) in self.questers
                if not quester:
                    self.questers.append(player_id)
                    return True
        return False

    def dummy_questers(self):
        # TODO: test this function - Shamee
        if self.state == GameState.NOMINATE:
            while len(self.questers) < self.questers_required:
                self.questers.append(self.players[-1].id)
        else:
            return False

    def remove_quester(self, player_id):
        '''
        Removes a quester based on a player id.
        Returns true if successful, and false otherwise.
        '''
        if self.state == GameState.NOMINATE:
            for i in range(0, len(self.questers)):
                if self.questers[i] == int(player_id):
                    del self.questers[i]
                    return True
        return False

    def start_voting(self):
        '''
        Starts voting if the number of questers is
        the same as the number required.
        '''
        if self.questers_required == len(self.questers):
            self.state = GameState.TEAM_VOTE
            return True
        else:
            return False

    # def add_voter(self, player_id):
    #     if self.state == GameState.TEAM_VOTE:
    #         voted = int(player_id) in self.voted
    #         if not voted:
    #             self.voted.append(int(player_id))
    #             return True
    #     return False

    def add_voter(self, player_id, player_vote):
        '''
        Adds a player to the voted list and adds their
        player vote for the current nomination to the votes total.
        '''
        if self.state == GameState.TEAM_VOTE:
            if not self.check_if_voted(player_id):
                self.voted.append(int(player_id))
                self.votes = self.votes + player_vote.value
                return True
        return False

    # TODO: This function will literally never be used. 
    # Why do we even need it? - Shamee    
    # def remove_voter(self, player_id):
    #     if self.state == GameState.TEAM_VOTE:
    #         for i in range(0, len(self.voted)):
    #             if self.voted[i] == player_id:
    #                 del self.voted[i]
    #                 return True
    #     return False

    def use_lady(self, player_id):
        '''
        Invokes the Lady of the Lake to reveal a player's allegiance.
        '''
        if self.state == GameState.NOMINATE:
            return self.get_player(int(player_id)).role > 0

    def decrement_quest_result(self):
        '''
        Adds a fail to the quest counter.
        Will fail quest if too many fails are added.
        '''
        self.quest_result = self.quest_result - 1

    def check_quest(self):
        '''
        Returns result of quest. 
        True means quest passed.
        False means quest failed.
        '''
        result = self.quest_result
        if self.current_quest == 3:
            self.double_fail = self.settings['DF']
        if self.double_fail:
            return not result <= -2
        else:
            return not result <= -1

    def start_game(self):
        '''
        Begins the game.
        Sets state to NOMINATE.
        Sets default settings according to number of players in game.
        Sets roles based on selected settings.
        '''
        if self.state == GameState.CREATED:
            if not str(len(self.players)) in self.settings:
                return False
            game_settings = self.settings[str(len(self.players))]
            # TODO: Put all the role assignments and shuffling in their own functions! - Shamee
            total_evil_replacement = self.add_morgana + self.add_mordred + self.add_oberon + self.add_lancelot
            if game_settings['EVIL']-1 < total_evil_replacement:
                return False
            # After game starts
            good_roles = [Role.MERLIN]
            evil_roles = [Role.ASSASSIN]
            for i in range(1, game_settings['GOOD']):
                good_roles.append(Role.GOOD_GUY)
            for i in range(1, game_settings['EVIL']):
                evil_roles.append(Role.EVIL_GUY)
            # Increments position in list every time a replacement happens (based on toggles)
            counter = 1
            if self.add_percival:
                good_roles[counter] = Role.PERCIVAL
                counter += 1
            if self.add_lancelot:
                good_roles[counter] = Role.GOOD_LANCELOT
                self.lancelot_swaps = [True, True, False, False, False]
                random.shuffle(self.lancelot_swaps)
            counter = 1
            if self.add_morgana:
                evil_roles[counter] = Role.MORGANA
                counter += 1
            if self.add_mordred:
                evil_roles[counter] = Role.MORDRED
                counter += 1
            if self.add_oberon:
                evil_roles[counter] = Role.OBERON
                counter += 1
            if self.add_lancelot:
                evil_roles[counter] = Role.EVIL_LANCELOT
            # Concatenates good roles with bad roles, then shuffles and assigns to players
            roles = good_roles + evil_roles
            random.shuffle(roles)
            for i in range(0,len(self.players)):
                # TODO: remove deprecated line below
                #   player_name = self.players[i][0] # Will probably use set_roles function in the future, during some code cleanup
                self.players[i].Role = roles.pop()
            players = self.players
            random.shuffle(players) # This is to determine turn order
            self.king = players[0].id
            self.lady = players[len(players)-1].id
            self.state = GameState.NOMINATE
            self.settings = game_settings # After number of players determined, sets settings to amount of players
            self.questers_required = self.settings['Q1']
            return True
        else:
            return False

    def end_game(self):
        '''
        Ends the game.
        Sets the state of the game to GAME_OVER.
        '''
        self.state = GameState.GAME_OVER

    def lancelot_swap(self):
        '''
        Swaps the roles of the two Lancelot players.
        '''
        swap = self.lancelot_swaps.pop()
        if not swap: # Swap is false and does not occur on this turn.
            return False
        for i in range(0, len(self.players)):
            if self.players[i].role == Role.GOOD_LANCELOT:
                self.players[i] = (self.players[i][0], Role.EVIL_LANCELOT)
            elif self.players[i].role == Role.EVIL_LANCELOT:
                self.players[i] = (self.players[i][0], Role.GOOD_LANCELOT)
        return True

    def assassinate(self, target_id):
        '''
        Targets a player by id and attempts to assassinate Merlin.
        '''
        target_role = self.get_role(target_id)
        return target_role == self.get_merlin().role
