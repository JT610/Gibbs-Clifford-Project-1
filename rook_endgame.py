def setup_rook_endgame(game):
    ##### setup board for rook endgame
    import random

    # initialize board with only kings and one rook, with random placement of the pieces
    while True:
        game.board = [""] * 64

        game.board[random.randint(0, 63)] = 'K'
        game.board[random.randint(0, 63)] = 'k'
        game.board[random.randint(0, 63)] = 'R'

        # make sure the kings are not in check and that no two pieces were put on the same square
        if game.board.count('K') == 1 and game.board.count('k') == 1 and game.board.count('R') == 1:
            if game.is_in_check('white') or game.is_in_check('black'):
                continue
            break
    
    game.en_passant_possible_file = None
    game.white_can_castle_kingside = False
    game.white_can_castle_queenside = False
    game.black_can_castle_kingside = False
    game.black_can_castle_queenside = False
    game.black_queenside_rook_file = 'a'
    game.white_queenside_rook_file = 'a'
    game.black_kingside_rook_file = 'h'
    game.white_kingside_rook_file = 'h'
    game.position_history = []
    game.move_log = []
    game.game_active = True
    game.move_counter = 0

def computer_move(game):
    ##### process computer move

    white_king_index = game.board.index('K')
    white_king_file = chr(ord('a') + white_king_index % 8)
    white_king_rank = 8 - (white_king_index // 8)

    black_king_index = game.board.index('k')
    black_king_file = chr(ord('a') + black_king_index % 8)
    black_king_rank = 8 - (black_king_index // 8)

    white_rook_index = game.board.index('R')
    white_rook_file = chr(ord('a') + white_rook_index % 8)
    white_rook_rank = 8 - (white_rook_index // 8)

    # TODO implement logic for rook checkmate, set these 3 
    # variables to the piece and destination
    # use above variables to see current piece positions
    piece = 'R'
    dest_file = 'a'
    dest_rank = 1
    
    # DEBUG ####################################################################################################
    # remove this after implementing computer move logic, just to make sure the computer is making legal moves #
    ############################################################################################################
    legal_moves = game.get_all_legal_moves(True)                                                               #
    if not [x for x in legal_moves if (x[4] == piece and x[2] == dest_file and x[3] == dest_rank)]:            #
        print("\n\nComputer attempted an illegal move\n")                                                            #
        print("Legal moves are: ", legal_moves)                                                                #
        print("\nComputer attempted move: ", piece + dest_file + str(dest_rank) + '\n')                                 #
        exit()                                                                                                 #
    ############################################################################################################

    src_index = game.board.index(piece)
    src_file = chr(ord('a') + src_index % 8)
    src_rank = 8 - (src_index // 8)
    game.set(src_file, src_rank, "")
    game.set(dest_file, dest_rank, piece)

    game.move_log = game.move_log + [game.move_alg_not(src_file, src_rank, dest_file, dest_rank, piece, False, '', False, False, game.get_all_legal_moves(True)) + ('+' if game.is_in_check(False) else '')]




def rook_endgame(game):
    ##### Main function to run rook endgame
    setup_rook_endgame(game)

    white_move = True
    game.game_active = True

    while game.game_active:
        if white_move:
            computer_move(game)
            valid = True
        else:
            # print board and process move if blacks turn
            print(game)
            valid = game.process_move(white_move)
            
        # switch side
        if valid: 
            white_move = not white_move

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