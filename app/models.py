
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
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    bucket = db.relationship(
        'Bucketlist', cascade="all, delete-orphan")

    # def __init__(self, email, password):
    #     self.email = email
    #     self.password = Bcrypt().generate_password_hash(password).decode()

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = Bcrypt().generate_password_hash(
            password).decode()
        self.registered_on = datetime.datetime.now()

    def is_pw_valid(self, password):
        """
        Compares password against it's hash
        """
        return Bcrypt().check_password_hash(self.password, password)

    def encode_auth_token(self, email):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.now() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.now(),
                'sub': email
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def save(self):
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
    created_by = db.Column(db.String(255), db.ForeignKey(User.email))
    items = db.relationship("Item", backref="bucketlists", passive_deletes=True)

    def __init__(self, name):
        """initialize with name."""
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bucketlist.query.filter_by(created_by=User.email)

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
    bucketlist = db.Column(db.Integer, db.ForeignKey("bucketlists.id", ondelete="CASCADE"))

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
