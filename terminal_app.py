#!/usr/bin/python
from avalon import Session, GameState, Vote, Role
import random

game = Session(host=0000)


def menu():
    while True:
        print(
            '''
            Welcome to the Avalon test app.
            Here you can select from the following options:
            1) Start game
            '''
        )
        user_input = input("Which option would you like to choose? ")
        if user_input == "1":
            start_game()
        else:
            print("Not a valid option.")


def start_game():
    add_players()
    # print(game.host)
    # print(game.host == game.get_player(0000).id) # DEBUG: checking host of game
    print(game.start_game())
    while True:
        while True:
            print(
                '''
                Here you can select from the following options:
                1) Show turn order
                2) List players
                3) Mock nomination
                4) Mock removal
                5) List questers
                6) Mock start vote
                ''')
            user_input = input("Which option would you like to choose? ")
            if user_input == "1":
                turn()
            elif user_input == "2":
                print(game.players)
            elif user_input == "3":
                mock_nomination()
            elif user_input == "4":
                mock_removal()
            elif user_input == "5":
                questers()
            elif user_input == "6":
                mock_start_voting()
                if game.state == GameState.TEAM_VOTE:
                    break
            else:
                print("Not a valid option.")
        while True:
            print(
                '''
                Here you can select from the following options:
                1) Mock vote
                2) List players
                3) List questers
                ''')
            user_input = input("Which option would you like to choose? ")
            if user_input == "1":
                mock_vote_result = mock_vote()
                if mock_vote_result:
                    questing()
                elif not mock_vote_result:
                    pass
                elif mock_vote_result is None:
                    break
                game.increment_turn()
                break

            elif user_input == "2":
                print(game.players)
            elif user_input == "3":
                questers()
            else:
                print("Not a valid option.")


def add_players():
    number_of_players = 0
    while number_of_players < 5 or number_of_players > 10:
        number_of_players = int(input("How many players would you like to add?\nEnter a number from 5-10. "))

    random.seed(6969)
    random_ids = random.sample(range(1000, 9999), number_of_players)

    for i in range(0, number_of_players):
        player_name = input("Name of player " + str(i) + "? ")
        game.add_player(random_ids[i], player_name)


def turn():
    current_turn = game.turn
    player_order = ''
    for i in range(0, game.num_players()):
        player_user = game.players[i]
        if i != current_turn:
            player_order += f'{player_user.Name}\n'
        else:
            player_order += f'{player_user.Name} <- current turn\n'
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
    # DEBUG: remove bottom code block for testing voting values later - Shamee
    # print('Testing voting values...')
    # print(
    #     f'y - {game.check_user_vote("y")}, yes - {game.check_user_vote("yes")}, yea - {game.check_user_vote("yea")}, '
    #     f'yep - {game.check_user_vote("yep")}')
    # print(
    #     f'n - {game.check_user_vote("n")}, nay - {game.check_user_vote("nay")}, no - {game.check_user_vote("no")}, '
    #     f'yep - {game.check_user_vote("nada")}')
    print(game.add_voter(2143, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: game vote check - Shamee
    print(game.add_voter(2143, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: duplicate game vote check - Shamee
    print(game.add_voter(6931, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: game vote check - Shamee
    print(game.add_voter(9327, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: game vote check - Shamee
    print(game.add_voter(5453, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: game vote check - Shamee
    print(game.add_voter(2091, game.check_user_vote(input("Add user vote. [y/n] ")))) # DEBUG: game vote check - Shamee
    print(game.tally_votes())
    if game.tally_votes():
        vote_test = game.check_vote_result()
        print(vote_test)
        if vote_test:
            return True # vote passed
        elif game.doom_counter == 5:
            print('Doom counter is 5, vote passes anyway.')
            return True # vote passed
        else:
            game.increment_doom_counter()
            game.state = GameState.NOMINATE
            return False # vote failed
    else:
        return None # Not enough people voted


def questing():
    game.state = GameState.QUESTING
    print('Quest begins!')
    for quester in game.questers:
        quest_check = input(f"Pass or fail quest for {game.get_player(quester).Name}? [p/f] ")
        if quest_check == 'p':
            pass
        elif quest_check == 'f':
            game.decrement_quest_result()
    quest_result = game.check_quest()
    if quest_result:
        print('Quest passed!')
    else:
        fails = game.quest_result * -1
        print(f'Quest fails... by {fails} fail{"s" if fails > 1 else ""}. :(')
    post_quest_resolve(quest_result)


def post_quest_resolve(quest_result):
    game.next_quest(quest_result)
    if game.current_quest+1 >= 3 and game.add_lancelot:
        if game.lancelot_swap():
            print('Attention: Lancelots have been swapped!')
    if game.quests_passed >= 3:
        last_stand()
    elif game.quests_failed >= 3:
        print('Bad guys win.')
        game.end_game()
    else:
        game.reset_doom_counter()
        game.state = GameState.NOMINATE


def last_stand():
    game.state = GameState.LAST_STAND
    print('Bad guys: ')
    for player in game.players:
        if player.Role < 0:
            print(f'Name: {player.Name}, Role: {player.Role}')
    kill_id = input("Who are you choosing to assassinate? <id> ")
    if game.assassinate(kill_id):
        print('Bad guys win, you have successfully assassinated Merlin.')
        game.end_game()
    else:
        merlin = game.get_merlin()
        print(f'Good guys win. Merlin was {merlin.Name}.')
        game.end_game()


if __name__ == "__main__":
    menu()

# menu()
