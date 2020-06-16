import random
import json
from enum import Enum
from threading import Lock
from discord.ext import commands


class GameState(Enum):
    CREATED = 0
    NOMINATE = 1
    TEAM_VOTE = 2
    QUESTING = 3
    LAST_STAND = 4
    GAME_OVER = 5

class Vote(Enum):
    NAY = -1
    YEA = 1

class Role(Enum):
    GOOD_GUY = 1
    EVIL_GUY = -5
    MERLIN = 2
    ASSASSIN = -3
    PERCIVAL = 3
    MORGANA = -2
    MORDRED = -1
    OBERON = 0
    GOOD_LANCELOT = 4
    EVIL_LANCELOT = -4

    # Simplified conditions for role checks
    # if player_role.value < -1 #Merlin
    # if player_role.value < 0 #Evil, except Oberon
    # if player_role.value > 0 #Good, unused
    # if abs(player_role.value) == 2 #Percival

class Session:
    def __init__(self, host):
        self.host = int(host)
        self.players = []
        self.joining = Lock()

        self.king = None
        self.lady = None
        self.turn = 0
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
        self.add_percival = False
        self.add_morgana = False
        self.add_mordred = False
        self.add_oberon = False
        self.add_lancelot = False
        self.lancelot_swaps = []
        self.settings = [] # Settings will change based on # of players after game starts
        with open('settings.json') as json_file:
            self.settings = json.load(json_file)['game_configs'] # Currently sets settings to all settings in settings.json

    def get_host(self):
        return self.host

    def get_turn(self):
        return self.turn % len(self.get_players())

    def get_total_turns(self):
        return self.turn

    def get_double_fail(self):
        return self.double_fail

    def get_players(self):
        return self.players

    def get_num_players(self):
        return len(self.players)

    def get_player(self, id):
        id = int(id)
        for i in range(0, len(self.get_players())):
            player_id = int(self.get_players()[i][0])
            if player_id == id:
                return self.get_players()[i]
        return None

    def get_role(self, player):
        return self.get_player(player)[1]

    def get_king(self):
        return self.king

    def get_lady(self):
        return self.lady

    def get_state(self):
        return self.state

    def get_quests_passed(self):
        return self.quests_passed

    def get_quest_result(self):
        return self.quest_result

    def get_quests_failed(self):
        return self.quests_failed

    def get_current_quest(self):
        return self.current_quest
    
    def get_questers_required(self):
        return self.questers_required
    
    def get_questers(self):
        return self.questers
    
    def get_doom_counter(self):
        return self.doom_counter

    def get_votes(self):
        return self.votes
    
    def get_voted(self):
        return self.voted

    def get_voter(self, player):
        return player in self.get_voted()

    def get_add_percival(self):
        return self.add_percival

    def get_add_morgana(self):
        return self.add_morgana

    def get_add_mordred(self):
        return self.add_mordred

    def get_add_oberon(self):
        return self.add_oberon

    def get_add_lancelot(self):
        return self.add_lancelot

    def get_settings(self):
        return self.settings

    def set_lady(self, player):
        self.lady = int(player)

    def set_king(self, player):
        self.king = int(player)

    def set_votes(self, votes):
        self.votes = votes

    def set_double_fail(self, fail):
        self.double_fail = fail

    def set_doom_counter(self, number):
        self.doom_counter = number

    def set_questers_required(self, number):
        self.questers_required = number

    def set_role(self, id, role):
        id = int(id)
        for i in range(0, len(self.get_players())):
            player_id = int(self.get_players()[i][0])
            if player_id == id:
                self.get_players()[i] = (id, role)

    def set_state(self, new_state):
        self.state = new_state
    
    def set_quest_result(self, number):
        self.quest_result = number

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

    def increment_doom_counter(self):
        self.doom_counter += 1

    def increment_turn(self):
        self.turn += 1
        self.king = self.get_players()[self.get_turn()][0]
        self.clear_voted()
        self.clear_questers()
        self.set_votes(0)

    def vote_result(self):
        result = (self.get_votes() > 0)
        return result

    def check_user_vote(self, user_vote):
        if(user_vote == 'yes' or user_vote == 'yea'):
            return Vote.YEA
        elif(user_vote == 'no' or user_vote == 'nay'):
            return Vote.NAY
        else:
            return None

    def check_voted(self):
        if(len(self.get_voted()) == len(self.get_players())): #everyone voted
            result = True #votes are done
        else:
            result = False #votes are still being taken
        return result

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
                random.shuffle(lancelot_swaps)
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
                  player_name = self.get_players()[i][0]
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
