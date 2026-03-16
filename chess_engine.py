import re
from rook_endgame import rook_endgame
from chess_clock import *

class ChessEngine:
    def __init__(self):
        # Initialize the chess engine
        self.board = [""] * 64
        self.en_passant_possible_file = None
        self.white_can_castle_kingside = False
        self.white_can_castle_queenside = False
        self.black_can_castle_kingside = False
        self.black_can_castle_queenside = False
        self.black_queenside_rook_file = None
        self.white_queenside_rook_file = None
        self.black_kingside_rook_file = None
        self.white_kingside_rook_file = None
        self.move_counter = 0
        self.position_history = [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, True]]
        self.game_active = False
        pass

    def setup_normal(self):
        # Set up the initial chess board configuration
        self.board = [""] * 64
        self.board[0:8] = ["r", "n", "b", "q", "k", "b", "n", "r"]  # Black pieces
        self.board[8:16] = ["p"] * 8  # Black pawns
        self.board[48:56] = ["P"] * 8  # White pawns
        self.board[56:64] = ["R", "N", "B", "Q", "K", "B", "N", "R"]  # White pieces
        self.en_passant_possible_file = None
        self.white_can_castle_kingside = False
        self.white_can_castle_queenside = False
        self.black_can_castle_kingside = False
        self.black_can_castle_queenside = False
        self.black_queenside_rook_file = 'a'
        self.white_queenside_rook_file = 'a'
        self.black_kingside_rook_file = 'h'
        self.white_kingside_rook_file = 'h'
        self.position_history = []
        self.game_active = True

    def verify_chess960(self,pieces):
        B1 = pieces.index("B")
        B2 = pieces.index("B", B1 + 1)
        R1 = pieces.index("R")
        R2 = pieces.index("R", R1 + 1)
        K = pieces.index("K")

        if B1 % 2 == B2 % 2:  # Both bishops must be on different colored squares
            return False
        if not (R1 < K < R2):  # King must be between the two rooks
            return False
        return True

    def setup_chess960(self):
        # Set up the chess board for Chess960 (Fischer Random Chess)
        import random
        pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        correct = False
        while not correct:
            random.shuffle(pieces)
            correct = self.verify_chess960(pieces)

        self.board = [""] * 64
        self.board[0:8] = [p.lower() for p in pieces]  # Black pieces
        self.board[8:16] = ["p"] * 8  # Black pawns
        self.board[48:56] = ["P"] * 8  # White pawns
        self.board[56:64] = pieces  # White pieces
        self.en_passant_possible_file = None
        self.white_can_castle_kingside = False
        self.white_can_castle_queenside = False
        self.black_can_castle_kingside = False
        self.black_can_castle_queenside = False
        self.black_queenside_rook_file = chr(pieces.index("R") + ord('a'))
        self.white_queenside_rook_file = chr(pieces.index("R") + ord('a'))
        self.black_kingside_rook_file = chr(pieces.index("R", pieces.index("R") + 1) + ord('a'))
        self.white_kingside_rook_file = chr(pieces.index("R", pieces.index("R") + 1) + ord('a'))
        self.position_history = []
        self.game_active = True

    def get(self, file, rank):
        row = 8 - rank
        col = ord(file) - ord('a')
        if(row < 0 or row > 7 or col < 0 or col > 7):
            # indicate out of bounds access with 'e' for error
            return 'e'
        return self.board[row * 8 + col]

    def set(self, file, rank, piece):
        row = 8 - rank
        col = ord(file) - ord('a')
        if(row < 0 or row > 7 or col < 0 or col > 7):
            raise IndexError(f"Invalid file ({file}) or rank ({rank}) {piece}")
        self.board[row * 8 + col] = piece

    def process_move(self, white_move):
        #### Process the move and update the game state

        # get all legal moves and check for checkmate and stalemate
        legal_candidates = self.get_all_legal_moves(white_move)
        if not legal_candidates:
            # checkmate or stalemate
            if self.is_in_check(white_move):
                print(("0-1" if white_move else "1-0") + "   Checkmate! " + ("Black wins!" if white_move else "White wins!"))
                self.game_active = False
            else:
                print("1/2-1/2   Stalemate! It's a draw!")
                self.game_active = False
            return False
        
        # check for insufficient material (K-K, KB-K, KN-K, KB-KB with bishops on same color)
        if (not any(piece in 'QRPqrp' for piece in self.board) and (sum(piece in 'BbNn' for piece in self.board) <= 1)) or (not any(piece in 'QRNPqrnp' for piece in self.board) and self.board.count('B') == 1 and self.board.count('b') == 1 and self.board.index('B') % 2 == self.board.index('b') % 2):
            print("1/2-1/2   Insufficient material! It's a draw!")
            self.game_active = False
            return False
        
        # threefold repetition check
        if self.position_history.count(self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, white_move]) == 3:
            print("1/2-1/2   Threefold repetition: It's a draw!")
            self.game_active = False
            return False
        
        # check move counter for 50 move rule check
        if (self.move_counter >= 100): # 50 moves each
            print("1/2-1/2   50 move rule: It's a draw!")
            self.game_active = False
            return False

        while True:
            # request input
            print('White to move' if white_move else 'Black to move')
            move = input("Enter your move: ")

            # handle help request
            if move.lower() == 'help':
                self.display_help()
            else:
                break

        # check if move is 'q'/'Q'/'quit' --> quit program
        if move.lower() in ['q', 'quit']:
            print("Quitting program...")
            exit()

        # create placeholders
        src_file = -1
        src_rank = -1
        dest_file = -1
        dest_rank = -1
        promotion = False
        promote_to_piece = -1

        # handle draw offer and resignation
        if re.fullmatch(r'\(=\)', move) or re.fullmatch(r'draw\??', move.lower()):
            # Handle draw offer
            if self.get_draw_response(white_move):
                print("1/2-1/2   Draw by agreement!")
                self.game_active = False
            else:
                print("Draw request not accepted")
            return False

        if re.fullmatch(r'resign\??', move.lower()):
            print(("0-1" if white_move else "1-0") + "   " + ("White resigns. Black wins!" if white_move else "Black resigns. White wins!"))
            self.game_active = False
            return False

        # check for special inputs for castling

        # queenside castling
        if re.fullmatch(r'[oO0]-?[oO0]-?[oO0][+#]?', move):
            if self.is_in_check(white_move):
                print("Illegal Move!")
                return False

            if white_move and self.white_can_castle_queenside:
                king_index = self.board.index("K")
                king_file = chr(ord('a') + king_index % 8)

                rook_file = self.white_queenside_rook_file

                # check legality
                for file_int in range(ord(rook_file) + 1, ord(king_file)):
                    # check if pieces block castling
                    if self.get(chr(file_int), 1) != "":
                        print("Illegal Move!")
                        return False
                    
                    # check if king moves through check
                    if file_int in range(ord('c'), ord(king_file)):
                        backup_board = self.board.copy()
                        self.set(chr(file_int), 1, "K")
                        self.set(king_file, 1, "")
                        if self.is_in_check(white_move):
                            self.board = backup_board
                            print("Illegal Move!")
                            return False
                        self.board = backup_board

                # attempt move
                backup_board = self.board.copy()
                self.set('c', 1, "K")
                self.set(king_file, 1, "")
                self.set('d', 1, "R")
                self.set(rook_file, 1, "")

                if self.is_in_check(white_move):
                    self.board = backup_board
                    print("Illegal Move!")
                    return False

                # can no longer castle
                self.white_can_castle_kingside = False
                self.white_can_castle_queenside = False

                # append board history, increase move counter and return
                self.position_history = self.position_history + [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, not white_move]]
                self.move_counter += 1
                return True

            if not white_move and self.black_can_castle_queenside:
                king_index = self.board.index("k")
                king_file = chr(ord('a') + king_index % 8)

                rook_file = self.black_queenside_rook_file
                
                # check legality
                for file_int in range(ord(rook_file) + 1, ord(king_file)):
                    # check if pieces block castling
                    if self.get(chr(file_int), 8) != "":
                        print("Illegal Move!")
                        return False
                    
                    # check if king moves through check
                    if file_int in range(ord('c'), ord(king_file)):
                        backup_board = self.board.copy()
                        self.set(chr(file_int), 8, "k")
                        self.set(king_file, 8, "")
                        if self.is_in_check(white_move):
                            self.board = backup_board
                            print("Illegal Move!")
                            return False
                        self.board = backup_board

                # attempt move
                backup_board = self.board.copy()
                self.set('c', 8, "k")
                self.set(king_file, 8, "")
                self.set('d', 8, "r")
                self.set(rook_file, 8, "")

                if self.is_in_check(white_move):
                    self.board = backup_board
                    print("Illegal Move!")
                    return False
                 
                # can no longer castle
                self.black_can_castle_kingside = False
                self.black_can_castle_queenside = False

                # append board history, increase move counter and return
                self.position_history = self.position_history + [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, not white_move]]
                self.move_counter += 1
                return True
    
            print("Illegal Move!")
            return False

        # kingside castling
        if re.fullmatch(r'[oO0]-?[oO0][+#]?', move):
            if white_move and self.white_can_castle_kingside:
                king_index = self.board.index("K")
                king_file = chr(ord('a') + king_index % 8)

                rook_file = self.white_kingside_rook_file

                # check legality
                for file_int in range(ord(king_file) + 1, ord(rook_file)):
                    # check if pieces block castling
                    if self.get(chr(file_int), 1) != "":
                        print("Illegal Move!")
                        return False
                    
                    # check if king moves through check
                    if file_int in range(ord(king_file) + 1, ord('h')):
                        backup_board = self.board.copy()
                        self.set(chr(file_int), 1, "K")
                        self.set(king_file, 1, "")
                        if self.is_in_check(white_move):
                            self.board = backup_board
                            print("Illegal Move!")
                            return False
                        self.board = backup_board

                # attempt move
                backup_board = self.board.copy()
                self.set('g', 1, "K")
                self.set(king_file, 1, "")
                self.set('f', 1, "R")
                self.set(rook_file, 1, "")

                if self.is_in_check(white_move):
                    self.board = backup_board
                    print("Illegal Move!")
                    return False

                # can no longer castle
                self.white_can_castle_kingside = False
                self.white_can_castle_queenside = False

                # append board history, increase move counter and return
                self.position_history = self.position_history + [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, not white_move]]
                self.move_counter += 1
                return True

            if not white_move and self.black_can_castle_kingside:
                king_index = self.board.index("k")
                king_file = chr(ord('a') + king_index % 8)

                rook_file = self.black_kingside_rook_file
                
                # check legality
                for file_int in range(ord(king_file) + 1, ord(rook_file)):
                    # check if pieces block castling
                    if self.get(chr(file_int), 8) != "":
                        print("Illegal Move!")
                        return False
                    
                    # check if king moves through check
                    if file_int in range(ord(king_file) + 1, ord('h')):
                        backup_board = self.board.copy()
                        self.set(chr(file_int), 8, "k")
                        self.set(king_file, 8, "")
                        if self.is_in_check(white_move):
                            self.board = backup_board
                            print("Illegal Move!")
                            return False
                        self.board = backup_board

                # attempt move
                backup_board = self.board.copy()
                self.set('g', 8, "k")
                self.set(king_file, 8, "")
                self.set('f', 8, "r")
                self.set(rook_file, 8, "")

                if self.is_in_check(white_move):
                    self.board = backup_board
                    print("Illegal Move!")
                    return False

                # can no longer castle
                self.black_can_castle_kingside = False
                self.black_can_castle_queenside = False

                # append board history, increase move counter and return
                self.position_history = self.position_history + [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, not white_move]]
                self.move_counter += 1
                return True

            print("Illegal Move!")
            return False

        # check for valid algebraic notation
        if not re.fullmatch(r'[KQRBNP]?[a-h]?[1-8]?x?[a-h][1-8][+#]?', move):
            #check if move is a promotion
            if re.fullmatch(r'P?[a-h]?[1-8]?x?[a-h][1-8]=?[QRBN][+#]?', move):
                move = move.replace("=", "")
                promotion = True
            else:
                print("\nInvalid move format! Type 'help' to get a list of allowed syntax")
                return False

        # simplify move notation by removing 'x'/'+'/'#'
        move = move.replace("x", "")
        move = move.replace("+", "")
        move = move.replace("#", "")

        # extract promotion information
        if promotion:
            promote_to_piece = move[-1]
            move = move[:-1]

        # add 'P' for pawn moves without 'P' indicator
        if re.fullmatch(r'[a-h]?[1-8]?[a-h][1-8]', move): move = 'P' + move

        piece = move[0]
        dest_file = move[-2]
        dest_rank = int(move[-1])

        # create error if promotion destination is invalid
        if promotion and dest_rank not in [1, 8]:
            print("Illegal Move!")
            return False

        # remove extracted piece and destination information from move string
        move = move[1:-2]

        # parse for additional source information if provided
        if move:
            if move[0] in 'abcdefgh':
                src_file = move[0]
                move = move[1:]
                if move:
                    src_rank = int(move[0])
            else:
                src_rank = int(move[0])


        # filter for correct piece type
        # also check if move is ambiguous and if provided source information resolves ambiguity
        resolved_candidates = [x for x in legal_candidates if ((src_file == -1 or ord(x[0]) == ord(src_file)) and (src_rank == -1 or x[1] == src_rank) and (x[2] == dest_file) and (x[3] == dest_rank) and (x[4] == piece))]
        if len(resolved_candidates) == 0:
            print("Not a legal move!")
            return False
        if len(resolved_candidates) > 1:
            print("Move is ambiguous, please provide more information!")
            return False
        
        src_file, src_rank, dest_file, dest_rank, piece, en_passant = resolved_candidates[0]

        # detect if en passant is possible for next move, and for which file, required for move validation
        double_pawn_move = (piece == 'P' and abs(src_rank - dest_rank) == 2)
        if double_pawn_move:
            self.en_passant_possible_file = src_file
        else: 
            self.en_passant_possible_file = None

        # reset move counter if move is a pawn move or a capture
        if piece == 'P' or self.get(dest_file, dest_rank) != "":
            self.move_counter = 0


        # make the move
        if en_passant:
            # handle en passant capture
            self.set(dest_file, src_rank, "")

        # handle normal move or promotion
        if promotion: piece = promote_to_piece
        self.set(dest_file, dest_rank, piece if white_move else piece.lower())
        self.set(src_file, src_rank, "")

        # disable castling if corresponding pieces have moved
        if piece == 'K': 
            self.white_can_castle_kingside = False
            self.white_can_castle_queenside = False
        if piece == 'k': 
            self.black_can_castle_kingside = False
            self.black_can_castle_queenside = False
        if self.get(self.white_kingside_rook_file, 1) != 'R': self.white_can_castle_kingside = False
        if self.get(self.white_queenside_rook_file, 1) != 'R': self.white_can_castle_queenside = False
        if self.get(self.black_kingside_rook_file, 1) != 'r': self.black_can_castle_kingside = False
        if self.get(self.black_queenside_rook_file, 1) != 'r': self.black_can_castle_queenside = False

        # append board history, increase move counter and return
        self.position_history = self.position_history + [self.board.copy() + [self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside, self.en_passant_possible_file, not white_move]]
        self.move_counter += 1
        return True
                
    def __repr__(self):        # Return a string representation of the board
        board_str = "\n   a b c d e f g h\n   ---------------\n"
        for rank in range(8,0,-1):
            board_str += str(rank) + " |"
            for file in 'abcdefg':
                piece = self.get(file, rank)
                board_str += piece if piece else "."
                board_str += " "
            piece = self.get('h', rank)
            board_str += piece if piece else "."
            board_str += "| "+ str(rank) + " "
            board_str += "\n"
        board_str += "   ---------------\n   a b c d e f g h\n"
        return board_str
    
    def get_all_legal_moves(self, white_move, ignore_self_checks=False):
        legal_moves = []
        for i in range(64):
            if self.board[i] != "" and self.board[i].isupper() == white_move:
                piece = self.board[i].upper()
                src_file = chr(ord('a') + i % 8)
                src_rank = 8 - (i // 8)

                match piece:
                    case 'P':
                        if white_move:
                            if self.get(src_file, src_rank + 1) == "":
                                legal_moves.append([src_file, src_rank, src_file, src_rank + 1, piece, False])
                                if src_rank == 2 and self.get(src_file, 4) == "":
                                    legal_moves.append([src_file, src_rank, src_file, src_rank + 2, piece, False])
    
                            if self.get(chr(ord(src_file) + 1), src_rank + 1) != '' and self.get(chr(ord(src_file) + 1), src_rank + 1) in "kqrbnp":
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) + 1), src_rank + 1, piece, False])
                            if self.get(chr(ord(src_file) - 1), src_rank + 1) != '' and self.get(chr(ord(src_file) - 1), src_rank + 1) in "kqrbnp":
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) - 1), src_rank + 1, piece, False])

                            if self.get(chr(ord(src_file) + 1), src_rank + 1) == '' and src_rank == 5 and self.en_passant_possible_file == chr(ord(src_file) + 1):
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) + 1), src_rank + 1, piece, True])
                            if self.get(chr(ord(src_file) - 1), src_rank + 1) == '' and src_rank == 5 and self.en_passant_possible_file == chr(ord(src_file) - 1):
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) - 1), src_rank + 1, piece, True])
                        else:
                            if self.get(src_file, src_rank - 1) == "":
                                legal_moves.append([src_file, src_rank, src_file, src_rank - 1, piece, False])
                                if src_rank == 7 and self.get(src_file, 5) == "":
                                    legal_moves.append([src_file, src_rank, src_file, src_rank - 2, piece, False])
    
                            if self.get(chr(ord(src_file) + 1), src_rank - 1) != '' and self.get(chr(ord(src_file) + 1), src_rank - 1) in "KQRBNP":
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) + 1), src_rank - 1, piece, False])
                            if self.get(chr(ord(src_file) - 1), src_rank - 1) != '' and self.get(chr(ord(src_file) - 1), src_rank - 1) in "KQRBNP":
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) - 1), src_rank - 1, piece, False])

                            if self.get(chr(ord(src_file) + 1), src_rank - 1) == '' and src_rank == 4 and self.en_passant_possible_file == chr(ord(src_file) + 1):
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) + 1), src_rank - 1, piece, True])
                            if self.get(chr(ord(src_file) - 1), src_rank - 1) == '' and src_rank == 4 and self.en_passant_possible_file == chr(ord(src_file) - 1):
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) - 1), src_rank - 1, piece, True])

                    case 'N':
                        for file_diff, rank_diff in [(1, 2), (2, 1), (-1, 2), (2, -1), (1, -2), (-2, 1), (-1, -2), (-2, -1)]:
                            if self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff) == "" or (self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff).islower() == white_move and self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff) != 'e'):
                                legal_moves.append([src_file, src_rank, chr(ord(src_file) + file_diff), src_rank + rank_diff, piece, False])

                    case 'B':
                        # down left
                        for i in range(1,min(src_rank, 1 + ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) - i), src_rank - i) != "":
                                if self.get(chr(ord(src_file) - i), src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank - i, piece, False])

                        # down right
                        for i in range(1,min(src_rank, 8 - (ord(src_file) - ord('a')))):
                            if self.get(chr(ord(src_file) + i), src_rank - i) != "":
                                if self.get(chr(ord(src_file) + i), src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank - i, piece, False])

                        # up left
                        for i in range(1,min(9 - src_rank, 1 + ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) - i), src_rank + i) != "":
                                if self.get(chr(ord(src_file) - i), src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank + i, piece, False])

                        # up right
                        for i in range(1,min(9 - src_rank, 8 - (ord(src_file) - ord('a')))):
                            if self.get(chr(ord(src_file) + i), src_rank + i) != "":
                                if self.get(chr(ord(src_file) + i), src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank + i, piece, False])

                    case 'R':
                        # down
                        for i in range(1, src_rank):
                            if self.get(src_file, src_rank - i) != "":
                                if self.get(src_file, src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, src_file, src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, src_file, src_rank - i, piece, False])

                        # up
                        for i in range(1, 9 - src_rank):
                            if self.get(src_file, src_rank + i) != "":
                                if self.get(src_file, src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, src_file, src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, src_file, src_rank + i, piece, False])

                        # left
                        for i in range(1, 1 + ord(src_file) - ord('a')):
                            if self.get(chr(ord(src_file) - i), src_rank) != "":
                                if self.get(chr(ord(src_file) - i), src_rank).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank, piece, False])

                        # right
                        for i in range(1, 8 - (ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) + i), src_rank) != "":
                                if self.get(chr(ord(src_file) + i), src_rank).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank, piece, False])

                    case 'Q':
                        # bishop moves
                        # down left
                        for i in range(1,min(src_rank, 1 + ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) - i), src_rank - i) != "":
                                if self.get(chr(ord(src_file) - i), src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank - i, piece, False])

                        # down right
                        for i in range(1,min(src_rank, 8 - (ord(src_file) - ord('a')))):
                            if self.get(chr(ord(src_file) + i), src_rank - i) != "":
                                if self.get(chr(ord(src_file) + i), src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank - i, piece, False])

                        # up left
                        for i in range(1,min(9 - src_rank, 1 + ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) - i), src_rank + i) != "":
                                if self.get(chr(ord(src_file) - i), src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank + i, piece, False])

                        # up right
                        for i in range(1,min(9 - src_rank, 8 - (ord(src_file) - ord('a')))):
                            if self.get(chr(ord(src_file) + i), src_rank + i) != "":
                                if self.get(chr(ord(src_file) + i), src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank + i, piece, False])

                        # rook moves
                        # down
                        for i in range(1, src_rank):
                            if self.get(src_file, src_rank - i) != "":
                                if self.get(src_file, src_rank - i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, src_file, src_rank - i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, src_file, src_rank - i, piece, False])

                        # up
                        for i in range(1, 9 - src_rank):
                            if self.get(src_file, src_rank + i) != "":
                                if self.get(src_file, src_rank + i).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, src_file, src_rank + i, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, src_file, src_rank + i, piece, False])

                        # left
                        for i in range(1, 1 + ord(src_file) - ord('a')):
                            if self.get(chr(ord(src_file) - i), src_rank) != "":
                                if self.get(chr(ord(src_file) - i), src_rank).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) - i), src_rank, piece, False])

                        # right
                        for i in range(1, 8 - (ord(src_file) - ord('a'))):
                            if self.get(chr(ord(src_file) + i), src_rank) != "":
                                if self.get(chr(ord(src_file) + i), src_rank).islower() == white_move:
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank, piece, False])
                                break
                            legal_moves.append([src_file, src_rank, chr(ord(src_file) + i), src_rank, piece, False])

                    case 'K':
                        for file_diff in range(-1, 2):
                            for rank_diff in range(-1, 2):
                                if file_diff == 0 and rank_diff == 0:
                                    continue
                                if self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff) == "" or (self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff).islower() == white_move and self.get(chr(ord(src_file) + file_diff), src_rank + rank_diff) != 'e'):
                                    legal_moves.append([src_file, src_rank, chr(ord(src_file) + file_diff), src_rank + rank_diff, piece, False])

        if ignore_self_checks: return legal_moves

        # test for self checks or kings being captured
        legal_moves_copy = legal_moves.copy()
        for move in legal_moves_copy:
            src_file, src_rank, dest_file, dest_rank, piece, en_passant = move
            
            backup_board = self.board.copy()

            if en_passant:
                self.set(dest_file, src_rank, "")
            self.set(dest_file, dest_rank, self.get(src_file, src_rank))
            self.set(src_file, src_rank, "")
            
            if not ('K' in self.board and 'k' in self.board):
                legal_moves.remove(move)

            if self.is_in_check(white_move):
                legal_moves.remove(move)

            self.board = backup_board
 
        return legal_moves
    
    def is_in_check(self, is_white):
        if is_white:
            king_index = self.board.index("K")
        else:
            king_index = self.board.index("k")

        king_file = chr(ord('a') + king_index % 8)
        king_rank = 8 - (king_index // 8)

        for move in self.get_all_legal_moves(not is_white, ignore_self_checks = True):
            if move[2] == king_file and move[3] == king_rank:
                return True
        return False

    def handle_help(self):
        print('List of allowed commands:')
        print('\'help\':\n\tDisplays this list\n')
        print('\'(=)\', \'=\', \'draw\':\n\tOffer Draw\n')
        print('\'resign\':\n\tResign from the game\n')
        print('\'O-O\', \'OO\':\n\tKingside Castle\n')
        print('\'O-O-O\', \'OOO\':\n\tQueenside Castle\n')
        print('Other moves should be inputted in algebraic notation:')
        print('\tFirst letter --> Piece Type (KQRBN) or either \'P\' or nothing for pawn moves')
        print('\tNext are optional specifiers of source file, then source rank in case of ambiguous moves')
        print('\tAfter that is an optional \'x\' to indicate captures')
        print('\tNext is file, then rank of the destination')
        print('\tIf promoting, now add \'=Q\' to indicate promotion to queen. (RBN) are also possible')
        print('\tOptional indicators for check \'+\' or checkmate \'#\' can be added to the end')


if __name__ == '__main__':

    print("\n\n\nChess Engine Initialized\n")
    game = ChessEngine()

    while True:

        resp = -1
        while True:
            print("What gamemode do you want to play?")
            print("1: Classic")
            print("2: Chess960")
            print("3: Rook Endgame")
            print("q: Quit Program")
            resp = input("Please input your choice: ")
            if resp.lower() in ['q', 'quit']:
                print("Quitting program...")
                exit()

            if int(resp) not in range(1,4):
                print("Not a valid input\n")
            else: 
                break

        match int(resp):
            case 1:
                game.setup_normal()
            case 2:
                game.setup_chess960()
            case 3:
                # TODO implement rook_endgame
                rook_endgame(game)
            
                continue
    
        enable_clock = False
        resp = -1
        while True:
            resp = input("\n Do you want to enable a chess clock? (y/n): ")

            if resp.lower() in ['q', 'quit']:
                print("Quitting program...")
                exit()

            if resp.lower() in ['y', 'yes']:
                # Enable chess clock
                enable_clock = True
                break
            if resp.lower() in ['n', 'no']:
                # Do not enable chess clock
                enable_clock = False
                break

            print("Not a valid input, please try again or type 'q' to quit\n")
    
    
        # Start the game
        white_move = True
        first_move = True
        game.position_history = game.position_history + [game.board.copy() + [game.white_can_castle_kingside, game.white_can_castle_queenside, game.black_can_castle_kingside, game.black_can_castle_queenside, game.en_passant_possible_file, white_move]]

        # game loop
        while game.game_active:
            # start clock if enabled
            if enable_clock and not first_move and white_move:
                # TODO start timer, replace the 'pass' instruction with your function
                pass
            first_move = False

            # print board and process move
            print(game)
            valid = game.process_move(white_move)
            

            # switch side
            if valid: white_move = not white_move

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

