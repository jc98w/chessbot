import queue
import threading
import tkinter as tk
from PIL import Image, ImageTk

from components.InfoBar import InfoBar

LIGHT_SQUARE_COLOR = '#DEB887'
DARK_SQUARE_COLOR = '#8B4513'
MIN_SIZE = 200
BOARDER_WIDTH = 30
FONT = 'Arial'

# PIECE_IMAGES = {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
#                'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}
PIECE_IMAGES = {'K': 'white_king.png', 'Q': 'white_queen.png', 'R': 'white_rook.png', 'B': 'white_bishop.png', 'N': 'white_knight.png', 'P': 'white_pawn.png',
               'k': 'black_king.png', 'q': 'black_queen.png', 'r': 'black_rook.png', 'b': 'black_bishop.png', 'n': 'black_knight.png', 'p': 'black_pawn.png'}
# Prep piece images
for icon in PIECE_IMAGES:
    PIECE_IMAGES[icon] = Image.open(f'res/{PIECE_IMAGES[icon]}')

class BoardCanvas2(tk.Canvas):

    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.game_manager = parent.game_manager
        self.game_thread = None
        self.drawing = True

        self.cell_size = 1
        self.x_offset = 1
        self.y_offset = 1
        self.icon_size = 1
        self.widgets = {}
        self.image_cache = {}

        self.cell_selected = None
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Configure>", self.on_resize)

        self.height = 0
        self.width = 0

        self.info_bar = InfoBar(self)
        self.info_window = self.create_window((0,0), anchor='s', window=self.info_bar)

    def on_resize(self, event):
        """ Adjusts sizes when window resizes """
        self.update()
        self.height = event.height
        self.width = event.width

        size = max(MIN_SIZE, min(self.width, self.height)) - BOARDER_WIDTH * 2
        self.x_offset = BOARDER_WIDTH if self.width < self.height or size < MIN_SIZE else BOARDER_WIDTH + (self.width - self.height) // 2
        self.y_offset = BOARDER_WIDTH
        self.cell_size = size // 8
        self.icon_size = int(self.cell_size * 0.7)

        self.coords(self.info_window, (self.width // 2, self.height))
        self.info_bar.set_font_size(-(self.icon_size // 4))
        self.itemconfigure(self.info_window, width=self.width)
        self.info_bar.configure(width=self.width, height=self.y_offset)

        # Resize piece images
        for img in PIECE_IMAGES:
            resized = PIECE_IMAGES[img].resize((self.cell_size, self.cell_size))
            self.image_cache[img] = ImageTk.PhotoImage(resized)

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

                    if self.game_manager.need_promotion(move):
                        move.append(self.ask_promotion_piece(self.game_manager.turn))
                    print(f'Adding {move} to move queue')
                    self.game_manager.add_player_move(move)
                    self.cell_selected = None
                else:
                    self.cell_selected = None

    def draw_board(self):
        """" Draws the board and pieces on the Canvas. Highlights selected squares and available moves """
        # check if should be drawing
        if not self.drawing:
            return

        # return in window is too small
        if self.width < 50 or self.height < 50:
            return

        label_size = -int(self.cell_size * 0.15)

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

                    if f'p{row}{col}' not in self.widgets:
                        # Piece on square and no piece draw -> draw new piece
                        self.widgets[f'p{row}{col}'] = self.create_image((center_x, center_y), image=self.image_cache[piece])
                    else:
                        # update drawn piece on that square
                        self.itemconfig(self.widgets[f'p{row}{col}'], image=self.image_cache[piece])
                        self.coords(self.widgets[f'p{row}{col}'], center_x, center_y)
                else:
                    # No piece on the square - check for drawn piece and delete if necessary
                    if f'p{row}{col}' in self.widgets:
                        self.delete(self.widgets[f'p{row}{col}'])
                        del self.widgets[f'p{row}{col}']

        self.info_bar.set_turn(self.game_manager.turn)

        if self.game_manager.winner is None:
            # Redraw board if game is still running
            self.after(100, self.draw_board)
        else:
            # game has ended
            self.end_dialog(self.game_manager.winner)

    def ask_promotion_piece(self, color='white'):
        """ Opens a dialog box to ask what to promote a pawn to """
        dialog = tk.Frame(self)
        dialog.config(bd=2, relief='raised')

        button_frame = tk.Frame(dialog, padx=10, pady=10)
        button_frame.pack()

        pieces = ['q', 'r', 'b', 'n']
        selected_piece = queue.Queue()

        def on_select(piece_code):
            dialog.destroy()
            selected_piece.put(piece_code)
            default_piece = 'Q' if color == 'white' else 'q'
            print(f'Returning {piece_code}')
            return piece_code if piece != '' else default_piece

        for piece in pieces:
            piece = piece.upper() if color == 'white' else piece
            tk.Button(button_frame, image=self.image_cache[piece], command=lambda p=piece: on_select(p))\
                .pack(side='left', padx=10, pady=10)

        x, y = self.winfo_width() // 2, self.winfo_height() // 2
        self.create_window((x, y), window=dialog)

        dialog.wait_window()
        return selected_piece.get()

    def end_dialog(self, winner, auto_restart=False):
        """ Opens dialog box giving user option to rest or go back to menu """
        self.drawing = False

        if auto_restart:
            self.reset()
        else:
            dialog = tk.Frame(self)

            message = ''
            match winner:
                case 'disconnect':
                    message = 'Connection lost'
                case 'draw':
                    message = 'Draw!'
                case _:
                    message = f'{winner.capitalize()} wins!'
            
            msg_lbl = tk.Label(dialog, text=message, font=(FONT, -int(self.icon_size * 0.75)))
            msg_lbl.pack(pady=10)

            def close_dialog():
                self.reset()
                dialog.destroy()
                self.start_game()

            def nav_to_menu():
                self.reset()
                dialog.destroy()
                self.parent.show_start_menu()

            if winner != 'disconnect':
                tk.Button(dialog, text='Reset', command=close_dialog, font=(FONT, -int(self.icon_size * 0.5))).pack(pady=10)
            tk.Button(dialog, text='Menu', command=nav_to_menu, font=(FONT, -int(self.icon_size * 0.5))).pack(pady=10)

            # position frame in middle of window
            x, y = self.winfo_width() // 2, self.winfo_height() // 2
            self.create_window((x, y), window=dialog)

            dialog.wait_window()

    def start_game(self):
        """ Starts game thread and draw loop """
        self.game_manager.reset()
        self.game_thread = threading.Thread(target=self.game_manager.game_loop, daemon=True)
        self.game_thread.start()
        self.drawing = True
        self.after(100, self.draw_board)

    def set_player_types(self, white='player', black='bot'):
        """ Sets player types as player, bot, or lan_opp """
        self.game_manager.set_player_types(white, black)
        self.info_bar.set_player_types(white, black)

    def reset(self):
        """ Resets GUI - unselects cells and clears pieces """
        self.kill_game_thread()
        self.cell_selected = None
        delete_widgets = []
        for widget in self.widgets.keys():
            if 'p' in widget:
                # a 'p' in a widget key indicates the widget is a piece
                self.delete(self.widgets[widget])
                delete_widgets.append(widget)
        for widget in delete_widgets:
            del self.widgets[widget]

    def kill_game_thread(self):
        if self.game_thread is not None and self.game_thread.is_alive():
            self.game_manager.interrupt_game_loop()
            self.game_thread.join()

    def return_to_menu(self):
        """ Called by InfoBar to return to main menu """
        self.reset()
        self.kill_game_thread()
        self.parent.show_start_menu()