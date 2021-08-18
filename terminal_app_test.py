import unittest
# from unittest import mock
from unittest.mock import patch

import terminal_app

class TestAddPlayers(unittest.TestCase):

    raw_input = '''5
player1
player2
player3
player4
player5
1'''

    number_of_players = '5'
    player_0_name = 'Player1'
    player_1_name = 'Player2'
    player_2_name = 'Player3'
    player_3_name = 'Player4'
    player_4_name = 'Player5'

    # @patch('builtins.input', side_effect=[number_of_players, player_0_name, player_1_name, player_2_name, player_3_name, player_4_name])
    @patch('builtins.input', side_effect=raw_input.split('\n'))
    def test_add_players(self, mock_inputs):
        result = terminal_app.start_game()
        # print(result)

TestAddPlayers().test_add_players()