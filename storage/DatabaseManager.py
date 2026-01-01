import threading
from pymongo.mongo_client import MongoClient
from storage.BoardLog import BoardLog

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

        threading.Thread(target=self.connect).start()

    def connect(self):
        """ Connect to MongoDB """
        uri = 'mongodb://localhost:27017/'
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=1000)
            self.db = self.client.chess
            self.collection = self.db['bot_one_data']
        except Exception as e:
            print('Unable to connect to MongoDB:', e)

    def ping(self):
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print('Unable to ping MongoDB')
            return False

    def create(self, data):
        try:
            if data is None:
                raise Exception('Data is None')
            insert = self.collection.insert_many(data) if isinstance(data, list) else self.collection.insert_one(data)
            return insert.acknowledged
        except Exception as e:
            print('Error in DatabaseManager.create')
            print(e)
            return None

    def read(self, data, many=False):
        try:
            return self.collection.find_one(data) if many == False else self.collection.find(data)
        except Exception as e:
            print('Error in DatabaseManager.read')
            print(e)
            return None

    def update(self, find_data, update_data):
        try:
            result =  self.collection.update_many(find_data, {'$set': update_data})
            return result.modified_count
        except Exception as e:
            print('Error in DatabaseManager.update')
            print(e)
            return None

    def delete(self, data):
        try:
            result = self.collection.delete_many(data)
            return result.deleted_count
        except Exception as e:
            print('Error in DatabaseManager.delete')
            print(e)
            return None

    def commit_log(self, board_log, winner):
        try:
            inserts = []
            if board_log is None:
                raise Exception('Board log is None')
            data = board_log.prepare_data(winner)
            for log in data:
                board_str = log['board']
                query = self.read({'board': board_str})
                if query is None:
                    inserts.append(log)
                else:
                    BoardLog.merge_log_into_list(log, [query])
                    self.update({'board': board_str}, query)
            if len(inserts) > 0:
                self.create(inserts)
            return True
        except Exception as e:
            print('Error in DatabaseManager.commit_log')
            print(e)
            return False

if __name__ == '__main__':
    db = DatabaseManager()
    if db.ping():
        print('Successful connection to MongoDB')
        print(db.read({'board':'rnbqkbnrpppppppp32PPPPPPPPRNBQKBNRKQkq'}))
    else:
        print('Failed to connect to MongoDB')
