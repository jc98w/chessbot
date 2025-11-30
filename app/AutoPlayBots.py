import sys
from copy import deepcopy
from pprint import pprint

from components.Board import Board
from components.ChessBot import ChessBot
from storage.DatabaseManager import DatabaseManager
from storage.BoardLog import BoardLog

if __name__ == '__main__':
    try:
        print('Connecting to database...', end='')
        db_manager = DatabaseManager()
        if db_manager.ping():
            print('Connection successful')
        else:
            raise Exception('Unable to connect to database')
    except Exception as e:
        print(e)
        db_manager = None

    bot = ChessBot(db_manager)

    x = 'y'
    while x == 'y':
        turn = 'white'
        board_log = BoardLog()
        board = Board()
        while True:
            move = bot.decide_move(board, turn)
            board_log.add_entry(deepcopy(board), *move)
            board.move_piece(*move)
            turn = board.opposite_color(turn)
            if board.in_checkmate(turn):
                print(f'Checkmate!')
                break
            if board.is_stalemate(turn):
                print(f'Stalemate!')
                break
        for log in board_log.get_log():
            pprint(log.get_board_array())
        x = input('Play again? (y/n)')



