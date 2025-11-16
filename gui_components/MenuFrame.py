import tkinter as tk

class MenuFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Default to white being the player and black being a bot
        self.white_is_bot = tk.BooleanVar()
        self.black_is_bot = tk.BooleanVar()
        self.white_is_bot.set(False)
        self.black_is_bot.set(True)

        self.pack_menu_widgets()


    '''
    * Sets up the menu widgets for selecting bots, starting a game, and entering LAN multiplayer
    '''
    def pack_menu_widgets(self):
        button_frame = tk.Frame(self)

        # Make radiobuttons for selecting if black and white are players or bots
        white_king_symbol = tk.Label(button_frame, text='♔')
        white_bot_checkbutton = tk.Checkbutton(button_frame, text='bot', variable=self.white_is_bot)
        black_king_symbol = tk.Label(button_frame, text='♚')
        black_bot_checkbutton = tk.Checkbutton(button_frame, text='bot', variable=self.black_is_bot)

        # Buttons for entering game or setting up LAN multiplayer
        start_button = tk.Button(button_frame, text='Start match', command=self.start_match)
        lan_button = tk.Button(button_frame, text='LAN match', command=self.config_lan_match)

        # Use grid to pack objects into MenuFrame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        white_king_symbol.grid(row=0, column=0)
        white_bot_checkbutton.grid(row=0, column=1, pady=10)
        black_king_symbol.grid(row=1, column=0, pady=10)
        black_bot_checkbutton.grid(row=1, column=1, pady=10)
        start_button.grid(row=2, column=0, columnspan=3, pady=10)
        lan_button.grid(row=3, column=0, columnspan=3, pady=10)

        button_frame.pack(fill='y', ipadx=60, expand=True)

    '''
    * Exits menu and starts game
    '''
    def start_match(self):
        self.parent.start_game()

    '''
    * Allows user to configure a LAN match
    '''
    def config_lan_match(self):
        # TODO: implement config_lan_match
        pass

    '''
    * Returns if white is a bot
    '''
    def get_white_is_bot(self):
        return self.white_is_bot.get()

    '''
    * Returns if black is a bot
    '''
    def get_black_is_bot(self):
        return self.black_is_bot.get()