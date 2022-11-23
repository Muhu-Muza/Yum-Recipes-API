from flask import Blueprint, request, jsonify, make_response, current_app
from app.models import User, UserSchema
from app.extentions import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from marshmallow import ValidationError


user = Blueprint('user', __name__)


def token_required(f):
    """A decorator function that enforces authorisation for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        token = token.split(" ")[1]

        try:
            """decoding the payload to fetch the stored details"""
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({"message": "Token is invalid or expired !"}), 401
            
        return f(current_user, *args, **kwargs)

    return decorated


@user.route('/signup', methods=['POST'])  # sign up route
def register():
    """function for registering a new user"""
    data = request.get_json()
    user_schema = UserSchema()

    if not data:
        return jsonify({"message": "No Input data provided !"})
    
    username = data['username']

    hashed_password = generate_password_hash(data['password'], method='sha256')
 
    user = User.query.filter_by(username = username).first()
    if user:
        return jsonify({"message": "User with that username already exists !"}), 409
    
    try:
        data = user_schema.load(data)
        
        new_user = User(firstname = data['firstname'],
                        lastname = data['lastname'],
                        username = data['username'],
                        email = data['email'],
                        password = hashed_password
                        )
        db.session.add(new_user)
        db.session.commit()
        result = user_schema.dump(User.query.filter_by(username = username).first())
        return jsonify({'message': 'Account created successfully!', "User": result}), 201

    except ValidationError as err:
        return err.messages, 422


@user.route('/login', methods=['POST'])
def login():
    """function for authenticating users and giving them access rights to restricted routes"""
    auth = request.authorization #   assign data from the Authorization header in parsed form to the variable auth
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
    user_schema = UserSchema(many = True)

    data = user_schema.dump(users)
    return jsonify({'users': data}), 200


@user.route('/users/<id>', methods=['GET'])
@token_required
def get_particular_user(current_user, id):
    """Get a particular user instance"""

    user = User.query.filter_by(id=id).first()

    if user:
        user_schema = UserSchema()
        data = user_schema.dump(user) 
        return jsonify({'user': data}), 200

    return jsonify({'message': 'No user found!'}), 404

@user.route('/users/<id>', methods=['PUT'])
@token_required
def edit_user(current_user, id):
    """Update user profile"""

    user = User.query.get(id)

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    data = request.get_json()
    user_schema = UserSchema()

    try:
        data = user_schema.load(data)

        firstname = data['firstname']
        lastname = data['lastname']
        username = data['username']
        email = data['email']
        password = data['password']

        user.firstname = firstname
        user.lastname = lastname
        user.username = username
        user.email = email
        user.password = password

        db.session.commit()
        result = user_schema.dump(User.query.filter_by(id = id).first())
        return jsonify({'message': 'User profile has been Updated!', "User": result}), 200
    
    except ValidationError as err:
        return err.messages, 422

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