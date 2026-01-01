import tkinter as tk

class InfoBar(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.white_player_type = tk.StringVar()
        self.black_player_type = tk.StringVar()
        self.turn = tk.StringVar()

        self.back_button = tk.Button(self, text='Back', command=self.return_to_menu)
        self.white_label = tk.Label(self, textvariable=self.white_player_type)
        self.black_label = tk.Label(self, textvariable=self.black_player_type)
        self.turn_label = tk.Label(self, textvariable=self.turn)

        self.back_button.grid(row=0, column=0, sticky='w', padx=10)
        self.white_label.grid(row=0, column=1, sticky='w', padx=10)
        self.black_label.grid(row=0, column=2, sticky='w', padx=10)
        self.turn_label.grid(row=0, column=3, sticky='w', padx=10)

    def set_font_size(self, size):
        for widget in (self.back_button, self.white_label, self.black_label, self.turn_label):
            widget.configure(font=('Arial', size))

    def set_player_types(self, white, black):
        """ Sets the player types to be displayed by info bar """
        self.white_player_type.set(f'White: {white}')
        self.black_player_type.set(f'Black: {black}')

    def set_turn(self, turn):
        """ Sets whose turn it is to be displayed in info bar"""
        self.turn.set(f'Turn: {turn}')

    def return_to_menu(self):
        """ Ends game and returns to menu """
        self.parent.return_to_menu()