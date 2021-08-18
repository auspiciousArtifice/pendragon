#!/usr/bin/python
from avalon import Session, GameState, Vote, Role
import random

game = Session(host=0000)

def menu():
    while(True):
        print(
'''
Welcome to the Avalon test app.
Here you can select from the following options:
1) Start game
'''
        )
        user_input = input("Which option would you like to choose? ")
        if(user_input == "1"):
            start_game()
        else:
            print("Not a valid option.")

def start_game():
    add_players()
    # print(game.host)
    # print(game.host == game.get_player(0000).id) # DEBUG: checking host of game
    print(game.start_game())
    while(True):
        print(
'''
Here you can select from the following options:
1) Show turn order
2) List players
3) Mock nomination
4) Mock removal
5) List questers
6) Mock start vote
'''     )
        user_input = input("Which option would you like to choose? ")
        if(user_input == "1"):
            turn()
        elif(user_input == "2"):
            print(game.players)
        elif(user_input == "3"):
            mock_nomination()
        elif(user_input == "4"):
            mock_removal()
        elif(user_input == "5"):
            questers()
        elif(user_input == "6"):
            mock_start_voting()
            if game.state.TEAM_VOTE:
                break
        else:
            print("Not a valid option.")
    while(True):
        print(
'''
Here you can select from the following options:
1) Mock vote
2) List players
3) List questers
'''     )
        user_input = input("Which option would you like to choose? ")
        if(user_input == "1"):
            mock_vote()
        elif(user_input == "2"):
            print(game.players)
        elif(user_input == "3"):
            questers()
        else:
            print("Not a valid option.")

def add_players():
    number_of_players = int(input("How many players would you like to add?\nEnter a number from 5-10. "))

    random.seed(6969)
    random_ids = random.sample(range(1000,9999), number_of_players)

    for i in range(0,number_of_players):
        player_name = input("Name of player " + str(i) + "? ")
        game.add_player(random_ids[i], player_name)

def turn():
    current_turn = game.turn
    player_order = ''
    for i in range(0, game.num_players()):
        player_user = game.players[i]
        if i != current_turn:
            player_order += f'{player_user.name}\n'
        else:
            player_order += f'{player_user.name} <- current turn\n'
    print(player_order)

def mock_nomination():
    if len(game.questers) < game.questers_required:
        print(game.add_quester(input("Who would you like to nominate? ")))
    else:
        print('Cannot nominate anymore, too many questers.')

def mock_removal():
    print(game.remove_quester(input("Who would you like to remove? ")))

def questers():
    print(game.questers)

def mock_start_voting():
    print(game.start_voting())

def mock_vote():
    print('Testing voting values...')
    print(f'y - {game.check_user_vote("y")}, yes - {game.check_user_vote("yes")}, yea - {game.check_user_vote("yea")}, yep - {game.check_user_vote("yep")}')
    print(f'n - {game.check_user_vote("n")}, nay - {game.check_user_vote("nay")}, no - {game.check_user_vote("no")}, yep - {game.check_user_vote("nada")}')
    game.votes = game.votes + game.value
    game.add_voter(2143, game.check_user_vote())

if __name__ == "__main__":
    menu()

# menu()