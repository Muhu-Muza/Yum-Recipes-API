from flask import Blueprint, request, jsonify
from app.extentions import db
from app.models import Category, CategorySchema
from app.auth.views import token_required
from marshmallow import ValidationError
from sqlalchemy import desc
from flasgger import swag_from

category = Blueprint('category', __name__)


@category.route('/categories', methods=['POST'])
@swag_from('/app/docs/categories/create_category.yml')
@token_required
def create_category(current_user):
    """for adding a new category"""

    data = request.get_json()
    category_schema = CategorySchema()
   
    if not data:
        return jsonify({"message": "No Input data provided !"}), 400

    title = data['title']
    category = Category.query.filter_by(user_id = current_user.id, title = title).first()

    if category:
        return jsonify({"message": "Category with that name already exists !"}), 409

    try:
        data = category_schema.load(data)

        title = data["title"].strip().capitalize()
        description = data["description"].strip()
        user_id = current_user.id

        if not title:
            return jsonify({"message": "Data required !"}), 400

        if not description:
            return jsonify({"message": "Data required !"}), 400
   
        new_category = Category(title = title,
                                description = description,
                                user_id = user_id
                                )
        db.session.add(new_category)
        db.session.commit()

        result = category_schema.dump(new_category)
        return jsonify({'message': "Category created successfully !", "category": result}), 201

    except ValidationError as err:
        return err.messages, 422

@category.route('/categories', methods=['GET'])
@swag_from('/app/docs/categories/get_all_categories.yml')
@token_required
def get_all_categories(current_user):
    """ for fetching all categories available"""

    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int)
    q = request.args.get('q', "").capitalize()
    categories = Category.query.filter_by(user_id = current_user.id).order_by(desc('created_at')).paginate(page = page, per_page = per_page)
    
    if q:
        for category in categories:
            if q in category.title:

                category_schema = CategorySchema()
                data = category_schema.dump(category)

                return jsonify({"category": data}), 200

        else:
            return jsonify({"message": "Category not found ! Try a different spelling !"}), 404

 
    category_schema = CategorySchema(many = True)
    data = category_schema.dump(categories)

    meta = {
            "page": categories.page,
            'pages': categories.pages,
            'total_count': categories.total,
            'prev_page': categories.prev_num,
            'next_page': categories.next_num,
            'has_next': categories.has_next,
            'has_prev': categories.has_prev
        }

    return jsonify({"categories": data, "meta": meta}), 200

@category.route('/categories/<id>', methods=['GET'])
@swag_from('/app/docs/categories/get_particular_category.yml')
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
@swag_from('/app/docs/categories/edit_category.yml')
@token_required
def edit_category(current_user, id):
    """For updating a particular category"""
    category = Category.query.filter_by(user_id = current_user.id, id = id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    data = request.get_json()
    category_schema = CategorySchema()

    if not data:
        return jsonify({"message": "No Input data provided !"}), 400

    try:
        data = category_schema.load(data)

        title = data["title"].strip().capitalize()
        description = data["description"].strip()

        if not title:
            return jsonify({"message": "Data required !"}), 400

        if not description:
            return jsonify({"message": "Data required !"}), 400

        category.title = title
        category.description = description

        db.session.commit()
        result = category_schema.dump(category)
        return jsonify({'message': 'Category has been Updated!', "category": result}), 200

    except ValidationError as err:
        return err.messages, 422

    


@category.route('/categories/<id>', methods=['DELETE'])
@swag_from('/app/docs/categories/delete_category.yml')
@token_required
def delete_category(current_user, id):
    """Delete a particular category"""
    category = Category.query.filter_by(user_id = current_user.id, id=id).first()

    if not category:
        return jsonify({'message': 'No category found!'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted!'}), 200
