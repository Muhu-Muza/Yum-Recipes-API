from flask import Blueprint, request, jsonify, make_response, current_app
from ..models import User
from ..extentions import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


user = Blueprint('user', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        token = token.split(" ")[1]

        """decoding the payload to fetch the stored details"""
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
        current_user = User.query.filter_by(id=data['id']).first()

        return f(current_user, *args, **kwargs)

    return decorated


@user.route('/signup', methods=['POST'])  # sign up route
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(firstname=data['firstname'],
                    lastname=data['lastname'],
                    username=data['username'],
                    email=data['email'],
                    password=hashed_password
                    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created successfully!'}), 201


@user.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(username=auth.get('username')).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    if check_password_hash(user.password, auth.get('password')):
        """generates the JWT token"""
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})


@user.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    """Get all existing users"""
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['firstname'] = user.firstname
        user_data['lastname'] = user.lastname
        user_data['username'] = user.username
        user_data['email'] = user.email
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users': output}), 200


@user.route('/users/<id>', methods=['GET'])
@token_required
def get_one_user(current_user, id):
    """Get a particular user instance"""

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    user_data = {}
    user_data['firstname'] = user.firstname
    user_data['lastname'] = user.lastname
    user_data['username'] = user.username
    user_data['email'] = user.email
    user_data['password'] = user.password

    return jsonify({'user': user_data}), 200


@user.route('/users/<id>', methods=['PUT'])
@token_required
def edit_user(current_user, id):
    """Update user profile"""

    user = User.query.get(id)

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    firstname = request.json['firstname']
    lastname = request.json['lastname']
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    user.firstname = firstname
    user.lastname = lastname
    user.username = username
    user.email = email
    user.password = password

    db.session.commit()

    return jsonify({'message': 'User profile has been Updated!'}), 200


@user.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(id):
    """Delete a user instance"""
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'}), 200