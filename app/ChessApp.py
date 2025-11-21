import tkinter as tk

from gui_components.BoardCanvas2 import BoardCanvas2
from gui_components.MenuFrame import MenuFrame
from network.GameClient import GameClient
from network.GameHoster import GameHoster

BACKGROUND_GREEN = '#228833'
BACKGROUND_WHITE = '#EEEEEE'
DEFAULT_FONT = 'Arial, 20'

class ChessApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("ChessBot")
        self.geometry("500x500")
        self.set_default_styles()

        # Establish network managers
        self.server_manager = GameHoster()
        self.client_manager = GameClient()

        # Create frames for menu and game
        self.current_frame = None
        self.menu_frame = MenuFrame(self)
        self.board_canvas = BoardCanvas2(self)
        self.menu_frame['background'] = BACKGROUND_GREEN
        self.board_canvas['background'] = BACKGROUND_GREEN

    '''
    * sets some default values for widget styles
    '''
    def set_default_styles(self):
        self.option_add('*Background', BACKGROUND_WHITE)
        self.option_add('*Font', DEFAULT_FONT)

    '''
    * Hides the current frame to open space for new frame
    '''
    def hide_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = None

    '''
    * Switches view to start menu
    '''
    def show_start_menu(self):
        self.hide_current_frame()
        self.current_frame = self.menu_frame
        self.menu_frame.pack(fill='both', expand=True, anchor='center')

    '''
    * Switches view to game board
    '''
    def start_game(self):
        # Switch frame to board frame
        self.hide_current_frame()
        self.current_frame = self.board_canvas
        self.board_canvas.pack(fill='both', expand=True)

        # import settings from menu frame
        white_player_status = self.menu_frame.get_player_status('white')
        black_player_status = self.menu_frame.get_player_status('black')
        self.board_canvas.set_player_types(white_player_status, black_player_status)

        self.board_canvas.start_game()

    def close(self):
        self.board_canvas.kill_game_thread()
        root.destroy()

if __name__ == '__main__':
    root = ChessApp()
    root.show_start_menu()

    root.protocol('WM_DELETE_WINDOW', root.close)
    root.mainloop()
