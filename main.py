import tkinter as tk

from gui_components.BoardFrame import BoardFrame

def reset_board():
    board.reset()

def toggle_bot():
    board.set_bots(white=is_white_bot.get(), black=is_black_bot.get())

def toggle_auto_restart():
    board.set_auto_restart(auto_restart.get())


if __name__ == '__main__':



    root = tk.Tk()
    root.title("ChessBot")
    root.geometry("500x500")

    menubar = tk.Menu(root)
    game_menu = tk.Menu(menubar, tearoff=0)
    game_menu.add_command(label="Reset", command=reset_board)
    auto_restart = tk.BooleanVar()
    auto_restart.set(False)
    game_menu.add_checkbutton(label='Autorestart', variable=auto_restart, command=toggle_auto_restart)
    game_menu.add_separator()
    game_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="Game", menu=game_menu)
    bot_menu = tk.Menu(menubar, tearoff=0)
    is_white_bot = tk.BooleanVar()
    is_white_bot.set(False)
    is_black_bot = tk.BooleanVar()
    is_black_bot.set(True)
    bot_menu.add_checkbutton(label="White", variable=is_white_bot, command=toggle_bot)
    bot_menu.add_checkbutton(label="Black", variable=is_black_bot, command=toggle_bot)
    menubar.add_cascade(label="Bots", menu=bot_menu)
    root.config(menu=menubar)

    board = BoardFrame(root)
    board.pack(fill=tk.BOTH, expand=True)

    root.after(1000, board.trigger_bot_move())

    root.mainloop()
