import random
from enum import Enum
from threading import Lock

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
    GOOD_GUY = 0
    EVIL_GUY = 11
    MERLIN = 2
    ASSASSIN = 13
    PERCIVAL = 4
    MORGANA = 15
    MORDRED = 16
    OBERON = 7
    GOOD_LANCELOT = 8
    EVIL_LANCELOT = 19

class Session:
    def __init__(self, host):
        self.host = host
        self.players = {host: None}
        self.state = GameState.CREATED
        self.quests_passed = 0
        self.quests_failed = 0
        self.current_quest = 0
        self.questers = []
        self.doom_counter = 0
        self.votes = 0
        self.voted = []
        self.voting = Lock()
        self.merlins_watch_list = []
        self.evil_watch_list = []

    def get_host(self):
        return self.host

    def get_players(self):
        return self.players

    def add_player(self, player):
        if self.get_state() == GameState.CREATED:
            self.players[player] = None
            return True
        else:
            return False

    def remove_player(self, player):
        if self.get_state() == GameState.CREATED:
            self.players.pop(player)
            return True
        else:
            return False

    def get_num_players(self):
        return len(self.players)

    def change_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def start_game(self):
        if self.get_state() == GameState.CREATED:
            players = list(self.players.keys())
            #the for loop below exists for debugging currently. MUST BE REMOVED LATER	
            for i in range(len(players), 5):
                players.append('Player_'+str(i))
            #population of roles function. may put in another function later
            roles = [Role.MERLIN, Role.ASSASSIN]
            inverter = True
            while len(roles) < len(players):
                if inverter:
                    roles.append(Role.GOOD_GUY)
                else:
                    roles.append(Role.EVIL_GUY)
                inverter = not inverter
            if len(roles) % 2 == 0:
                roles[-1] = Role.GOOD_GUY
            #assigning roles to players and populating watch lists
            for player in players:
                player_role = random.choice(roles)
                self.players[player] = player_role
                roles.remove(player_role)
                if player_role.value % 2 == 1:
                    self.merlins_watch_list.append(player)
                if player_role.value > 9:
                    self.evil_watch_list.append(player)
            print(self.players)
            self.change_state(GameState.NOMINATE)
            return True
        else:
            return False

    def cast_vote(self, player_name, vote_type):
        votes[player_name] = vote_type
