# CSR_mongo
# Features
This process gets a PEM file from stdin and a challenge password from command-line arguments.
If the password is the same as what has been registered in a database, the program will exit with 0. 
<br>
Futhermore, if errors and exceptions happen, the program will exit with the error messages.
<br>
The mongod server must be started in addition. Check with mongo.py.


# Installation
Install CSR_mongo with pip command.
```bash
pip install CSR_mongo
```


# EAMPLE SETUP
Before testing,<br>
1.start mongod<br>
2, create a user<br>

1, start mongod
<br>
```bash
$sudo service mongod start
```

<br>
2, create a test user
<br>

```bash
$mongo
>use admin
>db.createUser({
  user:"admin",
  pwd:"pass",
  roles:[{ role:"userAdminAnyDatabase", db:"admin" }]
})
>db.auth("admin", "pass")

> use test
> db.createUser(
  {
    user: "testuser",
    pwd:"password",
    roles:[
       {role:"readWrite",  db:"verify"},
       {role:"readWrite",  db:"verify"},
    ]
  }
)
>quit()
```

<br>
```bash
$python3 -m CSR_mongo.lib.example_setup
$cat CSR_mongo/csr.pem | python3 -m CSR_mongo.lib.verify pass 
```

# Data Example
```bash
{"csrID":1,"csrGroup":1,"CN":"CN=TEST1,OU=MDM,O=scep-client,C=US","secret":"pass","expiration_date":datetome.now() + rekative}
```

# TEST
Before testing,<br>
1.start mongod<br>
2, create a testuser<br>
<br>
1, start mongod
<br>
```bash
$sudo service mongod start
```
<br>
2, create a test user

```bash
$mongo
>use admin
>db.createUser({
  user:"admin",
  pwd:"pass",
  roles:[{ role:"userAdminAnyDatabase", db:"admin" }]
})
>db.auth("admin", "pass")

> use test
> db.createUser(
  {
    user: "testuser",
    pwd:"password",
    roles:[
       {role:"readWrite",  db:"test"},
       {role:"readWrite",  db:"test"},
    ]
  }
)
```

This is how to test.
```bash
$ python3 -m unittest CSR_mongo.tests.test_mongo
```
<br>
(This will take about 30s)
<br>

```bash
$ python3 -m unittest CSR_mongo.tests.test_verify
```


# Auther
Tasuku Sasaki<br>
Gmail: t.sasaki.revol@gmail.com



