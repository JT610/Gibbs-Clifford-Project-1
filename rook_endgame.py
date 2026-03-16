def rook_endgame(game):
    # TODO setup board

    white_move = True
    game.game_active = True

    while game.game_active:
        print(game)
    

        # TODO implement endgame

        pass

    # ask if you want to play again
    resp = -1
    while True:
        resp = input("Do you want to play another game? (y/n): ")
        if resp.lower() in ['y', 'yes']:
            break
        elif resp.lower() in ['n', 'no']:
            print("Quitting program...")
            exit()
        else:
            print("Please enter a valid input (y/n): ")