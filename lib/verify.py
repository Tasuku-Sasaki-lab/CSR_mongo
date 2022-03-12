from datetime import datetime
from dateutil import relativedelta
from bson.objectid import ObjectId  # ObjectId(oid)
import sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from CSR_mongo.lib import mongo
from CSR_mongo.lib import db


def setMongo():
    url = db.DUR
    db_name = db.DSN
    collection_name = db.DCL
    user_name = db.USN
    passwd = db.PWD

    """
        DBNAMEと　コレクションネーム　を考えるなら　ここやな
    """

    return mongo.Mongo(user_name, passwd, url, db_name, collection_name)


"""
-Unable to load PEM file. See https://cryptography.io/en/latest/faq.html#why-can-t-i-import-my-pem-file
 for more details. MalformedFraming

-Valid PEM but no BEGIN CERTIFICATE REQUEST/END CERTIFICATE REQUEST delimiters.
 Are you sure this is a CSR?
"""


def getCSR():
    pem_file = None
    try:
        pem_file = sys.stdin.read().encode()
    except Exception as e:
        exit(str(e))

    try:
        return x509.load_pem_x509_csr(pem_file)
    except Exception as e:
        exit(str(e))


def getDevice(device_id):
    obj = setMongo()
    return obj.getOne({"CN": device_id})


"""
    Format as RFC4514 Distinguished Name string.
    For example 'CN=foobar.com,O=Foo Corp,C=US'

    An X.509 name is a two-level structure: a list of sets of attributes.
    Each list element is separated by ',' and within each list element, set
    elements are separated by '+'. The latter is almost never used in
    real world certificates. According to RFC4514 section 2.1 the
     RDNSequence must be reversed when converting to string representation.
"""


def getDeviceID(csr):
    try:
        return csr.subject.rfc4514_string()
    except Exception as e:
        exit(str(e))


def certificateCSR(device, passwd): 
    if device is None:
        exit("The device_id (RFC4514 Distinguished Name string) is not mathched")

    if device.get("expiration_date") is None:
        exit("The expiration_date is not set.")
    elif datetime.now() > device["expiration_date"]:
        exit("The csr has been expired.")

    if device.get("secret") is None:
        exit("The secret is not set.")
    elif device["secret"] != passwd:
        exit("The password is not corect")

    return 0


def getPasswd():
    value = sys.argv
    if len(value) > 2:
        exit("The number of command-line arguments is too many.")
    elif len(value) < 2:
        exit("A challenge password password is not set in command-line arguments.")
    else:
        return value[1]


"""
This process gets a PEM file from stdin and a challenge password from command-line arguments.
If the password is the same as what has been registered in a database, the program will retrn 0.

The mongod server must be started in addition. Check with mongo.py.
"""


def setUp():
    now = datetime.now()
    td = relativedelta.relativedelta(years=1)
    post = {"csrID": 1, "csrGroup": 1, "CN": "CN=TEST1,OU=MDM,O=scep-client,C=US",
            "secret": "pass", "expiration_date": now + td}
    setMongo().deleteMany({"CN": "CN=TEST1,OU=MDM,O=scep-client,C=US"})
    setMongo().addOne(post)



def main():
    csr = getCSR()

    device_id = getDeviceID(csr)
    device = getDevice(device_id)
    passwd = getPasswd()

    exit(certificateCSR(device, passwd))


if __name__ == '__main__':
    #setUp()
    main()