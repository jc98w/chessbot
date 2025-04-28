RED = '\033[31m'
GREEN = '\033[32m'
NORMAL = '\033[0m'

class LogEntry:
    def __init__(self, board, from_row, from_col, to_row, to_col):
        self.board = board
        self.move = (from_row, from_col, to_row, to_col)

    def get_board(self):
        return self.board

    def get_move(self):
        return self.move

    def get_board_array(self):
        return self.board.board


class BoardLog:

    def __init__(self):
        self.log = []

    def add_entry(self, board, from_row, from_col, to_row, to_col):
        self.log.append(LogEntry(board, from_row, from_col, to_row, to_col))
        self.print_entry()

    # remove last entry. Useful for undoing moves
    def pop_entry(self):
        self.log.pop()

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
