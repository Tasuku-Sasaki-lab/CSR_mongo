import unittest
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.results import (InsertOneResult,
                             InsertManyResult,
                             UpdateResult,
                             DeleteResult)

from CSR_mongo.lib import mongo
from CSR_mongo.tests.mongo_test_lib import MongoForTest


class TestMongo(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        correct_url = 'localhost'
        correct_DB_name = "test"
        correct_collection_name = "test"
        correct_user_name = "testuser"
        correct_password = "password"
        self.testMongo = MongoForTest(
            correct_user_name,  correct_password, correct_url,  correct_DB_name, correct_collection_name)

        self.serverA = mongo.Mongo(correct_user_name,  correct_password,
                                   correct_url,  correct_DB_name, correct_collection_name)
        self.serverB = mongo.Mongo(
            "error_user_name",  correct_password, correct_url,  correct_DB_name, correct_collection_name)
        self.serverC = mongo.Mongo(
            correct_user_name,  "error_password", correct_url,  correct_DB_name, correct_collection_name)
        self.serverD = mongo.Mongo(
            correct_user_name,  correct_password, "error_url",  correct_DB_name, correct_collection_name)

    def setUp(self):
        self.testMongo.clear()

    def testConnect(self):
        post = {"_id": 1000}
        document = "Fail to get the deviece from the database.(getOne()) Authentication failed., full error: {'ok': 0.0, 'errmsg': 'Authentication failed.', 'code': 18, 'codeName': 'AuthenticationFailed'}"
        try:
            self.serverB.getOne(post)
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        try:
            self.serverC.getOne(post)
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        document = "Fail to get the deviece from the database.(getOne()) error_url:27017: [Errno -2] Name or service not known, Timeout: 30s"
        try:
            self.serverD.getOne(post)
        except SystemExit as e:
            self.assertEqual(e.code[:120], document)
        else:
            self.fail('SystemExit exception expected')

    def testAddOne(self):
        post = {"_id": 1000}
        result = self.serverA.addOne(post)
        self.assertTrue(result, InsertOneResult)
        self.assertTrue(isinstance(result.inserted_id, int))
        self.assertEqual(post["_id"], result.inserted_id)
        self.assertTrue(result.acknowledged)
        self.assertIsNotNone(self.testMongo.getData({"_id": post["_id"]}))
        self.assertEqual(1, self.testMongo.countData({}))

    def testAddMany(self):
        docs = [{} for _ in range(5)]
        result = self.serverA.addMany(docs)
        self.assertTrue(isinstance(result, InsertManyResult))
        self.assertTrue(isinstance(result.inserted_ids, list))
        self.assertEqual(5, len(result.inserted_ids))
        for doc in docs:
            _id = doc["_id"]
            self.assertTrue(isinstance(_id, ObjectId))
            self.assertTrue(_id in result.inserted_ids)
            self.assertEqual(1, self.testMongo.countData({'_id': _id}))
        self.assertTrue(result.acknowledged)

    def testGetOne(self):
        post = {'csrID': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US', 'secret': 'pass',
                'expiration_date': datetime(2023, 1, 30, 16, 43, 8)}
        self.testMongo.insertData(post)
        self.assertEqual(post, self.serverA.getOne(
            {'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US'}))
        self.assertIsNone(self.serverA.getOne(
            {'CN': 'spaceclient'}))
        """ここもっと丁寧にテストする"""

    def testGetCount(self):
        self.assertEqual(self.serverA.getCount({}), 0)
        self.testMongo.insertData({})
        self.assertEqual(self.serverA.getCount({}), 1)
        self.testMongo.insertData({'foo': 'bar'})
        self.assertEqual(self.serverA.getCount({'foo': 'bar'}), 1)

    def testUpdateMany(self):
        self.testMongo.insertData({"x": 4, "y": 3})
        self.testMongo.insertData({"x": 5, "y": 5})
        self.testMongo.insertData({"x": 4, "y": 4})

        result = self.serverA.updateMany({"x": 4}, {"$set": {"y": 5}})
        self.assertTrue(isinstance(result, UpdateResult))
        self.assertEqual(2, result.matched_count)
        self.assertTrue(result.modified_count in (None, 2))
        self.assertIsNone(result.upserted_id)
        self.assertTrue(result.acknowledged)
        self.assertEqual(3, self.testMongo.countData({"y": 5}))

        result = self.serverA.updateMany({"x": 2}, {"$set": {"y": 1}}, True)
        self.assertTrue(isinstance(result, UpdateResult))
        self.assertEqual(0, result.matched_count)
        self.assertTrue(result.modified_count in (None, 0))
        self.assertTrue(isinstance(result.upserted_id, ObjectId))
        self.assertTrue(result.acknowledged)

    def testDeleteOne(self):
        self.testMongo.insertData({"x": 1})
        self.testMongo.insertData({"y": 1})
        self.testMongo.insertData({"z": 1})

        result = self.serverA.deleteOne({"x": 1})
        self.assertTrue(isinstance(result, DeleteResult))
        self.assertEqual(1, result.deleted_count)
        self.assertTrue(result.acknowledged)
        self.assertEqual(2, self.testMongo.countData({}))

        result = self.serverA.deleteOne({"y": 1})
        self.assertTrue(isinstance(result, DeleteResult))
        self.assertEqual(1, result.deleted_count)
        self.assertTrue(result.acknowledged)
        self.assertEqual(1, self.testMongo.countData({}))

    def testDeleteMany(self):
        self.testMongo.insertData({"x": 1})
        self.testMongo.insertData({"x": 1})
        self.testMongo.insertData({"y": 1})
        self.testMongo.insertData({"y": 1})

        result = self.serverA.deleteMany({"x": 1})
        self.assertTrue(isinstance(result, DeleteResult))
        self.assertEqual(2, result.deleted_count)
        self.assertTrue(result.acknowledged)
        self.assertEqual(0, self.testMongo.countData({"x": 1}))


if __name__ == '__main__':
    unittest.main()
