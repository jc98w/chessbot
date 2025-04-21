class BoardLog:

    def __init__(self):
        self.log = []

    def add_state(self, board):
        self.log.append(board)
