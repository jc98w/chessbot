import unittest
from pprint import pprint

from components.Board import Board


class MyTestCase(unittest.TestCase):
    def test_get_piece_locations(self):
        board = Board()
        white_locations = board.get_piece_locations('white')
        black_locations = board.get_piece_locations('black')
        self.assertEqual(len(white_locations), 16)
        self.assertEqual(len(black_locations), 16)

    def test_valid_pawn_move(self):
        board = Board()
        board.set_board_array([[''] * 8,
                              ['P'] * 8,
                              [''] * 8, ['p'] * 8, ['P'] * 8, [''] * 8,
                              ['p'] * 8,
                              [''] * 8])
        board.set_king_loc('white', 0, 5)
        board.set_king_loc('black', 7, 5)
        pprint(board.get_board_array())

        white_pawn1 = board.get_piece(1, 0)
        print('valid_pawn_moves(white_pawn1, 1, 0):', board.valid_pawn_move(white_pawn1, 1, 0, add_promotion=False))
        print('get_valid_moves(1, 0):', board.get_valid_moves(1, 0))
        print('get_valid_moves(1, 0, add_promotion=True):', board.get_valid_moves(1, 0, add_promotion=True))
        print('get_valid_moves(1, 0, add_promotion=True):', board.get_valid_moves(1, 0, add_promotion=True),'\n')

        white_pawn2 = board.get_piece(4, 4)
        print('valid_pawn_moves(white_pawn2, 4, 4):', board.valid_pawn_move(white_pawn2, 4, 4, add_promotion=False))
        print('get_valid_moves(4, 4):',board.get_valid_moves(4, 4))
        print('get_valid_moves(4, 4, add_promotion=True):', board.get_valid_moves(4, 4, add_promotion=True))
        print('get_valid_moves(4, 4, add_promotion=True):', board.get_valid_moves(4, 4, add_promotion=True), '\n')

        black_pawn = board.get_piece(6, 0)
        print('valid_pawn_moves(black_pawn, 6, 0):', board.valid_pawn_move(black_pawn, 6, 0, add_promotion=False))
        print('get_valid_moves(6, 0):', board.get_valid_moves(6, 0))
        print('get_valid_moves(6, 0, add_promotion=True):', board.get_valid_moves(6, 0, add_promotion=True))
        print('get_valid_moves(6, 0, add_promotion=True):', board.get_valid_moves(6, 0, add_promotion=True))

if __name__ == '__main__':
    unittest.main()
