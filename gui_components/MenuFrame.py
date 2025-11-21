import threading
import tkinter as tk

class MenuFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.server_manager = parent.server_manager
        self.client_manager = parent.client_manager
        self.udp_broadcast_thread = None
        self.udp_listen_thread = None
        self.user_list = tk.Variable()

        # Default to white being the player and black being a bot
        self.white_is_bot = tk.BooleanVar()
        self.black_is_bot = tk.BooleanVar()
        self.white_is_bot.set(False)
        self.black_is_bot.set(True)

        self.white_player_status = 'player'
        self.black_player_status = 'bot'

        self.current_frame = None
        self.options_frame = self.prep_options_menu()
        self.lan_frame = self.prep_lan_frame()
        self.set_frame(self.options_frame)

    def prep_options_menu(self):
        """ Sets up the menu widgets for selecting bots, starting a game, and entering LAN multiplayer """
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

    def prep_lan_frame(self):
        """ Sets up frame for setting up lan multiplayer """
        lan_frame = tk.Frame(self)

        # Return to options menu button
        back_button = tk.Button(lan_frame, text='back', command=lambda: self.set_frame(self.options_frame))

        # Show list of matches that can be joined
        match_list_label = tk.Label(lan_frame, text='available matches')
        available_matches = tk.Listbox(lan_frame, listvariable=self.user_list,selectmode=tk.SINGLE)

        # Widgets for hosting
        host_button = tk.Button(lan_frame, text='host', command=self.host)
        username_box = tk.Entry(lan_frame)

        # Arrange widgets in lan_frame
        back_button.grid(row=0, column=0, sticky='w')
        match_list_label.grid(row=0, column=1)
        available_matches.grid(row=1, column=1, columnspan=2)
        host_button.grid(row=3, column=0)
        username_box.grid(row=3, column=1)

        return lan_frame

    def set_frame(self, frame):
        """ unpacks current frame and packs selected frame """
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill='y', expand=True)

        if self.current_frame == self.lan_frame:
            self.udp_listen_thread = threading.Thread(target=self.check_for_opponents)
            self.udp_listen_thread.start()

    def start_match(self):
        """ Exits menu and starts game """
        self.white_player_status = 'bot' if self.white_is_bot.get() else 'player'
        self.black_player_status = 'bot' if self.black_is_bot.get() else 'player'
        self.parent.start_game()

    def get_player_status(self, color):
        """ Returns player status - player, bot, or lan_opp (LAN opponent)"""
        if color == 'white':
            return self.white_player_status
        elif color == 'black':
            return self.black_player_status
        else:
            return ''

    def check_for_opponents(self):
        """ Checks for UDP broadcasts from other users """
        while self.current_frame == self.lan_frame:
            self.client_manager.receive_broadcast()
            self.user_list.set(self.client_manager.get_users())

    def host(self):
        """ Become game host """
        self.udp_broadcast_thread = threading.Thread(target=self.server_manager.establish_connection)
        self.udp_broadcast_thread.start()
