""" File that contains tests for the Bucketlist API """

import unittest
import os
import json

from app import create_app, db
from flask import current_app
from flask_testing import TestCase
from app.models import User, Bucketlist
from app.auth.views import RegisterAPI, UserAPI


class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go to Borabora for vacation'}

        # binds the app to the current context
        self.app_context = self.app.app_context()
        self.app_context.push()
            # close old sessions and create all tables
        db.session.close()
        db.drop_all()
        db.create_all()

    def test_api_can_create_bucketlist(self):
        """Test API can create a bucketlist (POST request)"""
        res = self.client().post('/api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_retrieve_all_bucketlists(self):
        """ Test API can get a bucketlist (GET request)."""
        res = self.client().post('/api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        resp = self.client().get('/api/v1.0/bucketlists/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Go to Borabora for vacation', str(res.data))

    def test_api_can_retrieve_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        res = self.client().post('/api/v1.0/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(
            res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1.0/bucketlists/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Borabora', str(result.data))

    def test_a_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        res = self.client().post(
            '/api/v1.0/bucketlists/',
            data={'name': 'Eat, pray and love'})
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/api/v1.0/bucketlists/1',
            data={
                "name": "Dont just eat, but also pray and love :-)"
            })
        self.assertEqual(res.status_code, 200)
        results = self.client().get('/api/v1.0/bucketlists/1')
        self.assertIn('Dont just eat', str(results.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        res = self.client().post(
            '/api/v1.0/bucketlists/',
            data={'name': 'Eat, pray and love'})
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/api/v1.0/bucketlists/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/api/v1.0/bucketlists/1')
        self.assertEqual(result.status_code, 404)

    def test_app_is_development(self):
        """ Test API can set different config for development of the app"""
        self.assertTrue(self.app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            self.app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/bucketlist_api"
        )

    def test_app_is_testing(self):
        """ Test API can set different config for testing the app"""
        self.assertTrue(self.app.config['DEBUG'])
        self.assertTrue(
            self.app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/test_api"
        )

    def test_encode_auth_token(self):
        """ Test API can create an auth token"""
        with self.client:
            user = User(
                email='test@test.com',
                password='test'
            )
            user.save()

            auth_token = user.encode_auth_token(user.id)
            self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """ Test API can decode the auth token"""
        user = User(
            email='test@test.com',
            password='test'
        )
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token) == 1)

    def test_api_can_register_user(self):
        """ Test for user registration """

        response = self.client().post(
            '/api/v1.0/auth/register',
            data=json.dumps(dict(
                email='joe@gmail.com',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully registered.')
        self.assertTrue(data['auth_token'])
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        user = User(
            email='joe@gmail.com',
            password='test'
        )
        user.save()
        # with self.client:
        response = self.client().post(
            '/api/v1.0/auth/register',
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
        with self.client:
            # user registration
            resp_register = self.client.post(
                '/api/v1.0/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json',
            )
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # registered user login
            response = self.client.post(
                '/api/v1.0/auth/login',
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

    # def tearDown(self):
    #     """teardown all initialized variables."""
    #     with self.app.app_context():
    #         # drop all tables
    #         db.session.remove()
    #         db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
