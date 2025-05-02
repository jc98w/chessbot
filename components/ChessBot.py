import random
from copy import deepcopy

from storage.DatabaseManager import DatabaseManager

class ChessBot:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.board = None
        self.color = None
        self.piece_locations = None

    def decide_move(self, board, color):
        self.board = board
        self.color = color
        self.piece_locations = self.board.get_piece_locations(self.color)

        move = self.search_for_checkmate()
        if move is None:
            move = self.pick_best_db_move()
            if move is None:
                move = self.pick_random_move()

        return move

    def pick_random_move(self):
        random.shuffle(self.piece_locations)
        move = None
        for loc in self.piece_locations:
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
        for loc in self.piece_locations:
            valid_moves = self.board.get_valid_moves(loc[0], loc[1])
            for to_loc in valid_moves:
                attacker_piece = self.board.get_piece(loc[0], loc[1])
                if self.board.move_delivers_check(attacker_piece, loc[0], loc[1], *to_loc, mate=True):
                    print(f'{self.color} found checkmate at {loc + to_loc}')
                    return loc + to_loc
        return None

    def pick_best_db_move(self):
        if self.db_manager is None:
            return None

        move_to_play_str = None
        matching_board = self.db_manager.read({'board':self.board.normalized_board_str(self.color)})
        if matching_board is None:
            return None
        else:
            moves_seen_ratings = []
            # getting move -ex.{id:'0003', win:10, draw:3, loss:3}
            for move in matching_board['moves']:
                times_played = move['win'] + move['loss'] + move['draw']
                win_percent = move['win'] / times_played
                # --- this rating system weighs the moves based on winning percentage with higher credibility given ---
                # --- as the move is played more times ---
                rating = 0.5 + ((win_percent - 0.5) * times_played / (times_played + 1))
                moves_seen_ratings.append((move['id'], rating))
            moves_seen_ratings = sorted(moves_seen_ratings, key=lambda x: x[1], reverse=True)

            move_to_play_odds = None
            for move in moves_seen_ratings:
                if random.random() < move[1]:
                    move_to_play_str = move[0]
                    move_to_play_odds = move[1]
                    break
                else:
                    print(f'\t{self.color} rejected move {move[0]} with odds {move[1]:.2f}')

        # --- convert move to list of ints instead of string, may string at end for promotion piece ---
        move_to_play = []
        if move_to_play_str is None:
            sabotage_attempt = self.pick_best_sabotage()
            if sabotage_attempt is not None:
                return sabotage_attempt
            else:
                prev_moves = []
                for move in moves_seen_ratings:
                    move = move[0]
                    seen_move = []
                    for char in move:
                        seen_move.append(int(char)) if char.isdigit() else seen_move.append(char)
                    prev_moves.append(seen_move)
                return self.try_new_move(prev_moves)

        for char in move_to_play_str:
            move_to_play.append(int(char)) if char.isdigit() else move_to_play.append(char)

        # --- translate normalized more to actual move ---
        # --- if opposing king is above player king, vertically flip move
        if self.board.king_loc(self.color)[0] < self.board.king_loc(self.board.opposite_color(self.color))[0]:
            move_to_play[0] = 7 - move_to_play[0]
            move_to_play[2] = 7 - move_to_play[2]
        # --- if opposing king is to the right of player king, horizontally flip move
        if self.board.king_loc(self.color)[1] > self.board.king_loc(self.board.opposite_color(self.color))[1]:
            move_to_play[1] = 7 - move_to_play[1]
            move_to_play[3] = 7 - move_to_play[3]

        print(f'{self.color} found move {move_to_play}; winning odds: {move_to_play_odds}')
        return move_to_play

    # instead of looking for a move that results in a good chance of winning, look for a move that puts opponent
    # in the position with the worst chance of success
    def pick_best_sabotage(self):
        if self.db_manager is None:
            return None

        # --- for each of player's pieces ---
        for loc in self.piece_locations:
            valid_moves = self.board.get_valid_moves(*loc)
            # --- for each of the piece's valid moves ---
            for to_loc in valid_moves:
                # --- find resulting opponent's position in the db ---
                test_board = deepcopy(self.board)
                test_board.move_piece(*loc, *to_loc)
                test_board_str = test_board.normalized_board_str(self.board.opposite_color(self.color))
                opp_board = self.db_manager.read({'board':test_board_str})
                # --- if the board wasn't in the db, consider it 50-50 ---
                if opp_board is None:
                    continue
                else:
                    # --- Find opponent's best odds of winning from the resulting position ---
                    opp_best_odds = -1
                    for opp_move in opp_board['moves']:
                        times_played = opp_move['win'] + opp_move['draw'] + opp_move['loss']
                        opp_win_odds = opp_move['win'] / times_played
                        if opp_win_odds > opp_best_odds:
                            opp_best_odds = opp_win_odds
                    if random.random() > opp_best_odds:
                        move_to_play = list(loc + to_loc)
                        # --- translate normalized more to actual move ---
                        # --- if opposing king is above player king, vertically flip move
                        if self.board.king_loc(self.color)[0] < self.board.king_loc(self.board.opposite_color(self.color))[0]:
                            move_to_play[0] = 7 - move_to_play[0]
                            move_to_play[2] = 7 - move_to_play[2]
                        # --- if opposing king is to the right of player king, horizontally flip move
                        if self.board.king_loc(self.color)[1] > self.board.king_loc(self.board.opposite_color(self.color))[1]:
                            move_to_play[1] = 7 - move_to_play[1]
                            move_to_play[3] = 7 - move_to_play[3]
                        print(f'{self.color} found move {move_to_play}; opponent best found odds of winning {opp_best_odds:.2f}')
                        return move_to_play
                    else:
                        print(f'\t{self.color} rejected move {loc + to_loc}; opponent best found odds of winning {opp_best_odds:.2f}')

        return None


    def try_new_move(self, prev_moves):
        print('{self.color} Trying new move.', end=' ')
        valid_moves = []
        for loc in self.piece_locations:
            loc_moves = self.board.get_valid_moves(*loc)
            for move in loc_moves:
                if move not in prev_moves:
                    valid_moves.append(loc + move)
        if len(valid_moves) == 0:
            print('No new move found')
            return None
        move = random.choice(valid_moves)
        print(f'Found new move {move}')
        return move

