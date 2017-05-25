""" File that contains tests for the Bucketlist API """

import unittest
import os
import json

from app import create_app, db
from flask import current_app
from flask_testing import TestCase
from app.models import User, Bucketlist
from app.auth.views import RegisterAPI, LoginAPI


class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Hike Mount Everest'}
        user_data = {
            'email': 'testuser@test.com',
            'password': 'testpassword1'
        }
        self.client().post('/bucketlist/api/v1.0/auth/register', data=user_data)
        res = self.client().post('/bucketlist/api/v1.0/auth/login', data=user_data)
        auth_token = json.loads(res.data.decode('utf-8'))['auth_token']
        self.headers = dict(Authorization="Bearer " + auth_token)

        # binds the app to the current context
        self.app_context = self.app.app_context()
        self.app_context.push()
        # close old sessions and create all tables
        db.session.close()
        db.drop_all()
        db.create_all()

    def register_test_user(self, email="testuser@test.com", password="testpassword1"):
        """ Method to register a test user """
        user_data = {
            'email': email,
            'password': password
        }
        user = User(email=email, password=password)
        user.save()

        return self.client().post('/bucketlist/api/v1.0/auth/register', data=user_data)

    def login_test_user(self, email="testuser@test.com", password="testpassword1"):
        """ Method to login the test user """
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/bucketlist/api/v1.0/auth/login', data=user_data)

        # Bucketlist tests
    def test_api_can_create_bucketlist(self):
        """Test API can create a bucketlist (POST request)"""

        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)
        res = self.client().post('/bucketlist/api/v1.0/bucketlists/',
                                 headers=this_header, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Hike Mount Everest', str(res.data))

    def test_api_can_retrieve_all_bucketlists(self):
        """ Test API can get a bucketlist (GET request)."""

        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)

        res = self.client().post('/bucketlist/api/v1.0/bucketlists/',
                                 headers=this_header, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().get('/bucketlist/api/v1.0/bucketlists/',
                                 headers=this_header)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hike Mount Everest', str(res.data))

    def test_api_can_retrieve_a_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""

        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)
        res = self.client().post('/bucketlist/api/v1.0/bucketlists/',
                                 headers=this_header, data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(
            res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/bucketlist/api/v1.0/bucketlists/{}'.format(result_in_json['id']), headers=this_header)
        self.assertEqual(result.status_code, 200)
        self.assertIn('Hike Mount Everest', str(result.data))

    def test_api_can_edit_bucketlist(self):
        """Test API can edit an existing bucketlist. (PUT request)"""

        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)
        res = self.client().post('/bucketlist/api/v1.0/bucketlists/',
                                 headers=this_header, data={'name': 'Go bungee jumping'})
        self.assertEqual(res.status_code, 201)
        res = self.client().put('/bucketlist/api/v1.0/bucketlists/1',
                                headers=this_header, data={"name": "Go paragliding in Panama"})
        self.assertEqual(res.status_code, 200)
        results = self.client().get('/bucketlist/api/v1.0/bucketlists/1', headers=this_header)
        self.assertIn('Go paragliding', str(results.data))

    def test_api_can_delete_bucketlist(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""

        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)
        res = self.client().post('/bucketlist/api/v1.0/bucketlists/',
                                 headers=self.headers, data={'name': 'Go bungee jumping'})
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/bucketlist/api/v1.0/bucketlists/1', headers=this_header)
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/bucketlist/api/v1.0/bucketlists/1', headers=this_header)
        self.assertEqual(result.status_code, 404)

    # Bucketlist item tests
    def test_api_can_create_bucketlist_item(self):
        """ Test API can add an item to a bucketlist"""
        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)

        # Create a bucketlist
        response = self.client().post(
            '/bucketlist/api/v1.0/bucketlists/',
            headers=this_header,
            data={'name': 'Go bungee jumping'})
        self.assertEqual(response.status_code, 201)

        results = json.loads(response.data.decode())

        # add item to the created bucketlist
        item = {'name': 'Go bungee jumping in Nakuru'}
        res = self.client().post(
            '/bucketlist/api/v1.0/bucketlists/{}/items/'.format(results['id']),
            headers=this_header, data=item)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go bungee jumping', str(res.data))

    def test_api_can_delete_bucketlist_item(self):
        """ Test API can delete a bucketlist item by ID"""
        self.register_test_user()
        response = self.login_test_user()
        auth_token = json.loads(response.data.decode('utf-8'))['auth_token']
        this_header = dict(Authorization="Bearer " + auth_token)

        # Create a bucketlist
        bucket = self.client().post(
            '/bucketlist/api/v1.0/bucketlists/',
            headers=this_header,
            data={'name': 'Go paragliding'})
        self.assertEqual(bucket.status_code, 201)

        results = json.loads(bucket.data.decode())
        print(results["id"])
        # add item to the created bucketlist
        bucket_item = {'name': 'Go paragliding in Peru'}
        res = self.client().post(
            '/bucketlist/api/v1.0/bucketlists/{}/items/'.format(results['id']),
            headers=this_header, data=bucket_item)
        self.assertEqual(res.status_code, 201)
        item_id = json.loads(res.data.decode())['id']
        print(item_id)
        response = self.client().delete('/bucketlist/api/v1.0/bucketlists/{}/items/{}'.format(
            results['id'], item_id), headers=this_header)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_app_is_development(self):
        """ Test API can set different config for development of the app"""
        self.assertTrue(self.app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            self.app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/bucketlist_api"
        )

    # User Tests
    def test_api_can_register_user(self):
        """ Test for user registration """

        response = self.client().post(
            '/bucketlist/api/v1.0/auth/register',
            data=json.dumps(dict(
                email='joe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully registered.')
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 201)

    def test_already_registered_user(self):
        """ Test registration with already registered email"""
        user = User(
            email='joe@gmail.com',
            password='test'
        )
        user.save()
        # with self.client:
        response = self.client().post(
            '/bucketlist/api/v1.0/auth/register',
            data=json.dumps(dict(
                email='joe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(
            data['message'] == 'User already exists. Please Log in.')
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 202)

    def test_registered_user_login(self):
        """ Test for login of registered-user login """

        response = self.client().post(
            '/bucketlist/api/v1.0/auth/register',
            data=json.dumps(dict(
                email='joe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(
            data['message'] == 'Successfully registered.'
        )
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 201)
        # registered user login
        response = self.client().post(
            '/bucketlist/api/v1.0/auth/login',
            data=json.dumps(dict(
                email='joe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged in.')
        self.assertTrue(data['auth_token'])
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_non_registered_user_cannot_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        fake_user = {
            'email': 'fakeuser@test.com',
            'password': 'sina'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('bucketlist/api/v1.0/auth/login', data=fake_user)
        result = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Wrong email or password")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
