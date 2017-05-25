
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

# Buckets : A Bucketlist API
 
## Introduction
A Bucket List is a list of things that one has not done before but wants to do before dying. Bonne Vie is an api for online bucket list service using Flask. Buckets allows you to interact with an api and perform CRUD (Create, Read, Update, Delete) operations on the bucket list.
 
## Installation
 
#### Clone Buckets GitHub repo:
 

`>>> git clone https://github.com/mojo706/bucketlist.git`

#### cd into the created folder create a virtualenv using virtualenvwrapper

`>>> mkvirtualenv --python=/usr/local/bin/python3 cp-bucketlist `

#### Activate the virtual environment

`>>> workon cp-bucketlist`

#### Use pip to install all the app requirements

`>>> pip install -r requirements.txt`

#### Create the database and run migrations

`>>> createdb bucketlist_api`

`>>> python manage.py db init`

`>>> python manage.py db migrate`

`>>> python manage.py db upgrade`   

#### For testing use the same process but with a different database eg. 

`>>> createdb test_db`

`>>> python manage.py db init`

`>>> python manage.py db migrate`

`>>> python manage.py db upgrade` 

#### All done! Now, start your server by running `>>> python manage.py runserver`. Use [postman](https://www.getpostman.com/) to make requests to the api.

### Endpoints

Here is a list of all the endpoints in bucketlist app.

Endpoint | Functionality| Access
------------ | ------------- | ------------- 
POST bucketlist/app/v1/auth/login |Logs a user in | PUBLIC
POST bucketlist/app/v1/auth/register | Registers a user | PUBLIC
POST bucketlist/app/v1/bucketlists/ | Creates a new bucket list | PRIVATE
GET bucketlist/app/v1/bucketlists/ | Lists all created bucket lists | PRIVATE
GET bucketlist/app/v1/bucketlists/id | Gets a single bucket list with the suppled id | PRIVATE
PUT bucketlist/app/v1/bucketlists/id | Updates bucket list with the suppled id | PRIVATE
DELETE bucketlist/app/v1/bucketlists/id | Deletes bucket list with the suppled id | PRIVATE
POST bucketlist/app/v1/bucketlists/id/items/ | Creates a new item in bucket list | PRIVATE
PUT bucketlist/app/v1/bucketlists/id/items/item_id | Updates a bucket list item | PRIVATE
DELETE bucketlist/app/v1/bucketlists/id/items/item_id | Deletes an item in a bucket list | PRIVATE

### Features:
* Search by name
* Pagination
* Token based authentication
### Searching

It is possible to search bucketlists using the parameter `q` in the GET request. 
Example:

`GET http://localhost:/bucketlists?q=Before I get to 30`

This request will return all bucketlists with `Before I get to 30` in their name.

### Pagination

It is possible to limit the count of bucketlist data displayed using the parameter `limit` in the GET request. 
Example:

`GET http://localhost:/bucketlist/api/v1.0/bucketlists?limit=3`

### Sample GET response
After a successful resgistration and login, you will receive an athentication token. Pass this token in your request header.
Below is a sample of a GET request for bucketlist

```
{
      "created_by": 1,
      "date_created": "Thu, 25 May 2017 10:57:19 GMT",
      "date_modified": "Thu, 25 May 2017 10:57:19 GMT",
      "id": 1,
      "items": [],
      "name": "Tracebacks "
    },
```

### Testing
The application tests are based on python’s unit testing framework unittest.
To run tests with nose, run `nosetests` . 
You Can also run tests autmoatically with the command . 
`>>> python manage.py test to run all the tests `

### License
The API uses an MPL-2.0, license
