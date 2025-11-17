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

        self.current_frame = None
        self.options_frame = self.prep_options_menu()
        self.lan_frame = self.prep_lan_frame()
        self.set_frame(self.options_frame)

    '''
    * Sets up the menu widgets for selecting bots, starting a game, and entering LAN multiplayer
    '''
    def prep_options_menu(self):
        button_frame = tk.Frame(self, padx=50)

        # Make radiobuttons for selecting if black and white are players or bots
        white_king_symbol = tk.Label(button_frame, text='♔')
        white_bot_checkbutton = tk.Checkbutton(button_frame, text='bot', variable=self.white_is_bot)
        black_king_symbol = tk.Label(button_frame, text='♚')
        black_bot_checkbutton = tk.Checkbutton(button_frame, text='bot', variable=self.black_is_bot)

        # Buttons for entering game or setting up LAN multiplayer
        start_button = tk.Button(button_frame, text='Start match', command=self.start_match)
        lan_button = tk.Button(button_frame, text='LAN match', command=lambda: self.set_frame(self.lan_frame))

        # Use grid to pack objects into MenuFrame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        white_king_symbol.grid(row=0, column=0, pady=10, ipadx=10, sticky='e')
        white_bot_checkbutton.grid(row=0, column=1, pady=10, sticky='w')
        black_king_symbol.grid(row=1, column=0, pady=10, ipadx=10, sticky='e')
        black_bot_checkbutton.grid(row=1, column=1, pady=10, sticky='w')
        start_button.grid(row=2, column=0, columnspan=3, pady=10)
        lan_button.grid(row=3, column=0, columnspan=3, pady=10)

        return button_frame

    '''
    * Sets up frame for setting up lan multiplayer
    '''
    def prep_lan_frame(self):
        lan_frame = tk.Frame(self)

        # Return to options menu button
        back_button = tk.Button(lan_frame, text='back', command=lambda: self.set_frame(self.options_frame))

        # Show list of matches that can be joined
        match_list_label = tk.Label(lan_frame, text='Available matches')
        available_matches = tk.Listbox(lan_frame)

        # Arrange widgets in lan_frame
        back_button.grid(row=0, column=0, sticky='w')
        match_list_label.grid(row=0, column=2)
        available_matches.grid(row=1, column=2)

        return lan_frame

    '''
    * unpacks current frame and packs selected frame
    '''
    def set_frame(self, frame):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill='y', expand=True)

    '''
    * Exits menu and starts game
    '''
    def start_match(self):
        self.parent.start_game()

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