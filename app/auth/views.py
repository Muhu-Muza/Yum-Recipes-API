from flask import Blueprint, request, jsonify, make_response, current_app
from app.models import User, UserSchema
from app.extentions import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from marshmallow import ValidationError
from flasgger import swag_from
from sqlalchemy import desc


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
@swag_from('/app/docs/auth/register.yml')
def register():
    """function for registering a new user"""
    data = request.get_json()
    user_schema = UserSchema()

    if not data:
        return jsonify({"message": "No Input data provided !"}), 400
    
    username = data['username']

    hashed_password = generate_password_hash(data['password'], method='sha256')
 
    user = User.query.filter_by(username = username).first()
    if user:
        return jsonify({"message": "User with that username already exists !"}), 409
    
    try:
        data = user_schema.load(data)

        firstname = data["firstname"].strip().capitalize()
        lastname = data["lastname"].strip().capitalize()
        username = data["username"].strip()
        email = data["email"].strip()
        
        if not firstname:
            return jsonify({"message": "Data required !"}), 400

        if not lastname:
            return jsonify({"message": "Data required !"}), 400

        if not username:
            return jsonify({"message": "Data required !"}), 400

        if not email:
            return jsonify({"message": "Data required !"}), 400

        new_user = User(firstname = firstname,
                        lastname = lastname,
                        username = username,
                        email = email,
                        password = hashed_password
                        )
        db.session.add(new_user)
        db.session.commit()
        result = user_schema.dump(User.query.filter_by(username = username).first())
        return jsonify({'message': 'Account created successfully!', "User": result}), 201

    except ValidationError as err:
        return err.messages, 422


@user.route('/login', methods=['POST'])
@swag_from('/app/docs/auth/login.yml')
def login():
    """function for authenticating users and giving them access rights to restricted routes"""
    auth = request.authorization 
    if not auth or not auth.get('username') or not auth.get('password'):        
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(username = auth.get('username')).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    if check_password_hash(user.password, auth.get('password')):
        """generates the JWT token"""
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token}), 200

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})


@user.route('/users', methods=['GET'])
@swag_from('/app/docs/admin/get_all_users.yml')
@token_required
def get_all_users(current_user):
    """Get all existing users"""

    if not current_user.username == "admin":
        return jsonify({'message' : 'You are not authorised to perform that action!'}), 401

    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int)
    users = User.query.filter(User.id > 0).order_by(desc('created_at')).paginate(page = page, per_page = per_page)

    user_schema = UserSchema(many = True)
    data = user_schema.dump(users)

    meta = {
            "page": users.page,
            'pages': users.pages,
            'total_count': users.total,
            'prev_page': users.prev_num,
            'next_page': users.next_num,
            'has_next': users.has_next,
            'has_prev': users.has_prev, 
        }

    return jsonify({"users": data, "meta": meta}), 200

@user.route('/users/<id>', methods=['GET'])
@swag_from('/app/docs/admin/get_particular_user.yml')
@token_required
def get_particular_user(current_user, id):
    """Get a particular user instance"""

    if not current_user.username == "admin":
        return jsonify({'message' : 'You are not authorised to perform that action!'}), 401

    user = User.query.filter_by(id = id).first()

    if user:
        user_schema = UserSchema()
        data = user_schema.dump(user) 
        return jsonify({'user': data}), 200

    return jsonify({'message': 'No user found!'}), 404