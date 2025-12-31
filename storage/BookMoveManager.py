"""
Moves are stored in SQLite table.
Table book
Columns board_id (int primary key), moves (varchar)
* Book moves input in database are referenced from
* Silman, J. (1998). 'The Complete Book of Chess Strategy: GrandMaster Techniques from A to Z' Siles Press
"""
import re
import sqlite3
from pathlib import Path
from components.Board import Board

# format of traditional chess moves (e6, qxh1, ...)
MOVE_FORMAT = re.compile(r"""
    ^(?P<piece>[rbnkq])?
    (?P<from>[a-h1-8])?
    (?P<x>x)?
    (?P<dest>[a-h][1-8])
    (?P<promotion>[rbkq])?$
""", re.VERBOSE)

def convert_square(square: str):
    """ Converts rank, file pair (e4) to row, col pair"""
    try:
        square = square.lower()
        col = ord(square[0]) - ord('a')
        row = 8 - int(square[1])
        if col < 0 or 7 < col or row < 0 or 7 < row:
            raise IndexError
        return row, col
    except (AttributeError, ValueError, IndexError):
        return None, None

def convert_move(board, trad_move, color):
    """ Converts from traditional form (e4, kxe6) to program's format [2, 3, 3, 3]
        This method does not necessarily care if the move is valid """
    trad_move = trad_move.lower()
    match_move = MOVE_FORMAT.match(trad_move)
    if not match_move:
        # Check for castling / invalid moves
        match trad_move:
            case '0-0':
                if color == 'white':
                    return [7, 4, 7, 6]
                elif color == 'black':
                    return [0, 4, 0, 6]
            case '0-0-0':
                if color == 'white':
                    return [7, 4, 7, 2]
                elif color == 'black':
                    return [0, 4, 0, 2]
            case _:
                raise Exception('Invalid move cannot be converted')

    for group in ('piece', 'from', 'x', 'dest', 'promotion'):
        print(f'{group}: {match_move.group(group)}')

    piece = match_move.group('piece')
    if piece and color == 'white':
        piece = piece.upper()
    from_loc = match_move.group('from')
    dest = match_move.group('dest')
    from_row, from_col = convert_square(from_loc)   # Will often be None, None
    to_row, to_col = convert_square(dest)           # Will always exist
    promo = match_move.group('promotion')           # Probably won't appear for book moves

    # Return if provided enough information
    if from_row and from_col and to_row and to_col:
        return from_row, from_col, to_row, to_col, promo

    search_range = range(7, -1, -1) if color == 'white' else range(8)   # Search from the bottom if color is white
    # Find starting location
    for row in search_range:
        if from_row and from_row != row:
            # if row is listed, only check that row
            continue
        for col in search_range:
            if from_col and from_col != col:
                # if col is listed, only check that col
                continue
            test_piece = board.get_piece(row, col)
            if board.get_color(test_piece) == color and \
                    (test_piece == piece or (piece is None and test_piece in ('p', 'P'))):
                if (to_row, to_col) in board.get_valid_moves(row, col):
                    return [row, col, to_row, to_col, promo]

    # Return None if nothing was found
    return None


class BookMoveManager:
    def __init__(self):
        self._book = None
        self._cursor = None

    def connect(self):
        """ Connects to the SQLite database """

        path = 'bookmoves.db' if Path('bookmoves.db').exists() else 'storage/bookmoves.db'
        self._book = sqlite3.connect(path)
        self._cursor = self._book.cursor()

    def close(self):
        self._book.close()

    def add_line(self, line: str):
        """ Incorporates a line into the database """
        board = Board()
        moves = line.split()
        color = 'white'
        for trad_move in moves:
            move = convert_move(board, trad_move, color)
            color = 'black' if color == 'white' else 'white'
            board_str = board.create_board_str()
            if not board.move_piece(*move):
                print(f'Line not added due to invalid move: {trad_move}')
                return
            # Add move to existing entry if it is not present
            params = {'id': board_str, 'move': trad_move, '_move': ' ' + trad_move}
            self._cursor.execute("""INSERT INTO book VALUES (:id, :move)
                                    ON CONFLICT(board_id)
                                    DO UPDATE SET moves = moves || :_move
                                    WHERE INSTR(moves, :move) = 0"""
                                    ,params)
            print(f'Entry {board_str} updated')
        self._book.commit()

    def get_moves(self, board_str):
        """ Retrieves list of moves for a given board """
        self._cursor.execute("SELECT moves FROM book WHERE board_id = ?", (board_str, ))
        try:
            return self._cursor.fetchone()[0].split()
        except TypeError:
            return None
