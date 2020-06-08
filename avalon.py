from enum import Enum
from threading import Lock
import random

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

class Session:
    def __init__(self, host):
        self.host = host
        self.players = []
        self.joining = Lock()
        self.king = None
        self.lady = None
        self.turn = 0
        self.state = GameState.CREATED
        
        self.quests_passed = 0
        self.quests_failed = 0
        self.current_quest = 0
        self.questers = []
        self.nominating = Lock()
        self.doom_counter = 0
        
        self.votes = 0
        self.voted = []
        self.voting = Lock()

    def get_host(self):
        return self.host

    def get_turn(self):
        return self.turn % len(self.players)

    def get_players(self):
        return self.players

    def get_num_players(self):
        return len(self.players)

    def get_player(self, name):
        for i in range(0, len(self.players)):
            if self.players[i][0] == name:
                return self.players[i]
        return None

    def get_quester(self, name):
        for i in range(0, len(self.questers)):
            if self.questers[i][0] == name:
                return self.questers[i]
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

    def get_quests_failed(self):
        return self.quests_failed

    def get_current_quest(self):
        return self.current_quest
    
    def get_questers(self):
        return self.questers
    
    def get_doom_counter(self):
        return self.doom_counter

    def get_votes(self):
        return self.votes
    
    def get_voted(self):
        return self.voted

    def set_lady(self, player):
        self.lady = player

    def set_king(self, player):
        self.king = player

    def set_votes(self, votes):
        self.votes = votes

    def set_doom_counter(self, number):
        self.doom_counter = number

    def set_role(self, player, role):
        player_obj = self.get_player(player)
        player_obj[1] = role

    def set_state(self, new_state):
        self.state = new_state

    def increment_quest_passed(self):
        self.quests_passed += 1

    def increment_quest_failed(self):
        self.quests_failed += 1

    def increment_current_quest(self):
        self.current_quest += 1

    def increment_doom_counter(self):
        self.doom_counter += 1

    def increment_turn(self):
        self.turn += 1
        self.king = players[self.turn % len(self.players)]

    def add_player(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.CREATED:
            if self.get_player(player) is not None:
                player_tuple = (player, None)
                self.players.append(player_tuple)
                return True
            return False
        else:
            return False

    def remove_player(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.CREATED:
            for i in range(0, len(self.players)):
                if self.players[i][0] == player:
                    del self.players[i]
                    return True
            return False
        else:
            return False

    def add_quester(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.NOMINATE:
            quester = self.get_questers().contains(player)
            if not quester:
                self.get_questers().append(player)
                return True
            return False
        else:
            return False

    def remove_quester(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.NOMINATE:
            for i in range(0, len(self.questers)):
                if self.questers[i] == player:
                    del self.questers[i]
                    return True
            return False
        else:
            return False

    def add_voter(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.TEAM_VOTE:
            voted = self.get_voted().contains(player)
            if not voted:
                self.get_voted.append(player)
                return True
            return False
        else:
            return False

    def remove_voter(self, player):
        # TODO: use mutex here
        if self.get_state() == GameState.TEAM_VOTE:
            for i in range(0, len(self.voted)):
                if self.voted[i] == player:
                    del self.voted[i]
                    return True
            return False
        else:
            return False

    def use_lady(self, player):
        if self.get_state() == GameState.NOMINATE:
            return self.get_player(player)[1]

    def start_quest(self):
        pass #TODO: check if doom_counter == 5

    def start_game(self):
        if self.get_state() == GameState.CREATED:
            # After game starts
            # for player_tuple in players
            #     player_tuple[1] = select_random_role()
            #     # select_random_role takes a role from the list then excludes it for later selections
            # random.shuffle(players) # This is to determine turn order
            self.change_state(GameState.NOMINATE)
            return True
        else:
            return False
