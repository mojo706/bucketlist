# app/__init__.py

import os

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response


# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    """ Function that wraps the creation of a new Flask object, and returns it after it's loaded up with configuration settings """
    from app.models import Bucketlist, User, Item
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/bucketlist/api/v1.0/bucketlists/', methods=['POST', 'GET'])
    def bucketlists():
        """ Function that creates a new bucketlist or retrieves all bucketlists """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_auth_token(access_token)

            if not isinstance(user_id, str):
                # user_email = User.query.filter_by(id=user_id).first()
                # user_email_details = user_email.email
                if request.method == "POST":
                    name = str(request.data.get('name', ''))

                    if name:
                        bucketlist = Bucketlist(name=name, created_by=user_id)
                        bucketlist.save()
                        response = jsonify({
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': user_id
                        })
                        response.status_code = 201
                        return make_response(response)
                    else:
                        response = jsonify({
                            "message": "Thine bucketlist must a have name"
                        })
                        response.status_code = 400
                        return make_response(response)
                else:
                    # GET
                    # Start Search Function
                    search = request.args.get("q", "")
                    if not search:
                        bucketlists = Bucketlist.get_all(user_id)
                        results = []

                        for bucketlist in bucketlists:
                            items = Item.query.filter_by(
                                bucketlist_id=bucketlist.id)
                            bucketlist_items = []
                            for item in items:
                                obj = {
                                    'id': item.id,
                                    'name': item.name,
                                    'date_created': item.date_created,
                                    'date_modified': item.date_modified
                                }
                                bucketlist_items.append(obj)
                            obj = {
                                'id': bucketlist.id,
                                'name': bucketlist.name,
                                'date_created': bucketlist.date_created,
                                'date_modified': bucketlist.date_modified,
                                'items': bucketlist_items,
                                'created_by': bucketlist.created_by
                            }
                            results.append(obj)
                        response = jsonify(results)
                        response.status_code = 200
                        return make_response(response)
                    else:
                        search_bucket = Bucketlist.query.filter_by(name=search).first()
                        if not search_bucket:
                            response = jsonify({
                                "message": "That Bucketlist Does Not Exist!"
                            })
                            response.status_code = 404
                            return make_response(response)
                        else:
                            search_item = Item.query.filter_by(bucketlist_id=search_bucket.id)
                            item_list = []
                            for item in search_item:
                                obj = {
                                    'id': item.id,
                                    'name': item.name,
                                    'date_created': item.date_created,
                                    'date_modified': item.date_modified
                                }
                                item_list.append(obj)
                            obj = {
                                'id': search_bucket.id,
                                'name': search_bucket.name,
                                'date_created': search_bucket.date_created,
                                'date_modified': search_bucket.date_modified,
                                'items': item_list,
                                'created_by': search_bucket.created_by
                            }
                            response = jsonify(obj)
                            response.status_code = 200
                            return make_response(response)
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                response = jsonify(response)
                response.status_code = 401
                return make_response(response)

    @app.route('/bucketlist/api/v1.0/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def update_bucketlist(id):
        """ Function that depending on the HTTP Request will handle deleting, updating or getting a bucketlist respectively."""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
     # retrieve a buckelist using it's ID
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if access_token:
            user_id = User.decode_auth_token(access_token)
            if not isinstance(user_id, str):
                if not bucketlist:
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == 'DELETE':
                    bucketlist.delete()
                    return {
                        "message": "bucketlist {} deleted successfully".format(bucketlist.id)
                    }, 200

                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    bucketlist.name = name
                    bucketlist.save()
                    response = jsonify({
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified
                    })
                    response.status_code = 200
                    return make_response(response)
                else:
                    # GET
                    items = Item.get_all(id)
                    bucketlist_items = []

                    for item in items:
                        obj = {
                            'id': item.id,
                            'name': item.name,
                            'date_created': item.date_created,
                            'date_modified': item.date_modified
                        }
                        bucketlist_items.append(obj)
                    obj = {
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'items': bucketlist_items,
                        'created_by': bucketlist.created_by
                    }
                response = jsonify(obj)
                response.status_code = 200
                return make_response(response)
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                response = jsonify(response)
                response.status_code = 401
                return make_response(response)

    @app.route('/bucketlist/api/v1.0/bucketlists/<int:id>/items/', methods=['POST'])
    def items(id):
        """ Method to add items to a bucketlist"""
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_auth_token(access_token)

            if not isinstance(user_id, str):

                name = str(request.data.get('name', ''))
                bucketlist = Bucketlist.query.filter(
                    Bucketlist.created_by == user_id, Bucketlist.id == id).first()
                exist_item = Item.query.filter(
                    Item.bucketlist_id == id, Item.name == name).first()

                if not bucketlist:

                    abort(404)
                if exist_item:
                    response = {
                        "message": "That item already exists"
                    }
                    response = jsonify(response)
                    response.status_code = 403
                    return make_response(response)

                if name and not exist_item:
                    item = Item(name=name, bucketlist_id=id)
                    item.save()
                    response = {
                        'id': item.id,
                        'name': item.name,
                        'date_created': item.date_created,
                        'date_modified': item.date_modified
                    }
                    response = jsonify(response)
                    response.status_code = 201
                    return make_response(response)
                else:
                    response = {
                        "message": "Item must have name"
                    }
                    response = jsonify(response)
                    response.status_code = 400
                    return make_response(response)

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                response = jsonify(response)
                response.status_code = 401
                return make_response(response)

    @app.route('/bucketlist/api/v1.0/bucketlists/<int:id>/items/<int:item_id>', methods=['PUT', 'DELETE'])
    def update_item(id, item_id):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_auth_token(access_token)
            name = str(request.data.get('name', ''))

            if not isinstance(user_id, str):
                bucketlist = Bucketlist.query.filter(
                    Bucketlist.created_by == user_id, Bucketlist.id == id).first()
                exist_item = Item.query.filter(
                    Item.bucketlist_id == id, Item.name == name).first()
                if not bucketlist:
                    abort(404)

                if not exist_item:
                    # Throw 404 if no items exist
                    abort(404)

                if request.method == "DELETE":
                    # delete the item
                    exist_item.delete()
                    return {
                        "message": "Item deleted successfully"
                    }, 200

                elif request.method == 'PUT':
                    # Get the new item name

                    if name:
                        exist_item.name = name
                        exist_item.save()

                        response = {
                            'id': exist_item.id,
                            'name': exist_item.name,
                            'date_created': exist_item.date_created,
                            'date_modified': exist_item.date_modified
                        }
                        response.status_code = 200
                        return make_response(jsonify(response))
                    else:
                        response = {
                            "message": "Item name not valid"
                        }
                        response = jsonify(response)
                        response.status_code = 400
                        return make_response(response)


            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    # Register the auth blueprint
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
