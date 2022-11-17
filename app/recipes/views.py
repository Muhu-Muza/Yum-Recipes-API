from flask import Blueprint, request, jsonify
from ..extentions import  db
from ..models import Recipe, Category
from ..auth.views import token_required

recipe = Blueprint('recipe', __name__)


@recipe.route('/recipes/<id>', methods=['POST'])
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
    
@recipe.route('/recipes', methods=['GET'])
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


@recipe.route('/view-recipes/<id>', methods=['GET'])
@token_required
def get_recipes_by_categories(current_user, id):
    """ for fetching recipes available to a particular category"""
    

    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int)

    category = Category.query.filter_by(id = id).first()
    print(category)
    if category:

        recipes = Recipe.query.filter_by(
                    category = id).paginate(page = page, per_page = per_page)
        print(recipes)
        

        output = []

        for recipe in recipes.items:
            print(recipe)
            recipe_data = {}
            recipe_data['title'] = recipe.title
            recipe_data['category'] = recipe.category
            recipe_data['ingredients'] = recipe.ingredients
            recipe_data['instructions'] = recipe.instructions
            output.append(recipe_data)

        meta = {
            "page": recipes.page,
            'pages': recipes.pages,
            'total_count': recipes.total,
            'prev_page': recipes.prev_num,
            'next_page': recipes.next_num,
            'has_next': recipes.has_next,
            'has_prev': recipes.has_prev,
        }

    return jsonify({'recipes': output, 'meta': meta}), 200


@recipe.route('/recipes/<id>', methods=['GET'])
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


@recipe.route('/recipes/<id>', methods=['PUT'])
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


@recipe.route('/recipes/<id>', methods=['DELETE'])
@token_required
def delete_recipe(current_user, id):
    """Delete a particular recipe instance"""
    recipe = Recipe.query.filter_by(id=id).first()

    if not recipe:
        return jsonify({'message': 'No recipe found!'}), 404

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({'message': 'Recipe deleted!'}), 200
