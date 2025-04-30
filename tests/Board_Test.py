import unittest
from components.Board import Board


class MyTestCase(unittest.TestCase):
    def test_get_piece_locations(self):
        board = Board()
        white_locations = board.get_piece_locations('white')
        black_locations = board.get_piece_locations('black')
        self.assertEqual(len(white_locations), 16)
        self.assertEqual(len(black_locations), 16)


if __name__ == '__main__':
    unittest.main()
