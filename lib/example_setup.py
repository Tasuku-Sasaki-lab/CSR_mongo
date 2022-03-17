from datetime import datetime
from dateutil import relativedelta

from CSR_mongo.lib import mongo
from CSR_mongo.lib import db


def setMongo():
    url = db.DUR
    db_name = db.DSN
    collection_name = db.DCL
    user_name = db.USN
    passwd = db.PWD

    return mongo.Mongo(user_name, passwd, url, db_name, collection_name)


def setUp():
    now = datetime.now()
    td = relativedelta.relativedelta(years=1)
    post = {"csrID": 1, "csrGroup": 1, "CN": "CN=TEST1,OU=MDM,O=scep-client,C=US",
            "secret": "pass", "expiration_date": now + td}
    setMongo().deleteMany({"csrGroup": 1})
    setMongo().addOne(post)


if __name__ == '__main__':
    setUp()
