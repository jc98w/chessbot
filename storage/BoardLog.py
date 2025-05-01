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

    def get_board_array(self):
        return self.board.board

    # put board in terms of the player rather than by color
    # i.e. make whichever color is making move capitalized
    # flip board such that player's king is below and to the left of opponent's king
    def normalized_board_array(self, color):
        reference_board = self.get_board_array()
        normalized_board =  deepcopy(self.get_board_array())

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

        return normalized_board


    # flip move so based on same criteria as board (based off king position)
    def normalized_move(self, color):
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
    def compressed_board_array(self):
        comp_board = ''

        empty_space_count = 0
        for row in self.get_board_array():
            for piece in row:
                if piece == '':
                    empty_space_count += 1
                else:
                    if empty_space_count > 0:
                        comp_board += str(empty_space_count)
                        empty_space_count = 0
                    comp_board += piece

        return comp_board

    def compressed_move(self):
        move_str = ''
        for char in self.move:
            move_str += char
        return move_str



class BoardLog:

    def __init__(self):
        self.log = []
        self.winner = None

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
        comp_array = self.log[entry].compressed_board_array()
        pprint(f'{comp_array}: length: {len(comp_array)}')

    def print_normalized_array(self, entry=-1):
        log_entry = self.log[entry]
        board = log_entry.get_board()
        move = log_entry.get_move()
        color = board.get_color(board.get_piece(move[0], move[1]))
        norm_array = self.log[entry].normalized_board_array(color)
        pprint(norm_array)

    def print_normalized_move(self, entry=-1):
        log_entry = self.log[entry]
        board = log_entry.get_board()
        move = log_entry.get_move()
        color = board.get_color(board.get_piece(move[0], move[1]))
        norm_move = self.log[entry].normalized_move(color)
        print(move)
        print(norm_move)
