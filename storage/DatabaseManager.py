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
        self.collection = self.db['bot_one_data']

    def ping(self):
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(e)
            return False

    def create(self, data):
        try:
            if data is None:
                raise Exception('Data is None')
            insert = self.collection.insert_many(data) if isinstance(data, list) else self.collection.insert_one(data)
            return insert.acknowledged
        except Exception as e:
            print(e)
            return None

    def read(self, data, many=False):
        try:
            return self.collection.find(data) if many else self.collection.find_one(data)
        except Exception as e:
            print(e)
            return None

    def update(self, find_data, update_data):
        try:
            result =  self.collection.update_many(find_data, {'$set': update_data})
            return result.modified_count
        except Exception as e:
            print(e)
            return None

    def delete(self, data):
        try:
            result = self.collection.delete_many(data)
            return result.deleted_count
        except Exception as e:
            print(e)
            return None

if __name__ == '__main__':
    db = DatabaseManager(sys.argv[1], sys.argv[2])
    if db.ping():
        print('Successful connection to MongoDB')
