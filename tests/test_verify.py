import unittest
import sys
from xml.dom.minidom import Document
from datetime import datetime
from dateutil import relativedelta
from bson.objectid import ObjectId
from io import StringIO, BytesIO
from unittest.mock import patch
import builtins
from cryptography import x509

from CSR_mongo.lib import verify


class DevNull(object):
    data = []

    def write(self, data):
        self.data.append(data)

    def clear(self):
        self.data = []


class TestVerify(unittest.TestCase):
    def setUp(self):
        self._stderr = DevNull()
        self.original_stderr = sys.stderr
        sys.stderr = self._stderr

    def tearDown(self):
        sys.stderr = self.original_stderr

    def testSetMongo(self):
        return 0

    def testGetCSR(self):
        with patch.object(sys, "stdin", StringIO("Thanks. This is correct")):
            self.assertEqual(sys.stdin.read(), "Thanks. This is correct")

        f = open("CSR_mongo/csr.pem", "r")
        answer = x509.load_pem_x509_csr(f.read().encode())
        f = open("CSR_mongo/csr.pem", "r")
        with patch.object(sys, "stdin", f):
            self.assertEqual(answer, verify.getCSR())

        with patch.object(sys, "stdin", StringIO("Thanks. This is correct")):
            document = "Unable to load PEM file. See https://cryptography.io/en/latest/faq.html#why-can-t-i-import-my-pem-file for more details. MalformedFraming"
            try:
                verify.getCSR()
            except SystemExit as e:
                self.assertEqual(e.code, document)
            else:
                self.fail('SystemExit exception expected')

        f = open("CSR_mongo/client.pem", "r")
        with patch.object(sys, "stdin", f):
            document = "Valid PEM but no BEGIN CERTIFICATE REQUEST/END CERTIFICATE REQUEST delimiters. Are you sure this is a CSR?"
            try:
                verify.getCSR()
            except SystemExit as e:
                self.assertEqual(e.code, document)
            else:
                self.fail('SystemExit exception expected')

        f = open("CSR_mongo/test.txt", "r")
        with patch.object(sys, "stdin", f):
            document = "Unable to load PEM file. See https://cryptography.io/en/latest/faq.html#why-can-t-i-import-my-pem-file for more details. MalformedFraming"
            try:
                verify.getCSR()
            except SystemExit as e:
                self.assertEqual(e.code, document)
            else:
                self.fail('SystemExit exception expected')

        f = open("CSR_mongo/test.txt", "rb")
        with patch.object(sys, "stdin", f):
            document = "'bytes' object has no attribute 'encode'"
            try:
                verify.getCSR()
            except SystemExit as e:
                self.assertEqual(e.code, document)
            else:
                self.fail('SystemExit exception expected')

        with patch.object(sys, "stdin", BytesIO(b"some initial binary data: \x00\x01")):
            document = "'bytes' object has no attribute 'encode'"
            try:
                verify.getCSR()
            except SystemExit as e:
                self.assertEqual(e.code, document)
            else:
                self.fail('SystemExit exception expected')

    def testGetDevice(self):
        return 0

    def testGetDeviceID(self):
        f = open("CSR_mongo/csr.pem", "r")
        csr = x509.load_pem_x509_csr(f.read().encode())
        self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                         verify.getDeviceID(csr))

        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID("qq"))
        except SystemExit as e:
            self.assertEqual(e.code, "'str' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(1))
        except SystemExit as e:
            self.assertEqual(e.code, "'int' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(True))
        except SystemExit as e:
            self.assertEqual(
                e.code, "'bool' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        f = open("CSR_mongo/test.txt", "r")
        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(f))
        except SystemExit as e:
            self.assertEqual(
                e.code, "'_io.TextIOWrapper' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        f = open("CSR_mongo/test.txt", "rb")
        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(f))
        except SystemExit as e:
            self.assertEqual(
                e.code, "'_io.BufferedReader' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        f = StringIO("Thanks. This is correct")
        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(f))
        except SystemExit as e:
            self.assertEqual(
                e.code, "'_io.StringIO' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

        f = BytesIO(b"some initial binary data: \x00\x01")
        try:
            self.assertEqual("CN=TEST1,OU=MDM,O=scep-client,C=US",
                             verify.getDeviceID(f))
        except SystemExit as e:
            self.assertEqual(
                e.code, "'_io.BytesIO' object has no attribute 'subject'")
        else:
            self.fail('SystemExit exception expected')

    def testCertificateCSR(self):
        now = datetime.now()
        td = relativedelta.relativedelta(years=1)
        post = {'_id': ObjectId('61fe2676e456a70780d1fbf1'), 'csrID': 1, 'csrGroup': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US',
                'secret': 'pass', 'expiration_date': now + td}
        self.assertEqual(0, verify.certificateCSR(post, "pass"))

        document = "The device_id (RFC4514 Distinguished Name string) is not mathched"
        try:
            verify.certificateCSR(None, "pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        document = "The expiration_date is not set."
        try:
            verify.certificateCSR(dict(), "pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        post = {'_id': ObjectId('61fe2676e456a70780d1fbf1'), 'csrID': 1, 'csrGroup': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US',
                'secret': 'pass'}
        try:
            verify.certificateCSR(post, "pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        td = relativedelta.relativedelta(years=-1)
        post = {'_id': ObjectId('61fe2676e456a70780d1fbf1'), 'csrID': 1, 'csrGroup': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US',
                'secret': 'pass', 'expiration_date': now + td}
        document = "The csr has been expired."
        try:
            verify.certificateCSR(post, "pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        td = relativedelta.relativedelta(years=1)
        post = {'_id': ObjectId('61fe2676e456a70780d1fbf1'), 'csrID': 1, 'csrGroup': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US',
                'expiration_date': now + td}
        document = "The secret is not set."
        try:
            verify.certificateCSR(post, "pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        post = {'_id': ObjectId('61fe2676e456a70780d1fbf1'), 'csrID': 1, 'csrGroup': 1, 'CN': 'CN=TEST1,OU=MDM,O=scep-client,C=US',
                'secret': 'pass', 'expiration_date': now + td}
        document = "The password is not corect"
        try:
            verify.certificateCSR(post, "error_pass")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        try:
            verify.certificateCSR(post, "")
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

    def testGetPasswd(self):
        sys.argv = ["filename", "pass"]
        self.assertEqual('pass', verify.getPasswd())

        sys.argv = ["filename"]
        document = "A challenge password password is not set in command-line arguments."
        try:
            verify.getPasswd()
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')

        sys.stderr = self.original_stderr
        sys.argv = ["filename", "pass1", "pass2"]
        document = "The number of command-line arguments is too many."
        try:
            verify.getPasswd()
        except SystemExit as e:
            self.assertEqual(e.code, document)
        else:
            self.fail('SystemExit exception expected')


if __name__ == '__main__':
    unittest.main()
