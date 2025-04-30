from copy import deepcopy
from pprint import pprint

RED = '\033[31m'
GREEN = '\033[32m'
NORMAL = '\033[0m'

class LogEntry:
    def __init__(self, board, from_row, from_col, to_row, to_col, promotion_piece=None):
        self.board = board
        self.move = (from_row, from_col, to_row, to_col)
        if promotion_piece:
            self.move = self.move + (promotion_piece,)

    def get_board(self):
        return self.board

    def get_move(self):
        return self.move

    def get_board_array(self):
        return self.board.board

    # Translate entry to storable format
    def compress_entry(self):
        comp_board = deepcopy(self.get_board_array())

        # remove empty rows
        while [''] * 8 in comp_board:
            comp_board.remove([''] * 8)
        # Trim excess from rows
        for row in comp_board:
            for i in range(7, 0, -1):
                print(i)
                if row[i] == '':
                    row.pop()
                else:
                    break

        return comp_board

class BoardLog:

    def __init__(self):
        self.log = []
        self.winner = None

    def add_entry(self, board, from_row, from_col, to_row, to_col):
        self.log.append(LogEntry(board, from_row, from_col, to_row, to_col))
        # self.print_entry()
        #self.print_compressed_array()

    # remove last entry. Useful for undoing moves
    def pop_entry(self):
        self.log.pop()

    def get_log(self):
        return self.log

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
        pprint(self.log[entry].compress_entry())
