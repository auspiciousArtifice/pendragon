from enum import Enum

class GameState(Enum):
    CREATED = 0
    PICK_QUEST = 1
    QUESTING = 2
    LAST_STAND = 3
    GAME_OVER = 4

class Vote(Enum):
    NAY = -1
    YEA = 1

class Session:
    def __init__(self, host):
        self.host = host
        self.players = {host: None}
        self.state = GameState.CREATED
        self.quests_passed = 0
        self.quests_failed = 0
        self.current_quest = 0
        self.votes = {}

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
            self.change_state(GameState.PICK_QUEST)
            return True
        else:
            return False

    def cast_vote(self, player_name, vote_type):
        votes[player_name] = vote_type