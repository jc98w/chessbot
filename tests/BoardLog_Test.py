import unittest
from pprint import pprint

from components.Board import Board
from storage.BoardLog import BoardLog


class MyTestCase(unittest.TestCase):
    def test_compress_entry(self):
        board = Board()
        log = BoardLog()
        log.add_entry(board, 0, 0, 1, 0)
        pprint(log.get_log()[0].get_board_array())
        pprint(log.get_log()[0].compress_entry())

if __name__ == '__main__':
    unittest.main()
