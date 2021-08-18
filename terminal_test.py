from avalon import Session, GameState, Vote, Role

def menu():
    while(True):
        print('''
        Welcome to the Avalon test app.
        Here you can select from the following options:
        1) Start game
        ''')
        user_input = input("Which option would you like to choose? ")
        if(user_input == "1"):
            pass
            # print("Option 1 picked.")
        else:
            print("Not a valid option.")

def add_players():
    number_of_players = int(input("How many players would you like to add?"))
    for _ in range(0,number_of_players):
        player_name = input("Name of player " + _ + "?")


menu()