import random

from storage.DatabaseManager import DatabaseManager

class ChessBot:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.board = None
        self.color = None

    def decide_move(self, board, color):
        self.board = board
        self.color = color


        move = self.search_for_checkmate()
        if move is None:
            move = self.pick_best_db_move()
            if move is None:
                move = self.pick_random_move()

        return move

    def pick_random_move(self):
        bot_piece_locations = self.board.get_piece_locations(self.color)
        random.shuffle(bot_piece_locations)
        move = None
        for loc in bot_piece_locations:
            valid_moves = self.board.get_valid_moves(loc[0], loc[1])
            if len(valid_moves) > 0:
                move = loc + random.choice(valid_moves)
                break
        # print(f'picking move: {move}')
        if move is None:
            return None
        else:
            piece = self.board.get_piece(move[0], move[1])
            if piece.lower() == 'p' and (move[2] == 0 or move[2] == 7):
                move += (random.choice(['q', 'r', 'b', 'n']),)
            return move

    def search_for_checkmate(self):
        piece_locations = self.board.get_piece_locations(self.color)
        for loc in piece_locations:
            valid_moves = self.board.get_valid_moves(loc[0], loc[1])
            for to_loc in valid_moves:
                attacker_piece = self.board.get_piece(loc[0], loc[1])
                if self.board.move_delivers_check(attacker_piece, loc[0], loc[1], *to_loc, mate=True):
                    return loc + to_loc
        return None

    # FIXME
    def pick_best_db_move(self):
        if self.db_manager is None:
            return None
        move = None
        return move

