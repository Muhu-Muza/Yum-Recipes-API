from flask import Flask, request, request, abort, current_app, jsonify, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "whatasecretkey"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='creater', cascade = 'all, delete-orphan')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), nullable=False)
    ingredients = db.Column(db.String())
    instructions = db.Column(db.String())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), unique=True, nullable=False)
    description = db.Column(db.String(200))
    recipes = db.relationship('Recipe', backref='kategory', cascade = 'all, delete-orphan')
    user = db.Column(db.Integer, db.ForeignKey('user.id'))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        token = token.split(" ")[1]

        """decoding the payload to fetch the stored details"""
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        current_user = User.query.filter_by(id=data['id']).first()

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/signup', methods=['POST'])  # sign up route
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


@app.route('/login', methods=['POST'])
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
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})


@app.route('/users', methods=['GET'])
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


@app.route('/users/<id>', methods=['GET'])
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


@app.route('/users/<id>', methods=['PUT'])
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


@app.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(id):
    """Delete a user instance"""
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'}), 200


@app.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    """for adding a new category"""
    data = request.get_json()

    new_category = Category(title=data['title'],
                            description=data['description']
                            )
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': "Category created!"}), 201


@app.route('/categories', methods=['GET'])
@token_required
def get_all_categories(current_user):
    """ for fetching all categories available"""
    categories = Category.query.all()

    output = []

    for category in categories:
        category_data = {}
        category_data['title'] = category.title
        category_data['description'] = category.description
        output.append(category_data)

    return jsonify({'categories': output}), 200


@app.route('/categories/<id>', methods=['GET'])
@token_required
def get_one_category(current_user, id):
    """for getting a particular category"""
    category = Category.query.filter_by(id=id).first()

    if category:
        category_data = {}
        category_data['title'] = category.title
        category_data['description'] = category.description

        return jsonify(category_data)

    if not category:
        return jsonify({'message': 'No category found!'}), 404


@app.route('/categories/<id>', methods=['PUT'])
@token_required
def edit_category(current_user, id):
    """For updating a particular category"""
    category = Category.query.get(id)

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    title = request.json['title']
    description = request.json['description']

    category.title = title
    category.description = description

    db.session.commit()

    return jsonify({'message': 'Category has been Updated!'}), 200


@app.route('/categories/<id>', methods=['DELETE'])
@token_required
def delete_category(current_user, id):
    """Delete a particular category instance"""
    category = Category.query.filter_by(id=id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted!'}), 200


@app.route('/recipes/<id>', methods=['POST'])
@token_required
def create_recipe(current_user, id):
    """for adding a new recipe"""
    data = request.get_json()
    title = data['title']
    instructions = data['instructions']
    ingredients = data['ingredients']

    if title and instructions and ingredients:
        category = Category.query.filter_by(id = id).first()
        if category:
            check_recipe = Recipe.query.filter_by(title = title).first()
            if not check_recipe:
                new_recipe = Recipe(
                                title = title,
                                ingredients = ingredients,
                                instructions = instructions,
                                category = id
                )

                db.session.add(new_recipe)
                db.session.commit()

                return jsonify({'message': 'Recipe created!'}), 201

            return jsonify({'message': 'Recipe with that name already Exists!'}), 409
        return jsonify({'message': 'Invalid request'}), 404
    
@app.route('/recipes', methods=['GET'])
@token_required
def get_all_recipes(current_user):
    """ for fetching all recipes available"""
    recipes = Recipe.query.all()

    output = []

    for recipe in recipes:
        recipe_data = {}
        recipe_data['title'] = recipe.title
        recipe_data['category'] = recipe.category
        recipe_data['ingredients'] = recipe.ingredients
        recipe_data['instructions'] = recipe.instructions
        output.append(recipe_data)

    return jsonify({'recipes': output}), 200


@app.route('/recipes/<id>', methods=['GET'])
@token_required
def get_one_recipe(current_user, id):
    """for getting a particular recipe"""
    recipe = Recipe.query.filter_by(id=id).first()

    if recipe:
        recipe_data = {}
        recipe_data['title'] = recipe.title
        recipe_data['category'] = recipe.category
        recipe_data['ingredients'] = recipe.ingredients
        recipe_data['instructions'] = recipe.instructions

        return jsonify(recipe_data), 200

    if not recipe:
        return jsonify({'message': 'No recipe found!'}), 404


@app.route('/recipes/<id>', methods=['PUT'])
@token_required
def edit_recipe(current_user, id):
    """For updating a particular recipe"""
    recipe = Recipe.query.get(id)

    if not recipe:
        return jsonify({'message': 'No recipe found!'}), 404

    title = request.json['title']
    category = request.json['category']
    ingredients = request.json['ingredients']
    instructions = request.json['instructions']

    recipe.title = title
    recipe.category = category
    recipe.ingredients = ingredients
    recipe.instructions = instructions

    db.session.commit()

    return jsonify({'message': 'Recipe has been Updated!'}), 200


@app.route('/recipes/<id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, id):
    """Delete a particular recipe instance"""
    recipe = Recipe.query.filter_by(id=id).first()

    if not recipe:
        return jsonify({'message': 'No recipe found!'}), 404

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({'message': 'Recipe deleted!'}), 200


if __name__ == '__main__':
    app.run()
