
import os
import datetime
import jwt
from flask import current_app
from flask_bcrypt import Bcrypt
from app import db, create_app
from sqlalchemy.schema import ForeignKey

# app = create_app(config_name=os.getenv('FLASK_CONFIG'))
# bcrypt = Bcrypt(app)


class User(db.Model):
    """This class represents the user table."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    bucket = db.relationship(
        'Bucketlist', cascade="all, delete-orphan")

    # def __init__(self, email, password):
    #     self.email = email
    #     self.password = Bcrypt().generate_password_hash(password).decode()

    def __init__(self, email, password):
        self.email = email
        self.password = Bcrypt().generate_password_hash(
            password).decode()
        self.registered_on = datetime.datetime.now()

    def is_pw_valid(self, password):
        """
        Compares password against it's hash
        """
        return Bcrypt().check_password_hash(self.password, password)

    # def encode_auth_token(self, user_id):
    #     """
    #     Generates the Auth Token
    #     :return: string
    #     """
    #     try:
    #         # payload = {
    #         #     'exp': datetime.datetime.now() + datetime.timedelta(days=0, minutes=20),
    #         #     'iat': datetime.datetime.now(),
    #         #     'sub': user_id
    #         # }
    #         # jwt_token = jwt.encode(
    #         #     payload,
    #         #     current_app.config.get('SECRET'),
    #         #     'utf-8',
    #         #     algorithm='HS256',
    #         # )

    #         return jwt_token.decode('utf-8')

    #     except Exception as e:
    #         # return an error in string format if an exception occurs
    #         return e
    def encode_auth_token(self, issuer, sub):
        """
        Generates the Auth Token
        :return: string
        """
        payload = {
            "iss": issuer,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(
                days=0, seconds=60 * 60),
            "iat": datetime.datetime.utcnow(),
            "sub": sub,
        }
        auth_token = jwt.encode(
            payload,
            current_app.config.get('SECRET'),
            algorithm='HS256'
        )
        return auth_token

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            # Try and decode auth token using our SECRET Key
            payload = jwt.decode(auth_token, current_app.config.get('SECRET'))
            if payload:
                return payload['sub']
            else:
                return "Forbidden, you cannot access that resource", 403
        except jwt.ExpiredSignatureError:
            # return an error when the token expires
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            # return an error when the token is invalid
            return 'Invalid token. Please log in again.'

    def save(self):
        """ Method to save to db"""
        db.session.add(self)
        db.session.commit()


class Bucketlist(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    items = db.relationship(
        "Item", backref="bucketlists", passive_deletes=True)

    def __init__(self, name, created_by):
        """initialize with name."""
        self.name = name
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        return Bucketlist.query.filter_by(created_by=user_id).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # def __repr__(self):
    #     return "<Bucketlist: {}>".format(self.name)

class Item(db.Model):
    """This class represents the items table."""

    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean)

    def __init__(self, name, bucketlist_id):
        """initialize with name."""
        self.name = name
        self.bucketlist_id = bucketlist_id

    @staticmethod
    def get_all(bucketlist_id):
        return Item.query.filter_by(bucketlist_id=bucketlist_id).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
