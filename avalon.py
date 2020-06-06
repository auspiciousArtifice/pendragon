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

class Role(Enum):
    GOOD_GUY = 1
    BAD_GUY = -1
    MERLIN = 1
    ASSASSIN = -1
    PERCIVAL = 1
    MORGANA = -1
    MORDRED = -1
    OBERON = -1
    GOOD_LANCELOT = 1
    BAD_LANCELOT = -1

class Session:
    def __init__(self):
        self.players = {}
        self.state = GameState.CREATED
        self.quests_passed = 0
        self.quests_failed = 0
        self.current_quest = 0
        self.votes = {}


    def get_num_players(self):
        return len(self.players)

    def change_state(self, new_state):
        self.state = new_state

    def cast_vote(self, player_name, vote_type):
        votes[player_name] = vote_type
