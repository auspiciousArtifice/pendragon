import random
import json
from enum import Enum
from threading import Lock
from discord.ext import commands

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
    def __init__(self, host):
        self.host = int(host)
        self.players = []
        self.joining = Lock()

        self.king = None
        self.lady = None
        self.__turn = 0
        self.state = GameState.CREATED

        self.quests_passed = 0
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
        self.merlins_watch_list = []
        self.evil_watch_list = []
        # TODO: rename config variables
        self.add_percival = False
        self.add_morgana = False
        self.add_mordred = False
        self.add_oberon = False
        self.add_lancelot = False
        self.lancelot_swaps = []
        self.settings = [] # Settings will change based on # of players after game starts
        with open('settings.json') as json_file:
            self.settings = json.load(json_file)['game_configs'] # Currently sets settings to all settings in settings.json

    @property
    def turn(self):
        return self.__turn % len(self.players)

    @turn.setter
    def turn(self, turn):
        self.__turn = turn

    # TODO: Get rid of getter
    # def get_host(self):
    #     return self.host

    # Replaced getter with property
    # def get_turn(self):
    #     return self.turn % len(self.get_players())

    # TODO: Get rid of getter
    # def get_total_turns(self):
    #     return self.turn

    # TODO: Get rid of getter
    # def get_double_fail(self):
    #     return self.double_fail

    # TODO: Get rid of getter
    # def get_players(self):
    #     return self.players

    def get_num_players(self):
        return len(self.players)

    # TODO: Make property
    def get_player(self, id):
        id = int(id)
        for i in range(0, len(self.get_players())):
            player_id = int(self.get_players()[i][0])
            if player_id == id:
                return self.get_players()[i]
        return None

    # TODO: Make property
    def get_merlin(self):
        for i in range(0, len(self.get_players())):
            role = self.get_players()[i][1]
            if role == Role.MERLIN:
                return self.get_players[i]
        return None

    # TODO: Make property
    def get_role(self, player):
        return self.get_player(player)[1]

    # TODO: Get rid of getter
    # def get_king(self):
    #     return self.king

    # TODO: Get rid of getter
    # def get_lady(self):
    #     return self.lady

    # TODO: Get rid of getter
    # def get_state(self):
    #     return self.state

    # TODO: Get rid of getter
    # def get_quests_passed(self):
    #     return self.quests_passed

    # TODO: Get rid of getter
    # def get_quest_result(self):
    #     return self.quest_result

    # TODO: Get rid of getter
    # def get_quests_failed(self):
    #     return self.quests_failed

    # TODO: Get rid of getter
    # def get_current_quest(self):
    #     return self.current_quest

    # TODO: Get rid of getter
    # def get_questers_required(self):
    #     return self.questers_required

    # TODO: Get rid of getter
    # def get_questers(self):
    #     return self.questers

    # TODO: Get rid of getter
    # def get_doom_counter(self):
    #     return self.doom_counter

    # TODO: Get rid of getter
    # def get_votes(self):
    #     return self.votes

    # TODO: Get rid of getter
    # def get_voted(self):
    #     return self.voted

    def get_voter(self, player):
        return player in self.get_voted()

    # TODO: Get rid of getter
    # def get_add_percival(self):
    #     return self.add_percival

    # TODO: Get rid of getter
    # def get_add_morgana(self):
    #     return self.add_morgana

    # TODO: Get rid of getter
    # def get_add_mordred(self):
    #     return self.add_mordred

    # TODO: Get rid of getter
    # def get_add_oberon(self):
    #     return self.add_oberon

    # TODO: Get rid of getter
    # def get_add_lancelot(self):
    #     return self.add_lancelot

    # TODO: Get rid of getter
    # def get_settings(self):
    #     return self.settings

    # Replaced setter with property
    # def set_lady(self, player):
    #     self.lady = int(player)
    @property
    def lady(self):
        return self.__lady

    @lady.setter
    def lady(self, player):
        self.__lady = int(player)

    # Replaced setter with property
    # def set_king(self, player):
    #     self.king = int(player)
    @property
    def king(self):
        return self.__king

    @king.setter
    def king(self, player):
        self.__king = int(player)

    # TODO: Get rid of setter
    # def set_votes(self, votes):
    #     self.votes = votes

    # TODO: Get rid of setter
    # def set_double_fail(self, fail):
    #     self.double_fail = fail

    # TODO: Get rid of setter
    # def set_doom_counter(self, number):
    #     self.doom_counter = number

    # TODO: Get rid of setter
    # def set_questers_required(self, number):
    #     self.questers_required = number

    # TODO: Make property
    def set_role(self, id, role):
        id = int(id)
        for i in range(0, len(self.get_players())):
            player_id = int(self.get_players()[i][0])
            if player_id == id:
                self.get_players()[i] = (id, role)

    # TODO: Get rid of setter
    # def set_state(self, new_state):
    #     self.state = new_state

    # TODO: Get rid of setter
    # def set_quest_result(self, number):
    #     self.quest_result = number

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

    def increment_quest_passed(self):
        self.quests_passed += 1

    def increment_quest_failed(self):
        self.quests_failed += 1

    def increment_current_quest(self):
        self.current_quest += 1
        self.set_questers_required(self.settings[f'Q{self.current_quest+1}'])

    def next_quest(self, passed):
        if passed:
            self.quests_passed += 1
        else:
            self.quests_failed += 1
        self.current_quest += 1
        self.set_questers_required(self.settings[f'Q{self.current_quest+1}'])

    def increment_doom_counter(self):
        self.doom_counter += 1

    def increment_turn(self):
        self.turn += 1
        self.king = self.get_players()[self.get_turn()][0]
        self.clear_voted()
        self.clear_questers()
        self.set_votes(0)

    def vote_result(self):
        return self.get_votes() > 0

    def check_user_vote(self, user_vote):
        if(user_vote == 'yes' or user_vote == 'yea' or user_vote == 'y'):
            return Vote.YEA
        elif(user_vote == 'no' or user_vote == 'nay' or user_vote == 'n'):
            return Vote.NAY
        else:
            return None

    def check_voted(self):
        return len(self.get_voted()) == len(self.get_players()) # True == Everyone Voted

    def add_player(self, player):
        if self.get_state() == GameState.CREATED:
            if self.get_player(player) is None:
                player = int(player)
                player_tuple = (player, None)
                self.get_players().append(player_tuple)
                return True
            return False
        else:
            return False

    def add_dummy(self, dummy):
        dummy = int(dummy)
        if self.get_state() == GameState.CREATED:
            player_tuple = (dummy, None)
            self.get_players().append(player_tuple)
        else:
            print('Game state is not \'Created\'')

    def remove_player(self, player):
        if self.get_state() == GameState.CREATED:
            for i in range(0, len(self.get_players())):
                if int(self.get_players()[i][0]) == int(player):
                    del self.players[i]
                    return True
            return False
        else:
            return False

    def add_quester(self, player):
        if self.get_state() == GameState.NOMINATE:
            if self.get_player(int(player)):
                quester = int(player) in self.get_questers()
                if not quester:
                    self.get_questers().append(int(player))
                    return True
            else:
                return False
            return False
        else:
            return False

    def dummy_questers(self):
        if self.get_state() == GameState.NOMINATE:
            while len(self.questers) < self.questers_required:
                self.get_questers().append(self.get_players()[-1][0])
        else:
            return False

    def remove_quester(self, player):
        if self.get_state() == GameState.NOMINATE:
            for i in range(0, len(self.get_questers())):
                if self.get_questers()[i] == int(player):
                    del self.questers[i]
                    return True
            return False
        else:
            return False

    def add_voter(self, player):
        if self.get_state() == GameState.TEAM_VOTE:
            voted = int(player) in self.get_voted()
            if not voted:
                self.get_voted().append(int(player))
                return True
            return False
        else:
            return False

    def remove_voter(self, player):
        if self.get_state() == GameState.TEAM_VOTE:
            for i in range(0, len(self.get_voted())):
                if self.get_voted()[i] == player:
                    del self.voted[i]
                    return True
            return False
        else:
            return False

    def clear_voted(self):
        self.voted = []

    def clear_questers(self):
        self.questers = []

    def use_lady(self, player):
        if self.get_state() == GameState.NOMINATE:
            return self.get_player(int(player))[1]

    def check_quest(self):
        result = self.get_quest_result()
        if self.get_double_fail():
            if result <= -2:
                return False #quest fails
            else:
                return True #quest passes
        else:
            if result <= -1:
                return False
            else:
                return True

    def start_game(self):
        if self.get_state() == GameState.CREATED:
            if not str(len(self.get_players())) in self.settings:
                return False
            game_settings = self.settings[str(len(self.get_players()))]
            ttl_evil_replacement = self.get_add_morgana() + self.get_add_mordred() + self.get_add_oberon() + self.get_add_lancelot()
            if game_settings['EVIL']-1 < ttl_evil_replacement:
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
            if self.get_add_percival():
                good_roles[counter] = Role.PERCIVAL
                counter += 1
            if self.get_add_lancelot():
                good_roles[counter] = Role.GOOD_LANCELOT
                self.lancelot_swaps = [True, True, False, False, False]
                random.shuffle(self.lancelot_swaps)
            counter = 1
            if self.get_add_morgana():
                evil_roles[counter] = Role.MORGANA
                counter += 1
            if self.get_add_mordred():
                evil_roles[counter] = Role.MORDRED
                counter += 1
            if self.get_add_oberon():
                evil_roles[counter] = Role.OBERON
                counter += 1
            if self.get_add_lancelot():
                evil_roles[counter] = Role.EVIL_LANCELOT
            # Concatenates good roles with bad roles, then shuffles and assigns to players
            roles = good_roles + evil_roles
            random.shuffle(roles)
            for i in range(0,len(self.get_players())):
                  player_name = self.get_players()[i][0] # Will probably use set_roles function in the future, during some code cleanup
                  self.get_players()[i] = (player_name,roles.pop())
            players = self.get_players()
            random.shuffle(players) # This is to determine turn order
            self.set_king(players[0][0])
            self.set_lady(players[len(players)-1][0])
            self.set_state(GameState.NOMINATE)
            self.settings = game_settings # After number of players determined, sets settings to amount of players
            self.set_questers_required(game_settings['Q1'])
            return True
        else:
            return False

    def lancelot_swap(self):
        swap = self.lancelot_swaps.pop()
        if not swap: # Swap is false
            return False
        for i in range(0, len(self.get_players())):
            if self.get_players[i][1] == Role.GOOD_LANCELOT:
                self.get_players[i] = (self.get_players[i][0], Role.EVIL_LANCELOT)
            elif self.get_players[i][1] == Role.EVIL_LANCELOT:
                self.get_players[i] = (self.get_players[i][0], Role.GOOD_LANCELOT)
        return True

    def assassinate(self, target):
        target_role = self.get_role(target)
        return target_role == self.get_merlin()[1]
