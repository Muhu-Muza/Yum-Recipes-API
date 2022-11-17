from flask import Blueprint, request, jsonify
from ..extentions import db
from ..models import Category
from ..auth.views import token_required

category = Blueprint('category', __name__)



@category.route('/categories', methods=['POST'])
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


@category.route('/categories', methods=['GET'])
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


@category.route('/categories/<id>', methods=['GET'])
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


@category.route('/categories/<id>', methods=['PUT'])
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


@category.route('/categories/<id>', methods=['DELETE'])
@token_required
def delete_category(current_user, id):
    """Delete a particular category instance"""
    category = Category.query.filter_by(id=id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted!'}), 200
