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

    def pick_best_db_move(self):
        if self.db_manager is None:
            return None
        move = None
        matching_board = self.db_manager.read({'board':self.board.normalized_board_str(self.color)})
        if matching_board is None:
            return None
        else:
            best_move = [None, -1]
            # getting move -ex.{id:'0003', win:10, draw:3, loss:3}
            for move in matching_board['moves']:
                win_percent = move['win'] / (move['win'] + move['loss'] + move['draw'])
                print(f'{move["id"]}: {win_percent}')
                if win_percent > best_move[1]:
                    best_move = [move['id'], win_percent]
            move = [int(best_move[0][0]), int(best_move[0][1]), int(best_move[0][2]), int(best_move[0][3])]
            if len(best_move) == 5:
                move += best_move[0][4]
            # don't bother with crappy move
            if best_move[1] < 0.4:
                return None

        # --- translate normalized more to actual move ---
        # --- if opposing king is above player king, vertically flip move
        if self.board.king_loc(self.color)[0] < self.board.king_loc(self.board.opposite_color(self.color))[0]:
            move[0] = 7 - move[0]
            move[2] = 7 - move[2]
        # --- if opposing king is to the right of player king, horizontally flip move
        if self.board.king_loc(self.color)[1] > self.board.king_loc(self.board.opposite_color(self.color))[1]:
            move[1] = 7 - move[1]
            move[3] = 7 - move[3]

        return move

