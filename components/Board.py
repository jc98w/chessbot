from copy import deepcopy
# from pprint import pprint

class Board:

    def __init__(self, reverse=False):
        self.board = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
                      ['p'] * 8,
                      [''] * 8,
                      [''] * 8,
                      [''] * 8,
                      [''] * 8,
                      ['P'] * 8,
                      ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]

        # indicates direction for pawn movement
        self.white_direction = -1
        self.black_direction = 1
        self.white_castling_rights = 'kq'
        self.black_castling_rights = 'kq'
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)

        # indicates pawn double jump used to determine if en passant is legal
        self.double_move_col = None

    def set_board(self, board):
        self.board = board

    def get_piece(self, row, col):
        return self.board[row][col]

    def king_loc(self, color):
        return self.white_king_loc if color == 'white' else self.black_king_loc

    def set_king_loc(self, color, row, col):
        if color == 'white':
            self.white_king_loc = (row, col)
        elif color == 'black':
            self.black_king_loc = (row, col)

    def get_castling_rights(self, color):
        return self.white_castling_rights if color == 'white' else self.black_castling_rights

    def set_castling_rights(self, color, state):
        if color == 'white':
            self.white_castling_rights = state
        elif color == 'black':
            self.black_castling_rights = state

    # Returns list of valid moves for a given piece
    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        match piece:
            case 'P' | 'p':
                pseudo_valid_moves = self.valid_pawn_move(piece, row, col)
            case 'R' | 'r':
                pseudo_valid_moves = self.valid_rook_move(piece, row, col)
            case 'N' | 'n':
                pseudo_valid_moves = self.valid_knight_move(piece, row, col)
            case 'B' | 'b':
                pseudo_valid_moves = self.valid_bishop_move(piece, row, col)
            case 'Q' | 'q':
                pseudo_valid_moves = self.valid_queen_move(piece, row, col)
            case 'K' | 'k':
                pseudo_valid_moves = self.valid_king_move(piece, row, col)
            case _:
                return []

        valid_moves = []
        for move in pseudo_valid_moves:
            if not self.move_causes_check(piece, row, col, move[0], move[1]):
                valid_moves.append(move)

        return valid_moves

    # Moves a piece from one square to another
    # Checks for validity by default
    def move_piece(self, from_row, from_col, to_row, to_col, force=False):
        piece = self.board[from_row][from_col]
        color = self.get_color(piece)

        # return False for invalid moves
        if piece == '':
            return False
        if not force and (to_row, to_col) not in self.get_valid_moves(from_row, from_col):
            return False

        self.double_move_col = None
        match piece:
            case 'K' | 'k':
                self.set_king_loc(color, to_row, to_col)
                self.set_castling_rights(color, '')
                self.white_castling_rights = ''
                # castling
                if abs(from_col - to_col) > 1:
                    if from_col < to_col:
                        self.move_piece(from_row, 7, from_row, 5, force=True)
                    else:
                        self.move_piece(from_row, 0, from_row, 3, force=True)
            case 'r' | 'R':
                rights = self.get_castling_rights(color)
                if from_col == 0 and 'q' in rights:
                    self.set_castling_rights(color, rights.replace('q', ''))
                if from_col == 7 and 'k' in rights:
                    self.set_castling_rights(color, rights.replace('k', ''))
            case 'P' | 'p':
                if abs(from_row - to_row) == 2:
                    self.double_move_col = from_col
                # if en passant
                if abs(from_col - to_col) == 1 and abs(from_row - to_row) == 1 and self.double_move_col == to_col:
                    # this move captures the intercepted pawn
                    self.move_piece(from_row, from_col, from_row, to_col, force=True)
                    # this move puts pawn into correct spot
                    self.move_piece(from_row, to_col, to_row, to_col, force=True)

        # move piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        return True

    # returns the direction for pawns
    def get_direction(self, piece):
        if piece.isupper():
            return self.white_direction
        else:
            return self.black_direction

    # returns whether two pieces are opposing colors
    @staticmethod
    def opposing_player(piece1, piece2):
        if piece1.isupper() and piece2.islower():
            return True
        elif piece1.islower() and piece2.isupper():
            return True
        else:
            return False

    # returns the color of a piece
    @staticmethod
    def get_color(piece):
        if piece.isupper():
            return 'white'
        else:
            return 'black'

    # returns the opposite color of a color
    @staticmethod
    def opposite_color(color):
        if color == 'white':
            return 'black'
        else:
            return 'white'

    # returns list of valid pawn moves
    def valid_pawn_move(self, piece, row, col):
        valid_moves = []
        direction = self.get_direction(piece)

        # straight ahead moves
        if (direction == row or direction == -1 and row == 6) \
            and self.get_piece(row + direction, col) == ''\
            and self.get_piece(row + 2 * direction, col) == '':
            valid_moves.append((row + 2 * direction, col))
        if 0 <= row + direction <= 7 and self.get_piece(row + direction, col) == '':
            valid_moves.append((row + direction, col))

        # captures
        for i in [-1, 1]:
            try:
                # has normal capture
                if self.opposing_player(piece, self.get_piece(row + direction, col + i)):
                    valid_moves.append((row + direction, col + i))
                # has en passant
                if col + i == self.double_move_col and row == int(3.5 + direction / 2):
                    valid_moves.append((row + direction, col + i))
            except IndexError:
                pass

        return valid_moves

    # returns list of valid rook moves
    def valid_rook_move(self, piece, row, col):
        valid_moves = []
        for i in [0, 1]:
            for j in [-1, 1]:
                target = [row, col]
                while True:
                    target[i] += j

                    # break if out of bounds
                    if target[i] < 0 or target[i] > 7:
                        break

                    target_piece = self.get_piece(target[0], target[1])
                    # add empty square to valid moves
                    if target_piece == '':
                        valid_moves.append((target[0], target[1]))
                    # add opposed square to valid moves
                    elif self.opposing_player(piece, target_piece):
                        valid_moves.append((target[0], target[1]))
                        break
                    else:
                        break
        return valid_moves

    def valid_knight_move(self, piece, row, col):
        valid_moves = []
        for i in [-2, -1, 1, 2]:
            for j in [-2, -1, 1, 2]:
                if abs(i) + abs(j) == 3:
                    try:
                        target_piece = self.get_piece(row + i, col + j)
                        if target_piece == ''\
                                or self.opposing_player(piece, target_piece):
                            valid_moves.append((row + i, col + j))
                    except IndexError:
                        pass

        return valid_moves

    def valid_bishop_move(self, piece, row, col):
        valid_moves = []
        for i in [-1, 1]:
            for j in [-1, 1]:
                target = [row, col]
                while True:
                    target[0] += i
                    target[1] += j

                    # break if out of bounds
                    if target[0] < 0 or target[0] > 7\
                            or target[1] < 0 or target[1] > 7:
                        break

                    target_piece = self.get_piece(target[0], target[1])
                    # add empty squares to valid moves
                    if target_piece == '':
                        valid_moves.append((target[0], target[1]))
                    # add opposed square to valid moves
                    elif self.opposing_player(piece, target_piece):
                        valid_moves.append((target[0], target[1]))
                        break
                    else:
                        break

        return valid_moves

    def valid_queen_move(self, piece, row, col):
        return self.valid_rook_move(piece, row, col) + self.valid_bishop_move(piece, row, col)

    def valid_king_move(self, piece, row, col):
        valid_moves = []
        color = self.get_color(piece)

        # --- Normal king moves ---
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                target = (row + i, col + j)

                # continue if out of bounds
                if target[0] < 0 or target[0] > 7 \
                    or target[1] < 0 or target[1] > 7:
                    continue
                if i == 0 and j == 0:
                    continue

                target_piece = self.get_piece(target[0], target[1])
                if self.is_square_attacked(target[0], target[1], self.opposite_color(color)):
                    continue
                if target_piece == '' or self.opposing_player(piece, target_piece):
                    valid_moves.append(target)

        # --- castling validation ---
        castling_rights = ''
        if color == 'white':
            castling_rights = self.white_castling_rights
        else:
            castling_rights = self.black_castling_rights

        if castling_rights != '':
            if not self.in_check(color):
                if 'k' in castling_rights:
                    if all(not self.is_square_attacked(row, col + i, self.opposite_color(color)) and self.get_piece(row, col + i) == '' for i in [1, 2]):
                        valid_moves.append((row, col + 2))
                if 'q' in castling_rights:
                    if all(not self.is_square_attacked(row, col - i, self.opposite_color(color)) and self.get_piece(row, col - i) == '' for i in [1, 2]):
                        valid_moves.append((row, col - 2))

        return valid_moves

    # --- Determine if square is attacked ---
    def is_square_attacked(self, row, col, attacker_color):
        for attacker_row in range(8):
            for attacker_col in range(8):
                attacker = self.get_piece(attacker_row, attacker_col)
                if self.get_color(attacker) != attacker_color:
                    continue

                match attacker:
                    case '':
                        continue
                    case 'k' | 'K':
                        if abs(row - attacker_row) <= 1 and abs(col - attacker_col) <= 1:
                            return True
                    case 'n' | 'N':
                        row_diff = abs(attacker_row - row)
                        col_diff = abs(attacker_col - col)
                        if (row_diff == 1 and col_diff == 2) or (row_diff == 2 and col_diff == 1):
                            return True
                    case 'r' | 'R' | 'b' | 'B' | 'q' | 'Q':
                        # Determine if rook move attacks square
                        move_sets = {'r': [(0, 1), (0, -1), (1, 0), (-1, 0)],
                                 'b': [(1, 1), (-1, -1), (-1, 1), (1, -1)]}
                        move_set = []
                        if attacker.lower() != 'b':
                            move_set.extend(move_sets['r'])
                        if attacker.lower() != 'r':
                            move_set.extend(move_sets['b'])

                        for move in move_set:
                            attack_path = (attacker_row, attacker_col)
                            while True:
                                attack_path = (attack_path[0] + move[0], attack_path[1] + move[1])
                                # check if target square has been reached
                                if attack_path == (row, col):
                                    return True
                                # break if out of bounds
                                if attack_path[0] < 0 or attack_path[0] > 7 or attack_path[1] < 0 or attack_path[1] > 7:
                                    break
                                # break if blocked
                                if self.get_piece(attack_path[0], attack_path[1]) != '':
                                    break

                    case 'p' | 'P':
                        # doesn't bother checking for en passant attacks
                        pawn_direction = self.white_direction if attacker_color == 'white' else self.black_direction
                        if row == attacker_row + pawn_direction and (col == attacker_col + 1 or col == attacker_col - 1):
                            return True

        return False


    def in_check(self, king_color):
        #return False
        if king_color == 'white':
            king_row, king_col = self.white_king_loc
        elif king_color == 'black':
            king_row, king_col = self.black_king_loc
        else:
            return False

        king = self.get_piece(king_row, king_col)
        if self.is_square_attacked(king_row, king_col, self.opposite_color(king_color)):
            return True

        return False

    def in_checkmate(self, king_color):
        #return False
        if king_color == 'white':
            king_row, king_col = self.white_king_loc
        elif king_color == 'black':
            king_row, king_col = self.black_king_loc
        else:
            return False

        king = self.get_piece(king_row, king_col)
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece != '' and not self.opposing_player(king, piece):
                    test_board = deepcopy(self)
                    for (test_row, test_col) in self.get_valid_moves(row, col):
                        test_board.move_piece(row, col, test_row, test_col)
                        if not test_board.in_check(king_color):

                            return False
                        test_board = deepcopy(self)
        return True

    # checks if a given move cause check
    def move_causes_check(self, piece, from_row, from_col, to_row, to_col):
        test_board = deepcopy(self)
        test_board.move_piece(from_row, from_col, to_row, to_col, force=True)
        return test_board.in_check(self.get_color(piece))

    # checks if pawn is on final row
    def pawn_should_promote(self, row, col):
        piece = self.get_piece(row, col)
        if piece.lower() != 'p':
            return False
        direction = self.get_direction(piece)
        if row + direction < 0 or 7 < row + direction:
            return True
        return False

    # change pawn to another piece
    def promote(self, row, col, promotion_piece='q'):
        piece = self.get_piece(row, col)
        match piece:
            case 'p':
                self.board[row][col] = promotion_piece.lower()
            case 'P':
                self.board[row][col] = promotion_piece.upper()
            case _:
                return