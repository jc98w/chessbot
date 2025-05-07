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

    def __eq__(self, other):
        if self.board == other.board and self.white_castling_rights == other.white_castling_rights and \
            self.black_castling_rights == other.black_castling_rights and self.double_move_col == other.double_move_col:
            return True
        return False

    def get_board_array(self):
        return self.board

    def set_board_array(self, board):
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
    def get_valid_moves(self, row, col, add_promotion=False):
        piece = self.board[row][col]
        match piece:
            case 'P' | 'p':
                pseudo_valid_moves = self.valid_pawn_move(piece, row, col, add_promotion)
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
            if not self.move_causes_check(piece, row, col, *move):
                valid_moves.append(move)

        return valid_moves

    # Moves a piece from one square to another
    # Checks for validity by default
    def move_piece(self, from_row, from_col, to_row, to_col, promotion_piece=None, force=False):
        piece = self.board[from_row][from_col]
        color = self.get_color(piece)

        # return False for invalid moves
        if piece == '':
            return False
        if not force and (to_row, to_col) not in self.get_valid_moves(from_row, from_col):
            return False

        match piece:
            case 'K' | 'k':
                self.set_king_loc(color, to_row, to_col)
                self.set_castling_rights(color, '')
                # castling
                if abs(from_col - to_col) > 1:
                    if from_col < to_col:
                        self.move_piece(from_row, 7, from_row, 5, force=True)
                    else:
                        self.move_piece(from_row, 0, from_row, 3, force=True)
                self.double_move_col = None
            case 'r' | 'R':
                rights = self.get_castling_rights(color)
                if from_col == 0 and 'q' in rights:
                    self.set_castling_rights(color, rights.replace('q', ''))
                if from_col == 7 and 'k' in rights:
                    self.set_castling_rights(color, rights.replace('k', ''))
                self.double_move_col = None
            case 'P' | 'p':
                if abs(from_row - to_row) == 2:
                    self.double_move_col = from_col
                # if en passant
                if abs(from_col - to_col) == 1 and abs(from_row - to_row) == 1 and self.double_move_col == to_col:
                    self.board[from_row][to_col] = ''
                if abs(from_row - to_row == 1):
                    self.double_move_col = None
            case _:
                self.double_move_col = None

        # move piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        if promotion_piece is not None and (to_row == 0 or to_row == 7):
            self.promote(to_row, to_col, promotion_piece)
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
        if piece == '':
            return ''
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
    def valid_pawn_move(self, piece, row, col, add_promotion):
        pre_promotion_valid_moves = []
        direction = self.get_direction(piece)

        # straight ahead moves
        if (row == 1 and direction == 1 or direction == -1 and row == 6) \
            and self.get_piece(row + direction, col) == ''\
            and self.get_piece(row + 2 * direction, col) == '':
            pre_promotion_valid_moves.append((row + 2 * direction, col))
        if 0 <= row + direction <= 7 and self.get_piece(row + direction, col) == '':
            pre_promotion_valid_moves.append((row + direction, col))

        # captures
        for i in [-1, 1]:
            if 0 <= col + i <= 7 and 0 <= row + direction <= 7:
                # has normal capture
                if self.opposing_player(piece, self.get_piece(row + direction, col + i)):
                    pre_promotion_valid_moves.append((row + direction, col + i))
                # has en passant
                if col + i == self.double_move_col and row == int(3.5 + direction / 2):
                    pre_promotion_valid_moves.append((row + direction, col + i))
        valid_moves = []
        if add_promotion and (row + direction == 0 or row + direction == 7):
            for move in pre_promotion_valid_moves:
                for promotion_piece in ['q', 'r', 'b', 'n']:
                    valid_moves.append(move + (promotion_piece,))
        else:
            valid_moves = pre_promotion_valid_moves

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
                if abs(i) + abs(j) == 3 and 0 <= row + i <= 7 and 0 <= col + j <= 7:
                    try:
                        target_piece = self.get_piece(row + i, col + j)
                        if target_piece == ''\
                                or self.opposing_player(piece, target_piece):
                            valid_moves.append((row + i, col + j))
                    except IndexError:
                        print('IndexError in valid_knight_move')
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
                    if all(not self.is_square_attacked(row, col - i, self.opposite_color(color)) for i in [1, 2]) and all(self.get_piece(row, col - i) == '' for i in [1, 2, 3]):
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
        if not self.in_check(king_color):
            return False
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

    # checks if a given move cause check on self
    def move_causes_check(self, piece, from_row, from_col, to_row, to_col, promotion_piece=None):
        test_board = deepcopy(self)
        test_board.move_piece(from_row, from_col, to_row, to_col, promotion_piece, force=True)
        return test_board.in_check(self.get_color(piece))

    # checks if move delivers check to opponent
    def move_delivers_check(self, piece, from_row, from_col, to_row, to_col, promotion_piece=None, mate=False):
        test_board = deepcopy(self)
        test_board.move_piece(from_row, from_col, to_row, to_col, promotion_piece, force=True)
        return test_board.in_check(self.opposite_color(piece)) if not mate else test_board.in_checkmate(self.opposite_color(piece))

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

    def get_piece_locations(self, color):
        locations = []
        for row in range(8):
            for col in range(8):
                if self.get_color(self.get_piece(row, col)) == color:
                    locations.append((row, col))
        return locations

    def is_stalemate(self, color):
        if self.in_check(color):
            return False
        piece_loc = self.get_piece_locations(color)
        num_valid_moves = 0
        for loc in piece_loc:
            num_valid_moves += len(self.get_valid_moves(*loc))
        return num_valid_moves == 0

    def get_num_pieces(self):
        num_pieces = 0
        for row in self.board:
            for piece in row:
                if piece != '':
                    num_pieces += 1
        return num_pieces

    # put board in terms of the player rather than by color
    # i.e. make whichever color is making move capitalized
    # flip board such that player's king is below and to the left of opponent's king
    def normalized_board_str(self, color):
        reference_board = self.get_board_array()
        normalized_board =  deepcopy(reference_board)

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
        if self.king_loc(color)[0] < self.king_loc(self.opposite_color(color))[0]:
            normalized_board = normalized_board[::-1]
        # flip board horizontally if player's king is to the right of the opponent's king
        if self.king_loc(color)[1] > self.king_loc(self.opposite_color(color))[1]:
            for row in range(8):
                normalized_board[row] = normalized_board[row][::-1]

        castling_rights = self.get_castling_rights(color).upper() + self.get_castling_rights(self.opposite_color(color))
        return self.compressed_board_string(normalized_board) + castling_rights

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
