from copy import deepcopy
from pprint import pprint

RED = '\033[31m'
GREEN = '\033[32m'
NORMAL = '\033[0m'

class LogEntry:
    def __init__(self, board, from_row, from_col, to_row, to_col, promotion_piece=None):
        self.board = board
        self.move = [from_row, from_col, to_row, to_col]
        if promotion_piece:
            self.move = self.move + [promotion_piece]

    def get_board(self):
        return self.board

    def get_move(self):
        return self.move

    def get_color(self):
        return self.board.get_color(self.board.get_piece(self.move[0], self.move[1]))

    def get_board_array(self):
        return self.board.board

    # put board in terms of the player rather than by color
    # i.e. make whichever color is making move capitalized
    # flip board such that player's king is below and to the left of opponent's king
    def normalized_board_str(self):
        reference_board = self.get_board_array()
        normalized_board =  deepcopy(self.get_board_array())

        color = self.get_color()

        # swap colors
        if color == 'black':
            for row in range(8):
                for col in range(8):
                    ref_piece = reference_board[row][col]
                    if ref_piece == '':
                        continue
                    if ref_piece.islower():
                        normalized_board[row][col] = ref_piece.upper()
                    else:
                        normalized_board[row][col] = ref_piece.lower()

        # flip board vertically if the player's king is above the opponent's king
        if self.board.king_loc(color)[0] < self.board.king_loc(self.board.opposite_color(color))[0]:
            normalized_board = normalized_board[::-1]
        # flip board horizontally if player's king is to the right of the opponent's king
        if self.board.king_loc(color)[1] > self.board.king_loc(self.board.opposite_color(color))[1]:
            for row in range(8):
                normalized_board[row] = normalized_board[row][::-1]

        return self.compressed_board_string(normalized_board)

    # flip move so based on same criteria as board (based off king position)
    def normalized_move(self):
        color = self.get_color()
        if self.move is None:
            return None
        norm_move = deepcopy(self.move)
        # flip move vertically if the player's king is above the opponent's king
        if self.board.king_loc(color)[0] < self.board.king_loc(self.board.opposite_color(color))[0]:
            norm_move[0] = 7 - self.move[0]
            norm_move[2] = 7 - self.move[2]
        # flip move horizontally if player's king is to the right of the opponent's king
        if self.board.king_loc(color)[1] > self.board.king_loc(self.board.opposite_color(color))[1]:
            norm_move[1] = 7 - self.move[1]
            norm_move[3] = 7 - self.move[3]

        return norm_move

    def __eq__(self, other):
        return self.board == other.board and self.move == other.move

    # compress to a string for storage
    @staticmethod
    def compressed_board_string(board_array):
        comp_board = ''

        empty_space_count = 0
        for row in board_array:
            for piece in row:
                if piece == '':
                    empty_space_count += 1
                else:
                    if empty_space_count > 0:
                        comp_board += str(empty_space_count)
                        empty_space_count = 0
                    comp_board += piece

        return comp_board

    @staticmethod
    def compressed_move_str(move):
        move_str = ''
        for char in move:
            move_str += str(char)
        return move_str

class BoardLog:

    def __init__(self):
        self.log = []

    def add_entry(self, board, from_row, from_col, to_row, to_col, promotion_piece=None):
        self.log.append(LogEntry(board, from_row, from_col, to_row, to_col, promotion_piece))
        # self.print_entry()
        # self.print_compressed_array()
        # self.print_normalized_array()
        # self.print_normalized_move()

    # remove last entry. Useful for undoing moves
    def pop_entry(self):
        self.log.pop()

    def get_log(self):
        return self.log

    def prepare_data(self, winner):
        data = []
        for entry in self.log:
            board_str = entry.normalized_board_str()
            move_str = LogEntry.compressed_move_str(entry.normalized_move())

            color = entry.get_color()
            win = 1 if color == winner else 0
            loss = 1 if color == 'black' and winner == 'white' or color == 'white' and winner == 'black' else 0
            draw = 1 if winner == 'draw' else 0

            new_entry = {'board': board_str, 'moves': [{'id': move_str, 'win': win, 'loss': loss, 'draw': draw}]}
            self.merge_log_into_list(new_entry, data)

        # --- Remove checkmating entry. Has no use in the database because bot can find checkmates by itself
        data.pop()
        return data

    # merges two board logs
    @staticmethod
    def merge_log_into_list(new_entry, log_list):
        new_move_data = new_entry['moves'][0]
        new_entry_board_str = new_entry['board']

        # --- Check if board exists in log ---
        board_matched = False
        for logged_board in log_list:
            if logged_board['board'] == new_entry_board_str:
                board_matched = True
                # --- Check if move exists in matched board ---
                move_matched = False
                for logged_move in logged_board['moves']:
                    if logged_move['id'] == new_move_data['id']:
                        # add result data to matched move records
                        logged_move['win'] += new_move_data['win']
                        logged_move['loss'] += new_move_data['loss']
                        logged_move['draw'] += new_move_data['draw']
                        move_matched = True
                        break
                if not move_matched:
                    logged_board['moves'].append(new_move_data)
                break

        if not board_matched:
            log_list.append(new_entry)



    def is_draw(self, curr_board):
        # False if less than 3 turns
        if len(self.log) < 7:
            return False

        # Threefold repetition
        match_count = 0
        for log_entry in self.log:
            if curr_board == log_entry.get_board():
                match_count += 1
        if match_count >= 2:
            return True

        # 50 move rule
        if len(self.log) >= 100:
            boring_move_count = 0
            for i, log_entry in enumerate(reversed(self.log)):
                board = log_entry.get_board()
                move = log_entry.get_move()
                moved_piece = board.get_piece(move[0], move[1])
                target_piece = board.get_piece(move[2], move[3])
                if moved_piece.lower() == 'p' or target_piece != '':
                    break
                boring_move_count += 1
            if boring_move_count >= 100:
                return True

        # Insufficient material
        white_pieces = []
        black_pieces = []
        for row in curr_board.board:
            for piece in row:
                if piece == '':
                    continue
                if piece.isupper():
                    white_pieces.append(piece)
                else:
                    black_pieces.append(piece)
        #
        if len(white_pieces) <= 2 and all(i not in white_pieces for i in ['Q', 'R', 'P']) \
                and len(black_pieces) <= 2 and all(i not in black_pieces for i in ['q', 'r', 'p']):
            return True
        if (white_pieces == ['K'] and black_pieces == ['k', 'n', 'n']) \
            or (white_pieces == ['K', 'N', 'N'] and black_pieces == ['k']):
            return True

        return False

    # prints board to console. Debug tool only. Will look "delayed" compared to live game because
    # one log entry stores the board state and what move was made from there and not
    # the result of the move
    def print_entry(self, entry=-1):
        curr_board = self.log[entry].get_board_array()
        curr_move = self.log[entry].get_move()

        for row, full_row in enumerate(curr_board):
            for col, piece in enumerate(full_row):

                if piece == '':
                    piece = '*'
                color = NORMAL
                if row == curr_move[0] and col == curr_move[1]:
                    color = RED
                elif row == curr_move[2] and col == curr_move[3]:
                    color = GREEN
                print(f'{color}{piece}', end=' ')
            print()
        print()

    def print_compressed_array(self, entry=-1):
        comp_array = LogEntry.compressed_board_string(self.log[entry].get_board_array())
        pprint(f'{comp_array}: length: {len(comp_array)}')

    def print_normalized_board_str(self, entry=-1):
        log_entry = self.log[entry]
        board = log_entry.get_board()
        move = log_entry.get_move()
        color = board.get_color(board.get_piece(move[0], move[1]))
        norm_array = self.log[entry].normalized_board_str()
        pprint(norm_array)

    def print_normalized_move(self, entry=-1):
        log_entry = self.log[entry]
        board = log_entry.get_board()
        move = log_entry.get_move()
        color = board.get_color(board.get_piece(move[0], move[1]))
        norm_move = self.log[entry].normalized_move()
        print(move)
        print(norm_move)
