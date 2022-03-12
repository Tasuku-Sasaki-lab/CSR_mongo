from datetime import datetime
from logging import exception
from bson.objectid import ObjectId  # ObjectId(oid)
from pymongo.errors import OperationFailure
from pymongo import MongoClient


"""
ユーザー認証関連とと２つのクラスを作ってしまえばいいやろ
"""


class MongoForTest(object):
    def __init__(self, user_name, passwd, url, db_name, collection_name):
        self.client = MongoClient('mongodb://%s:%s@%s' %
                                  (user_name, passwd, url))
        self.db = self.client[db_name]
        self.collection = self.db.get_collection(collection_name)

    def insertData(self, post):
        self.collection.insert_one(post)

    def clear(self):
        self.collection.drop()

    def getData(self, post):
        return self.collection.find_one(post)

    def countData(self, post):
        return self.collection.count_documents(post)