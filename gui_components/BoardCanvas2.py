import threading
import tkinter as tk
from time import sleep

from components.GameManager import GameManager

LIGHT_SQUARE_COLOR = '#DEB887'
DARK_SQUARE_COLOR = '#8B4513'
MIN_SIZE = 200
BOARDER_WIDTH = 10
FONT = 'Arial'

PIECE_ICONS = {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
               'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}

class BoardCanvas2(tk.Canvas):

    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.game_manager = parent.game_manager
        self.game_thread = None

        self.cell_size = 1
        self.x_offset = 1
        self.y_offset = 1
        self.icon_size = 1
        self.widgets = {}

        self.cell_selected = None
        self.bind("<Button-1>", self.on_left_click)

    def on_left_click(self, event):
        """ Resolves left mouse clicks for selecting pieces to move """
        if self.game_manager.is_players_turn():
            mouse_x = event.x
            mouse_y = event.y
            col = (mouse_x - self.x_offset) // self.cell_size
            row = (mouse_y - self.y_offset) // self.cell_size

            valid_moves =[]
            if self.cell_selected is not None:
                valid_moves = self.game_manager.valid_squares(*self.cell_selected)

            if 0 <= row <= 7 and 0 <= col <= 7:
                # Click was within the board boundaries
                if self.cell_selected is None:
                    # First click (selecting piece)
                    if self.game_manager.good_piece_selection(row, col):
                        # Valid piece
                        self.cell_selected = (row, col)
                elif (row, col) in valid_moves:
                    # Destination selecting click
                    move = [self.cell_selected[0], self.cell_selected[1], row, col]
                    self.game_manager.add_player_move(move)
                    if self.game_manager.need_promotion():
                        self.game_manager.set_promotion(self.ask_promotion_piece())
                    self.cell_selected = None
                else:
                    self.cell_selected = None

    def draw_board(self):
        """" Draws the board and pieces on the Canvas. Highlights selected squares and available moves """
        # Determine window size
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        # return in window is too small
        if width < 50 or height < 50:
            return

        size = max(MIN_SIZE, min(width, height)) - BOARDER_WIDTH * 2
        self.x_offset = BOARDER_WIDTH if width < height or size < MIN_SIZE else BOARDER_WIDTH + (width - height) // 2
        self.y_offset = BOARDER_WIDTH
        self.cell_size = size // 8
        self.icon_size = int(self.cell_size * 0.7)
        label_size = int(self.cell_size * 0.15)

        # Identify highlighted squares
        selected_row, selected_col, valid_squares_list = None, None, []
        if self.cell_selected is not None:
            selected_row = self.cell_selected[0]
            selected_col = self.cell_selected[1]
            valid_squares_list = self.game_manager.valid_squares(selected_row, selected_col)
        checked_king_loc, check_status = self.game_manager.get_checked_king_loc()

        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                # Square coordinates
                x1 = col * self.cell_size + self.x_offset
                y1 = row * self.cell_size + self.y_offset
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (row, col) == (selected_row, selected_col):
                    color = 'white'
                elif (row, col) in valid_squares_list:
                    color = 'lightgrey'
                elif (row, col) == checked_king_loc:
                    if check_status == 'check':
                        color = 'red'
                    elif check_status == 'mate':
                        color = 'black'
                if f's{row}{col}' not in self.widgets:
                    # create new squares on first draw - s for square
                    self.widgets[f's{row}{col}'] = self.create_rectangle(x1, y1, x2, y2, fill=color)
                else:
                    # update squares on subsequent draws
                    self.coords(self.widgets[f's{row}{col}'], x1, y1, x2, y2)
                    self.itemconfig(self.widgets[f's{row}{col}'], fill=color)

                # Draw rank and file labels
                if row == 7:
                    x_label = x1 + int(self.cell_size * 0.9)
                    y_label = y1 + int(self.cell_size * 0.9)
                    if f'fl{col}' not in self.widgets:
                        # create new labels if not yet existent - fl for file label
                        self.widgets[f'fl{col}'] = self.create_text(x_label, y_label, text=chr(ord('a') + col), font=(FONT, label_size), fill='black')
                    else:
                        self.coords(self.widgets[f'fl{col}'], x_label, y_label)
                if col == 0:
                    x_label = x1 + int(self.cell_size * 0.1)
                    y_label = y1 + int(self.cell_size * 0.1)
                    if f'rl{row}' not in self.widgets:
                        # new labels on first draw - rl for rank label
                        self.widgets[f'rl{row}'] = self.create_text(x_label, y_label, text=str(8 - row), font=(FONT, label_size), fill='black')
                    else:
                        self.coords(self.widgets[f'rl{row}'], x_label, y_label)

                # Draw Pieces
                piece = self.game_manager.get_piece(row, col)
                if piece != '':
                    center_x = x1 + self.cell_size // 2
                    center_y = y1 + self.cell_size // 2
                    piece_icon = PIECE_ICONS[piece]

                    if f'p{row}{col}' not in self.widgets:
                        # Piece on square and no piece draw -> draw new piece
                        self.widgets[f'p{row}{col}'] = self.create_text(center_x, center_y, text=piece_icon, font=(FONT, self.icon_size), fill='black')
                    else:
                        # update drawn piece on that square
                        self.itemconfig(self.widgets[f'p{row}{col}'], text=piece_icon, font=(FONT, self.icon_size))
                        self.coords(self.widgets[f'p{row}{col}'], center_x, center_y)
                else:
                    # No piece on the square - check for drawn piece and delete if necessary
                    if f'p{row}{col}' in self.widgets:
                        self.delete(self.widgets[f'p{row}{col}'])
                        del self.widgets[f'p{row}{col}']

        if not self.game_manager.winner:
            # Redraw board if game is still running
            self.after(100, self.draw_board)
        else:
            # game has ended
            self.end_dialog(self.game_manager.winner)

    def ask_promotion_piece(self, color='white'):
        """ Opens a dialog box to ask what to promote a pawn to """
        dialog = tk.Toplevel(self)
        dialog.overrideredirect(True)
        # dialog.transient(self.winfo_toplevel())

        # dialog.resizable(False, False)
        dialog.config(bd=2, relief='raised')

        chosen_piece = tk.StringVar(dialog)

        button_frame = tk.Frame(dialog, padx=10, pady=10)
        button_frame.pack()

        pieces = ['q', 'r', 'b', 'n']

        def on_select(piece_code):
            chosen_piece.set(piece_code)
            dialog.grab_release()
            dialog.destroy()

        for piece in pieces:
            piece = piece.upper() if color == 'white' else piece
            tk.Button(button_frame, text=PIECE_ICONS[piece], font=(FONT, int(self.icon_size * 0.75)), command=lambda p=piece: on_select(p))\
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

    def end_dialog(self, winner, auto_restart=False):
        if auto_restart:
            print('Auto restart')
            self.reset()
        else:
            dialog = tk.Toplevel(self)
            dialog.overrideredirect(True)

            match winner:
                case 'disconnect':
                    message = 'Connection lost'
                case 'draw':
                    message = 'Draw!'
                case _:
                    message = f'{winner.capitalize()} wins!'
            msg_lbl = tk.Label(dialog, text=message, font=(FONT, int(self.icon_size * 0.75)))
            msg_lbl.pack(pady=10)

            def close():
                self.reset()
                dialog.grab_release()
                dialog.destroy()
                self.start_game()

            def menu():
                self.reset()
                dialog.grab_release()
                dialog.destroy()
                self.parent.show_start_menu()

            if winner != 'disconnect':
                tk.Button(dialog, text='Reset', command=close, font=(FONT, int(self.icon_size * 0.5))).pack(pady=10)
            tk.Button(dialog, text='Menu', command=menu, font=(FONT, int(self.icon_size * 0.5))).pack(pady=10)

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

    def start_game(self):
        """ Starts game thread and draw loop """
        self.game_thread = threading.Thread(target=self.game_manager.game_loop, daemon=True)
        self.game_thread.start()
        self.after(100, self.draw_board)

    def set_player_types(self, white='player', black='bot'):
        """ Sets player types as player, bot, or lan_opp """
        self.game_manager.set_player_types(white, black)

    def reset(self):
        delete_widgets = []
        for widget in self.widgets.keys():
            if 'p' in widget:
                self.delete(self.widgets[widget])
                delete_widgets.append(widget)
        for widget in delete_widgets:
            del self.widgets[widget]
        self.game_manager.reset()

    def kill_game_thread(self):
        if self.game_thread is not None and self.game_thread.is_alive():
            self.game_manager.interrupt_game_loop()
