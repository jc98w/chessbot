import tkinter as tk

from gui_components.BoardCanvas import BoardCanvas
from gui_components.MenuFrame import MenuFrame

BACKGROUND_GREEN = '#228833'
BACKGROUND_WHITE = '#EEEEEE'
DEFAULT_FONT = 'Arial, 20'

class ChessApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("ChessBot")
        self.geometry("500x500")
        self.set_default_styles()

        # Create frames for menu and game
        self.current_frame = None
        self.menu_frame = MenuFrame(self)
        self.board_canvas = BoardCanvas(self)
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
        white_bot_status = self.menu_frame.get_white_is_bot()
        black_bot_status = self.menu_frame.get_black_is_bot()
        self.board_canvas.set_bots(white=white_bot_status, black=black_bot_status)
        self.board_canvas.after(1000, self.board_canvas.trigger_bot_move)

if __name__ == '__main__':
    root = ChessApp()
    root.show_start_menu()

    root.mainloop()
