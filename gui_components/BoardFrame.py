import sys
import threading
from copy import deepcopy
from pprint import pprint
from tkinter import Canvas, Toplevel, StringVar, Frame, Button, Label

from components.Board import Board
from components.ChessBot import ChessBot
from storage.BoardLog import BoardLog
from storage.DatabaseManager import DatabaseManager

BACKGROUND_COLOR = '#228833'
LIGHT_COLOR = '#DEB887'
DARK_COLOR = '#8B4513'
FONT = 'Arial'
MIN_SIZE = 200
BORDER_WIDTH = 10

PIECE_ICONS = {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
               'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}

class BoardFrame(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs, background=BACKGROUND_COLOR)
        self.board = Board()
        try:
            print('Connecting to database...')
            if len(sys.argv) < 2:
                raise Exception('Database credentials not provided')
            self.db_manager = DatabaseManager(sys.argv[1], sys.argv[2])
            if not self.db_manager.ping():
                raise Exception('Unable to connect to database')
        except Exception as e:
            print(e)
            self.db_manager = None
        self.bot = ChessBot(self.db_manager)
        self.board_log = BoardLog()
        self.board_to_log = deepcopy(self.board)
        self.cell_size = 1
        self.x_offset = 1
        self.y_offset = 1
        self.icon_size = 1
        self.turn = 'white'
        self.is_white_bot = False
        self.is_black_bot = True
        self.is_auto_restart = False
        self.cell_selected = None
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_left_click)

    def on_resize(self, event):
        self.delete('all')
        self.draw_board()

    def set_bots(self, white=False, black=True):
        self.is_white_bot = white
        self.is_black_bot = black

    def is_bot(self, color):
        return self.is_white_bot if color == 'white' else self.is_black_bot

    def on_left_click(self, event):
        # Do nothing if it is a bot's turn
        if self.is_bot(self.turn):
            return

        mouse_x = event.x
        mouse_y = event.y
        col = (mouse_x - self.x_offset) // self.cell_size
        row = (mouse_y - self.y_offset) // self.cell_size
        if 0 <= row <= 7 and 0 <= col <= 7:
            selected_piece = self.board.get_piece(row, col)

            if self.cell_selected is None:
                if selected_piece != '' and self.board.get_color(selected_piece) == self.turn:
                    self.cell_selected = (row, col)
                else:
                    return
            else:
                move = (self.cell_selected[0], self.cell_selected[1], row, col)
                if self.board.move_piece(*move):
                    if self.board.pawn_should_promote(row, col):
                        promotion_piece = self.ask_promotion_piece(color=self.turn)
                        if promotion_piece is None:
                            promotion_piece = 'q'
                        move += (promotion_piece,)
                        self.board.promote(row, col, promotion_piece)
                    self.board_log.add_entry(self.board_to_log, *move)
                    self.board_to_log = deepcopy(self.board)
                    self.cell_selected = None
                    self.swap_turn()
                elif selected_piece != '' and self.board.get_color(selected_piece) == self.turn:
                    self.cell_selected = (row, col)
        else:
            self.cell_selected = None

        self.draw_board()

    def swap_turn(self):
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def draw_board(self):
        # Determine sizing
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        # return if too small
        if width < 50 or height < 50:
            return

        size = max(MIN_SIZE, min(width, height)) - BORDER_WIDTH * 2
        self.x_offset = BORDER_WIDTH if width < height or size < MIN_SIZE else BORDER_WIDTH + (width - height) // 2
        self.y_offset = BORDER_WIDTH
        self.cell_size = size // 8
        self.icon_size = int(self.cell_size * 0.7)
        label_size = int(self.cell_size * 0.15)

        winner = None
        if self.board_log.is_draw(self.board) or self.board.is_stalemate(self.turn):
            winner = 'draw'
        else:
            # Draw board
            for row in range(8):
                for col in range(8):
                    # Draw squares
                    color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                    x1 = col * self.cell_size + self.x_offset
                    y1 = row * self.cell_size + self.y_offset
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    if self.cell_selected is not None:
                        selected_row = self.cell_selected[0]
                        selected_col = self.cell_selected[1]
                        if row == selected_row and col == selected_col:
                            color = 'white'
                        if (row, col) in self.board.get_valid_moves(selected_row, selected_col):
                            color = 'lightgrey'
                    if (row, col) == self.board.white_king_loc:
                        if self.board.in_check('white'):
                            color = 'red'
                            if self.board.in_checkmate('white'):
                                winner = 'black'
                    elif (row, col) == self.board.black_king_loc:
                        if self.board.in_check('black'):
                            color = 'red'
                            if self.board.in_checkmate('black'):
                                winner = 'white'

                    self.create_rectangle(x1, y1, x2, y2, fill=color)

                    # Draw rank and file labels
                    if row == 7:
                        x_label = x1 + int(self.cell_size * 0.9)
                        y_label = y1 + int(self.cell_size * 0.9)
                        self.create_text(x_label, y_label, text=chr(ord('a') + col), font=(FONT, label_size), fill='black')

                    if col == 0:
                        x_label = x1 + int(self.cell_size * 0.1)
                        y_label = y1 + int(self.cell_size * 0.1)
                        self.create_text(x_label, y_label, text=str(8 - row), font=(FONT, label_size), fill='black')

                    # Draw pieces
                    piece = self.board.get_piece(row, col)
                    if piece != '':
                        center_x = x1 + self.cell_size // 2
                        center_y = y1 + self.cell_size // 2
                        piece_icon = PIECE_ICONS[piece]
                        self.create_text(center_x, center_y, text=piece_icon, font=(FONT, self.icon_size), fill='black')
        if winner is not None:
            self._start_commit_log_thread(winner)
            self.end_dialog(winner, self.is_auto_restart)

    def _start_commit_log_thread(self, winner):
        commit_thread = threading.Thread(target=self._commit_log_async, args=(winner,), daemon=False)
        commit_thread.start()
        print('Started commit log thread')

    def _commit_log_async(self, winner):
        if self.db_manager:
            try:
                log_to_commit = deepcopy(self.board_log)
                success = self.db_manager.commit_log(log_to_commit, winner)
                if success:
                    print('Background thread: Log commited successfully')
                else:
                    print('Background thread: Failed to commit (check DatabaseManager errors')
            except Exception as e:
                print(f'Background thread error during commit_log: {e}')
                import traceback
                traceback.print_exc()
        else:
            print("Background thread: DatabaseManager not initialized, unable to commit")

    def reset(self):
        self.board = Board()
        self.cell_selected = None
        self.turn = 'white'
        self.board_log = BoardLog()
        self.board_to_log = deepcopy(self.board)
        self.draw_board()
        self.bot_move()

    def ask_promotion_piece(self, color='white'):
        dialog = Toplevel(self)
        dialog.overrideredirect(True)
        # dialog.transient(self.winfo_toplevel())

        # dialog.resizable(False, False)
        dialog.config(bd=2, relief='raised')

        chosen_piece = StringVar(dialog)

        button_frame = Frame(dialog, padx=10, pady=10)
        button_frame.pack()

        pieces = ['q', 'r', 'b', 'n']

        def on_select(piece_code):
            chosen_piece.set(piece_code)
            dialog.grab_release()
            dialog.destroy()

        for piece in pieces:
            piece = piece.upper() if color == 'white' else piece
            Button(button_frame, text=PIECE_ICONS[piece], font=(FONT, int(self.icon_size * 0.75)), command=lambda p=piece: on_select(p))\
                .pack(side='left', padx=10, pady=10)

        dialog.update_idletasks()
        parent_window = self.winfo_toplevel()
        parent_x = parent_window.winfo_rootx()
        parent_y = parent_window.winfo_rooty()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()

        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        dialog.geometry(f'+{x}+{y}')

        dialog.after_idle(dialog.grab_set)
        # dialog.protocol("WM_DELETE_WINDOW", lambda: on_select('q'))
        dialog.wait_window()

        result = chosen_piece.get()
        default_piece = 'Q' if color == 'white' else 'q'
        return result if result != '' else default_piece

    def set_auto_restart(self, auto_restart):
        self.is_auto_restart = auto_restart

    def end_dialog(self, winner, auto_restart=False):
        if auto_restart:
            print('Auto restart')
            self.reset()
        else:
            dialog = Toplevel(self)
            dialog.overrideredirect(True)

            message = f'{winner.capitalize()} wins!' if winner != 'draw' else 'Draw!'
            msg_lbl = Label(dialog, text=message, font=(FONT, int(self.icon_size * 0.75)))
            msg_lbl.pack(pady=10)

            def close():
                self.reset()
                dialog.grab_release()
                dialog.destroy()

            Button(dialog, text='Reset', command=close, font=(FONT, int(self.icon_size * 0.5))).pack(pady=10)

            dialog.update_idletasks()
            parent_window = self.winfo_toplevel()
            parent_x = parent_window.winfo_rootx()
            parent_y = parent_window.winfo_rooty()
            parent_width = parent_window.winfo_width()
            parent_height = parent_window.winfo_height()

            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()

            x = parent_x + (parent_width // 2) - (dialog_width // 2)
            y = parent_y + (parent_height // 2) - (dialog_height // 2)
            dialog.geometry(f'+{x}+{y}')

            dialog.protocol('WM_DELETE_WINDOW', close)

            dialog.after_idle(dialog.grab_set)

            dialog.wait_window()

    def bot_move(self):
        if self.is_bot(self.turn):
            bot_move = self.bot.decide_move(self.board, self.turn)
            if bot_move is None:
                return
            if self.board.move_piece(*bot_move):
                self.board_log.add_entry(self.board_to_log, *bot_move)
                if self.board.pawn_should_promote(bot_move[2], bot_move[3]):
                    self.board.promote(bot_move[2], bot_move[3], bot_move[4])

                self.board_to_log = deepcopy(self.board)
                self.swap_turn()
                self.draw_board()
        self.after(1000, self.bot_move)
