from flask import Blueprint, request, jsonify
from app.extentions import  db
from app.models import Recipe, Category, RecipeSchema
from app.auth.views import token_required
from marshmallow import ValidationError

recipe = Blueprint('recipe', __name__)


@recipe.route('/recipes/<id>', methods=['POST'])
@token_required
def create_recipe(current_user, id):
    """for adding a new recipe"""
    data = request.get_json()
    recipe_schema = RecipeSchema()

    if not data:
        return {"message": "No Input data provided !"}, 400

    try:    
        data = recipe_schema.load(data)
  
        category = Category.query.filter_by(id = id).first()
        if category:
            title = data["title"]
            ingredients = data["ingredients"]
            instructions = data["instructions"]
            category = id

            check_recipe = Recipe.query.filter_by(title = title).first()
            if not check_recipe:
                new_recipe = Recipe(title = title, ingredients = ingredients, instructions = instructions, category = category)

                db.session.add(new_recipe)
                db.session.commit()
                result = recipe_schema.dump(Recipe.query.filter_by(title = title).first())
                return jsonify({"message": "New Recipe Created !", "Recipe": result}), 201
            
            return jsonify({'message': 'Recipe with that name already Exists!'}), 409

    except ValidationError as err:
        return err.messages, 422

    
@recipe.route('/recipes', methods=['GET'])
@token_required
def get_all_recipes(current_user):
    """ for fetching all recipes available"""
    recipes = Recipe.query.all()

    recipe_schema = RecipeSchema(many = True)
    data = recipe_schema.dump(recipes)
    return jsonify({"recipes": data}), 200
   

@recipe.route('/view-recipes/<id>', methods=['GET'])
@token_required
def get_recipes_by_categories(current_user, id):
    """ for fetching recipes available to a particular category"""
    
    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int)

    category = Category.query.filter_by(id = id).first()
    if category:

        recipes = Recipe.query.filter_by(
                    category = id).paginate(page = page, per_page = per_page)
        
        output = []

        for recipe in recipes.items:
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
def get_particular_recipe(current_user, id):
    """for getting a particular recipe"""
    recipe = Recipe.query.filter_by(id=id).first()

    if recipe:
        recipe_schema = RecipeSchema()
        data = recipe_schema.dump(recipe)
        return jsonify({"recipe": data}), 200
    
    return jsonify({'message': 'No recipe found!'}), 404


@recipe.route('/recipes/<id>', methods=['PUT'])
@token_required
def edit_recipe(current_user, id):
    """For updating a particular recipe"""
    recipe = Recipe.query.get(id)

    if not recipe:
        return jsonify({'message': 'No recipe found!'}), 404

    data = request.get_json()
    recipe_schema = RecipeSchema()

    try:
        data = recipe_schema.load(data)

        title = data['title']
        category = data['category']
        ingredients = data['ingredients']
        instructions = data['instructions']

        recipe.title = title
        recipe.category = category
        recipe.ingredients = ingredients
        recipe.instructions = instructions

        db.session.commit()
        result = recipe_schema.dump(Recipe.query.filter_by(title = title).first())
        return jsonify({'message': 'Recipe has been Updated!', "Recipe": result}), 200

    except ValidationError as err:
        return err.messages, 422


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
