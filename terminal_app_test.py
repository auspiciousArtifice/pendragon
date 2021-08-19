import unittest
# from unittest import mock
from unittest.mock import patch

import terminal_app


class TestGame(unittest.TestCase):

    raw_input = '''1
5
player1
player2
player3
player4
player5
3
2143
3
6931
6
1
y
n
n
n
n
n'''

    raw_input2 = '''1
5
player1
player2
player3
player4
player5
3
2143
3
6931
6
1
y
n
y
y
y
y
p
f'''

    number_of_players = '5'
    player_0_name = 'Player1'
    player_1_name = 'Player2'
    player_2_name = 'Player3'
    player_3_name = 'Player4'
    player_4_name = 'Player5'

    # @patch('builtins.input', side_effect=[number_of_players, player_0_name, player_1_name, player_2_name,
    # player_3_name, player_4_name])
    @patch('builtins.input', side_effect=raw_input.split('\n'))
    def test_game(self, mock_inputs):
        result = terminal_app.start_game()
        # print(result)

    @patch('builtins.input', side_effect=raw_input2.split('\n'))
    def test_game2(self, mock_inputs):
        result = terminal_app.start_game()
        # print(result)


TestGame().test_add_players()