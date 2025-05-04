import unittest
from pprint import pprint

from components.Board import Board
from storage.BoardLog import BoardLog


class MyTestCase(unittest.TestCase):
    def test_normalize_entry(self):
        board = Board()
        log = BoardLog()
        log.add_entry(board, 6, 1, 5, 1)
        pprint(log.get_log()[0].get_board_array())
        pprint(log.get_log()[0].normalized_board_str())
        log.add_entry(board, 1, 2, 1, 4)
        pprint(log.get_log()[1].get_board_array())
        pprint(log.get_log()[1].normalized_board_str())


if __name__ == '__main__':
    unittest.main()
