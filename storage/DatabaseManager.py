import sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class DatabaseManager:
    def __init__(self, username, password, host='chesscluster.pnlwyv0.mongodb.net', extension='?retryWrites=true&w=majority&appName=ChessCluster'):
        self.username = username
        self.password = password
        self.host = host
        self.extension = extension

        uri = f'mongodb+srv://{username}:{password}@{host}/{extension}'

        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client.chess
        self.collection = self.db['moves']

    def ping(self):
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(e)
            return False

    def store_board_log(self, board_log):
        for log_entry in board_log.get_log():
            pass

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

if __name__ == '__main__':
    db = DatabaseManager(sys.argv[1], sys.argv[2])
    if db.ping():
        print('Successful connection to MongoDB')
