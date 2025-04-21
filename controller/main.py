import tkinter as tk

from gui_components.BoardFrame import BoardFrame

def reset_board():
    board.reset()

if __name__ == '__main__':
    root = tk.Tk("Chess")
    root.geometry("500x500")

    menubar = tk.Menu(root)
    game_menu = tk.Menu(menubar, tearoff=0)
    game_menu.add_command(label="Reset", command=reset_board)
    menubar.add_cascade(label="Game", menu=game_menu)
    root.config(menu=menubar)

    board = BoardFrame(root)
    board.pack(fill=tk.BOTH, expand=True)

    root.mainloop()