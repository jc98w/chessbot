import re
import threading
import tkinter as tk
from random import random

class MenuFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.server_manager = parent.server_manager
        self.client_manager = parent.client_manager
        self.agent_type = None
        self.udp_broadcast_thread = None
        self.udp_listen_thread = None

        self.user_list = tk.Variable()
        self.username = tk.StringVar(value=self.server_manager.get_username())
        self.username.trace('w', self.username_check)
        self.host_button = None
        self.username_box = None
        self.matches_listbox = None

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

        self.bind('<<Connected>>', self.start_host_match)

        self.shutdown_flag = False

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

        exit_button = tk.Button(button_frame, text='Exit', command=self.parent.close)

        # Grid pack objects into MenuFrame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        white_king_symbol.grid(row=0, column=0, pady=10, ipadx=10, sticky='e')
        white_bot_checkbutton.grid(row=0, column=1, pady=10, sticky='w')
        black_king_symbol.grid(row=1, column=0, pady=10, ipadx=10, sticky='e')
        black_bot_checkbutton.grid(row=1, column=1, pady=10, sticky='w')
        start_button.grid(row=2, column=0, columnspan=3, pady=10)
        lan_button.grid(row=3, column=0, columnspan=3, pady=10)
        exit_button.grid(row=4, column=0, columnspan=3, pady=10)

        return button_frame

    def prep_lan_frame(self):
        """ Sets up frame for setting up lan multiplayer """
        lan_frame = tk.Frame(self)

        # Return to options menu button
        back_button = tk.Button(lan_frame, text='back', command=lambda: self.set_frame(self.options_frame))

        # Show list of matches that can be joined
        match_list_label = tk.Label(lan_frame, text='available matches')
        self.matches_listbox = tk.Listbox(lan_frame, listvariable=self.user_list,selectmode=tk.SINGLE)
        self.matches_listbox.bind('<<ListboxSelect>>', self.select_host)

        # Widgets for hosting
        self.host_button = tk.Button(lan_frame, text='host', command=self.host)

        self.username_box = tk.Entry(lan_frame, textvariable=self.username)

        # Arrange widgets in lan_frame
        back_button.grid(row=0, column=0, sticky='w')
        match_list_label.grid(row=0, column=1)
        self.matches_listbox.grid(row=1, column=1, columnspan=2)
        self.host_button.grid(row=3, column=0)
        self.username_box.grid(row=3, column=1)

        return lan_frame

    def pack(self, *args, **kwargs):
        """ Overrides Frame::pack
            Sets current_frame to options_frame when the menu is packed """
        tk.Frame.pack(self, *args, **kwargs)
        self.current_frame = self.options_frame

    def username_check(self, *args):
        """ Keeps username entry limited to 10 alphanumeric characters
            Disables host button if username is empty """
        name = self.username.get()
        button_state = tk.DISABLED if name == '' else tk.NORMAL
        self.host_button.config(state=button_state)
        fixed_name = ''
        for index, char in enumerate(name):
            if char.isalnum() and index < 10:
                fixed_name += char
        self.username.set(fixed_name)

    def set_frame(self, frame):
        """ unpacks current frame and packs selected frame """
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill='y', expand=True)

        if self.current_frame == self.lan_frame:
            self.udp_listen_thread = threading.Thread(target=self.check_for_opponents)
            self.udp_listen_thread.start()
        else:
            self.server_manager.end_broadcast()

    def start_match(self):
        """ Exits menu and starts game """
        if self.current_frame == self. options_frame:
            self.white_player_status = 'bot' if self.white_is_bot.get() else 'player'
            self.black_player_status = 'bot' if self.black_is_bot.get() else 'player'
        self.shutdown()
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
            if self.client_manager.receive_broadcast():
                for user in (self.client_manager.get_users()):
                    if user != self.username.get() and user not in self.user_list.get():
                        self.matches_listbox.insert(tk.END, user)

    def host(self):
        """ Become game host """
        username = self.username.get()
        self.server_manager.set_username(username)

        self.udp_broadcast_thread = threading.Thread(target=self._host_thread)
        self.udp_broadcast_thread.start()

    def _host_thread(self):
        """ Helper for host method. Triggers event when connection is established to start game """
        self.server_manager.establish_connection()
        self.white_player_status = 'player' if random() < 0.5 else 'lan_opp'
        self.black_player_status = 'player' if self.white_player_status == 'lan_opp' else 'lan_opp'
        if not self.shutdown_flag:
            self.event_generate('<<Connected>>', when='tail')

    def start_host_match(self, event):
        """ Configure lan match as host and start game """
        lan_opp_color = 'white' if self.white_player_status == 'lan_opp' else 'black'
        # Tell opponent what color they will play
        self.server_manager.send_data(lan_opp_color)
        self.agent_type = 'host'
        print('starting game as host...')
        self.start_match()

    def select_host(self, event):
        """ Connects to host from list of available matches """
        index = self.matches_listbox.curselection()
        host_user = self.matches_listbox.get(index)
        self.client_manager.connect(host_user)
        client_color = self.client_manager.receive_data()
        self.white_player_status = 'player' if client_color == 'white' else 'lan_opp'
        self.black_player_status = 'player' if client_color == 'black' else 'lan_opp'
        self.agent_type = 'client'
        print('Starting game as client...')
        self.start_match()

    def shutdown(self):
        """ End check_for_opponent loop """
        self.shutdown_flag = True
        self.current_frame = None