from flask import Blueprint, request, jsonify
from app.extentions import db
from app.models import Category, CategorySchema
from app.auth.views import token_required
from marshmallow import ValidationError

category = Blueprint('category', __name__)


@category.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    """for adding a new category"""

    data = request.get_json()
    category_schema = CategorySchema()
   
    title = data['title']
    category = Category.query.filter_by(user_id = current_user.id, title = title).first()

    if category:
        return jsonify({"message": "Category already exists !"}), 409

    try:
        data = category_schema.load(data)

        user_id = current_user.id
   
        new_category = Category(title = data['title'],
                                description = data['description'],
                                user_id = user_id
                                )
        print(new_category)
        db.session.add(new_category)
        db.session.commit()

        result = category_schema.dump(new_category)
        return jsonify({'message': "Category created!", "category": result}), 201

    except ValidationError as err:
        return err.messages, 422

@category.route('/categories', methods=['GET'])
@token_required
def get_all_categories(current_user):
    """ for fetching all categories available"""
    categories = Category.query.filter_by(user_id = current_user.id).all()

    category_schema = CategorySchema(many = True)
    data = category_schema.dump(categories)
    return jsonify({"categories": data}), 200


@category.route('/categories/<id>', methods=['GET'])
@token_required
def get_particular_category(current_user, id):
    """for getting a particular category"""
    category = Category.query.filter_by(user_id = current_user.id, id=id).first()

    if category:
        category_schema = CategorySchema()
        data = category_schema.dump(category)
        return jsonify({"category": data}), 200
   
    return jsonify({'message': 'No category found!'}), 404


@category.route('/categories/<id>', methods=['PUT'])
@token_required
def edit_category(current_user, id):
    """For updating a particular category"""
    category = Category.query.filter_by(user_id = current_user.id, id = id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    data = request.get_json()
    category_schema = CategorySchema()

    try:
        data = category_schema.load(data)

        title = data["title"]
        description = data["description"]

        category.title = title
        category.description = description

        db.session.commit()
        result = category_schema.dump(category)
        return jsonify({'message': 'Category has been Updated!', "category": result}), 200

    except ValidationError as err:
        return err.messages, 422

    


@category.route('/categories/<id>', methods=['DELETE'])
@token_required
def delete_category(current_user, id):
    """Delete a particular category"""
    category = Category.query.filter_by(user_id = current_user.id, id=id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted!'}), 200
