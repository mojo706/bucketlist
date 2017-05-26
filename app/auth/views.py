
import re

from flask import request, json, jsonify, make_response
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from app import db
from app.models import User
from . import auth_blueprint

bcrypt = Bcrypt()


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        """ Method to handle POST from /bucketlist/api/v1.0/auth/register"""
        # get the post data

        post_data = request.data
        email = post_data["email"]
        password = post_data["password"]

        # check if user already exists
        user = User.query.filter_by(email="email").first()

        is_valid_email = re.match(
            '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

        if not is_valid_email:
            response = jsonify({
                "message": "Invalid Email Format!"
            })
            response.status_code = 400
            return make_response(response)

        if not user:
            # Try register a new user first
            try:
                user = User(
                    email=email,
                    password=password
                )

                # save the user
                user.save()

                response = {
                    'status': 'success',
                    'message': 'Successfully registered.'
                }
                return make_response(jsonify(response)), 201
            except Exception as e:
                # return a message with the error that occured
                response = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.',
                }

                return make_response(jsonify(response)), 401
        else:

            response = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(response)), 409


class LoginAPI(MethodView):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = request.data
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=post_data['email']
            ).first()
            if user and user.is_pw_valid(request.data["password"]):
                auth_token = user.encode_auth_token(user.email, user.id)
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                response = {
                    'status': 'fail',
                    'message': 'Wrong email or password'
                }
                return make_response(jsonify(response)), 401
        except Exception as e:
            print(e)
            response = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(response)), 500


# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/bucketlist/api/v1.0/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/bucketlist/api/v1.0/auth/login',
    view_func=login_view,
    methods=['POST']
)
