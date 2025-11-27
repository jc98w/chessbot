import sys
import queue
import threading
from _queue import Empty
from copy import deepcopy
from time import sleep

from components.Board import Board
from components.ChessBot import ChessBot
from storage.BoardLog import BoardLog
from storage.DatabaseManager import DatabaseManager


class GameManager:
    def __init__(self):
        self.board = Board()
        self.turn = 'white'
        self.winner = None
        self.white_player_type = None
        self.black_player_type = None

        self.network_manager = None
        self.lan_match = False

        self.move_queue = queue.Queue()
        self.lan_opp_queue = queue.Queue()
        self.lan_listen_thread = None

        self.board_log = BoardLog()
        self.board_to_log = deepcopy(self.board)

        self.game_loop_interrupt = False
        self.waiting_on_move = False

        # Attempt to connect to database
        try:
            print('Connecting to database...', end='')
            if len(sys.argv) < 2:
                raise Exception('Database credentials not provided')
            self.db_manager = DatabaseManager(sys.argv[1], sys.argv[2])
            if self.db_manager.ping():
                print('Connection successful')
            else:
                raise Exception('Unable to connect to database')
        except Exception as e:
            print(e)
            self.db_manager = None

        self.bot = ChessBot(self.db_manager)

    def set_player_types(self, white_type = 'player', black_type = 'bot'):
        """ Type should be player, bot, or lan_opp (LAN opponent) """
        self.white_player_type = white_type
        self.black_player_type = black_type
        if white_type == 'lan_opp' or black_type == 'lan_opp':
            self.lan_match = True
        else:
            self.lan_match = False

    def set_network_manager(self, manager):
        # manager can be a GameHoster or GameClient
        self.network_manager = manager

    def swap_turn(self):
        """ Swap self.turn from white to black or black to white """
        self.turn = 'white' if self.turn == 'black' else 'black'

    def get_player_type(self, color):
        if color == 'white':
            return self.white_player_type
        elif color == 'black':
            return self.black_player_type
        else:
            return None

    def is_players_turn(self):
        return self.get_player_type(self.turn) == 'player'

    def good_piece_selection(self, row, col):
        """ Used for determining if a click is appropriate
            ie if the player is white, they can't move black's pieces """
        return self.is_players_turn() and Board.get_color(self.board.get_piece(row, col)) == self.turn

    def need_promotion(self, move):
        """ Returns true if player needs to promote a pawn """
        from_row, from_col, to_row, to_col = move
        if self.board.get_piece(from_row, from_col) in ('p', 'P') and to_row in (0, 7):
            if from_col == to_col and self.board.get_piece(to_row, to_col) == '':
                return True
            elif from_col != to_col and self.board.get_piece(to_row, to_col) != '':
                return True
            else:
                return False
        else:
            return False

    def valid_squares(self, row, col):
        """ Returns list of valid squares for a given piece """
        return self.board.get_valid_moves(row, col)

    def get_piece(self, row, col):
        return self.board.get_piece(row, col)

    def get_checked_king_loc(self):
        """ Returns the location of a king in check or checkmate """
        for color in ('white', 'black'):
            if self.board.in_checkmate(color):
                return [self.board.king_loc(color), 'mate']
            elif self.board.in_check(color):
                return [self.board.king_loc(color), 'check']
        return [(-1, -1), 'safe']

    def game_loop(self):
        print('starting new game loop ', self)
        if self.lan_match:
            # Start listening with a clean slate
            while not self.lan_opp_queue.empty():
                self.lan_opp_queue.get_nowait()
            while not self.move_queue.empty():
                self.move_queue.get_nowait()

            self.network_manager.send_data('new game')
            new_game_msg = ''
            while new_game_msg != 'new game':
                try:
                    new_game_msg = self.network_manager.receive_data()
                except TimeoutError:
                    continue

            print(f'network_manager: {self.network_manager.game_sock.getsockname()}')
            self.lan_listen_thread = threading.Thread(target=self._lan_listen, daemon=True)
            self.lan_listen_thread.start()

        while self.winner is None and not self.game_loop_interrupt:
            for color in ['white', 'black']:
                if self.game_loop_interrupt:
                    # Ends game in event of window closing
                    return ''

                self.turn = color
                if self.winner is not None:
                    break

                if self.board.is_stalemate(color) or self.board_log.get_draw_status():
                    # Check for draws
                    self.winner = 'draw'
                else:
                    # Make move
                    player_type = self.get_player_type(color)
                    print(f'It\'s {player_type} {color}\'s turn')
                    move = None
                    if player_type == 'player':
                        print('my move')
                        move = self.player_move()
                    elif player_type == 'lan_opp':
                        print('opp move')
                        move = self.lan_move()
                    else:
                        move = self.bot_move(color)
                    if move is not None:
                        self.board_log.add_entry(self.board_to_log, *move)
                        self.board_to_log = deepcopy(self.board)

                # Check for win
                if self.board.in_checkmate(self.board.opposite_color(color)):
                    self.winner = color
                    if self.lan_match:
                        self.network_manager.send_data('game over')
                    print(f'Winner: {self.winner}')
        # Commit log in background
        threading.Thread(target=self.commit_log, daemon=True).start()

        return self.winner

    def interrupt_game_loop(self):
        """ Ends game loop with interrupt flag """
        self.game_loop_interrupt = True
        self.waiting_on_move = False
        if self.lan_listen_thread is not None and self.lan_listen_thread.is_alive():
            self.lan_listen_thread.join()

    def commit_log(self):
        # Commit log to database
        if self.db_manager:
            try:
                log_to_commit = deepcopy(self.board_log)
                success = self.db_manager.commit_log(log_to_commit, self.winner)
                if success:
                    print('Background thread: Log commited successfully')
                else:
                    print('Background thread: Failed to commit (check DatabaseManager errors')
            except Exception as e:
                print(f'Background thread error during commit_log: {e}')
                import traceback
                traceback.print_exc()

    def add_player_move(self, move):
        self.move_queue.put(move)

    def player_move(self):
        """ Waits to receive move from player """
        self.waiting_on_move = True
        move = None
        while self.waiting_on_move and not self.game_loop_interrupt:
            # Retrieve move from queue
            try:
                move = self.move_queue.get(timeout=1)
            except Empty:
                continue

            if self.board.move_piece(*move):
                self.waiting_on_move = False

                # Send data to opposing player
                if self.lan_match:
                    move_str = ''
                    for item in move:
                        move_str += str(item)
                    self.network_manager.send_data(move_str)
        return move

    def lan_move(self):
        """ Waits to receive move from lan opponent """
        self.waiting_on_move = True
        move = []
        while self.waiting_on_move and not self.game_loop_interrupt:
            try:
                move = self.lan_opp_queue.get(timeout=1)
            except Empty:
                continue
            if self.board.move_piece(*move):
                self.waiting_on_move = False

        return None if move == [] else move

    def _lan_listen(self):
        """ Background task to queue lan opponent's moves """
        while not self.game_loop_interrupt and self.winner is None:
            move = []
            try:
                move_str = self.network_manager.receive_data()
                if move_str == 'game over':
                    print('_lan_listen done: game over')
                    return
                # '' is a disconnect message
                elif move_str == '':
                    print('_lan_listen done: disconnect')
                    self.winner = 'disconnect'
                    self.game_loop_interrupt = True
                    self.waiting_on_move = False
                    return
            except TimeoutError:
                continue
            except OSError:
                self.winner = 'error'
                self.game_loop_interrupt = True
                self.waiting_on_move = False
                return

            try:
                for char in move_str[:4]:
                    if char.isnumeric():
                        move.append(ord(char) - ord('0'))
                    else:
                        raise TypeError
                if len(move_str) == 5:
                    print(f'{move_str[-1]}')
                    move.append(move_str[-1])
                elif len(move) > 5:
                    # throw out bad move
                    continue
            except TypeError:
                continue
            print(f'opp\'s move: {move_str}:{move}')
            self.lan_opp_queue.put(move)

    def bot_move(self, color):
        """ Returns bot generated move """
        sleep(1)
        while True:
            move = self.bot.decide_move(self.board, color)
            if self.board.move_piece(*move):
                break
        return move

    def reset(self):
        """ Resets board, winner, logs """
        self.winner = None
        self.board = Board()
        self.turn = 'white'
        self.game_loop_interrupt = False
        self.waiting_on_move = False
        self.board_log = BoardLog()
        self.board_to_log = deepcopy(self.board)

    def __str__(self):
        return (f'*G*{self.turn}:{self.winner}:{self.white_player_type}:{self.black_player_type}\n'
                f'*M*{self.move_queue.empty()}:{self.lan_opp_queue.empty()}:{self.waiting_on_move}:{self.game_loop_interrupt}')
