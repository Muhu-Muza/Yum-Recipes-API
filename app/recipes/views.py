from flask import Blueprint, request, jsonify
from app.extentions import  db
from app.models import Recipe, Category, RecipeSchema
from app.auth.views import token_required
from marshmallow import ValidationError
from sqlalchemy import desc
from flasgger import swag_from

recipe = Blueprint('recipe', __name__)


@recipe.route('/<category_id>/recipes', methods=['POST'])
@swag_from('/app/docs/recipes/create_recipe.yml')
@token_required
def create_recipe(current_user, category_id):
    """for adding a new recipe"""
    data = request.get_json()
    recipe_schema = RecipeSchema()

    if not data:
        return jsonify({"message": "No Input data provided !"}), 400

    try:    
        data = recipe_schema.load(data)

        title = data["title"].strip().capitalize()
        ingredients = data["ingredients"].strip()
        instructions = data["instructions"].strip()

        if not title:
            return jsonify({"message": "Data required !"}), 400

        if not ingredients:
            return jsonify({"message": "Data required !"}), 400

        if not instructions:
            return jsonify({"message": "Data required !"}), 400
            
        category = Category.query.filter_by(user_id = current_user.id, id = category_id).first()
        if category:
            category = category_id
            check_recipe = Recipe.query.filter_by(title = title).first()
            if not check_recipe:
                new_recipe = Recipe(title = title, ingredients = ingredients, instructions = instructions, category = category)

                db.session.add(new_recipe)
                db.session.commit()
                result = recipe_schema.dump(Recipe.query.filter_by(title = title).first())
                return jsonify({"message": "New Recipe Created !", "Recipe": result}), 201
            
            return jsonify({'message': 'Recipe with that name already Exists!'}), 409

        return jsonify({"message": "Invalid request !"}), 400

    except ValidationError as err:
        return err.messages, 422
   

@recipe.route('/<category_id>/recipes', methods=['GET'])
@swag_from('/app/docs/recipes/get_recipes_by_category.yml')
@token_required
def get_recipes_by_categories(current_user, category_id):
    """ for fetching recipes available to a particular category"""
    
    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int)
    q = request.args.get('q', "").capitalize()

    category = Category.query.filter_by(user_id = current_user.id, id = category_id).first()

    if category:
        recipes = Recipe.query.filter_by(
                    category = category_id).order_by(desc('created_at')).paginate(page = page, per_page = per_page)

        if q:
            
            for recipe in recipes:
                if q in recipe.title:
                    recipe_schema = RecipeSchema()
                    data = recipe_schema.dump(recipe)

                    return jsonify({"recipe": data}), 200

            else:
                return jsonify({"message": "Recipe not found ! Try a different spelling !" }), 404

        recipe_schema = RecipeSchema(many = True)
        data = recipe_schema.dump(recipes)

        meta = {
            "page": recipes.page,
            'pages': recipes.pages,
            'total_count': recipes.total,
            'prev_page': recipes.prev_num,
            'next_page': recipes.next_num,
            'has_next': recipes.has_next,
            'has_prev': recipes.has_prev,
        }

        return jsonify({'recipes': data, 'meta': meta}), 200

    return jsonify({"messages": "Invalid request !"})


@recipe.route('/<category_id>/recipes/<id>', methods=['GET'])
@swag_from('/app/docs/recipes/get_particular_recipe.yml')
@token_required
def get_particular_recipe(current_user, id, category_id):
    """for getting a particular recipe"""

    category = Category.query.filter_by(user_id = current_user.id, id = category_id).first()  
    if category:
        recipe = Recipe.query.filter_by(id = id, category = category_id).first()

        if recipe:
            recipe_schema = RecipeSchema()
            data = recipe_schema.dump(recipe)
            return jsonify({"recipe": data}), 200
        
        return jsonify({'message': 'No recipe found!'}), 404
    
    return jsonify({"message":"Invalid request !"}), 400


@recipe.route('/<category_id>/recipes/<id>', methods=['PUT'])
@swag_from('/app/docs/recipes/edit_recipe.yml')
@token_required
def edit_recipe(current_user, id, category_id):
    """For updating a particular recipe"""
    category = Category.query.filter_by(user_id = current_user.id, id = category_id)  
    if category:
        recipe = Recipe.query.get(id)

        if not recipe:
            return jsonify({'message': 'No recipe found!'}), 404

        data = request.get_json()
        recipe_schema = RecipeSchema()

        try:
            data = recipe_schema.load(data)

            title = data['title'].strip().capitalize()
            ingredients = data['ingredients'].strip()
            instructions = data['instructions'].strip()

            if not title:
                return jsonify({"message": "Data required !"}), 400

            if not ingredients:
                return jsonify({"message": "Data required !"}), 400

            if not instructions:
                return jsonify({"message": "Data required !"}), 400 

            recipe.title = title
            recipe.ingredients = ingredients
            recipe.instructions = instructions

            db.session.commit()
            result = recipe_schema.dump(Recipe.query.filter_by(title = title).first())
            return jsonify({'message': 'Recipe has been Updated!', "Recipe": result}), 200

        except ValidationError as err:
            return err.messages, 422

    return jsonify({"message": "Invalid request !"}), 400


@recipe.route('/<category_id>/recipes/<id>', methods=['DELETE'])
@swag_from('/app/docs/recipes/delete_recipe.yml')
@token_required
def delete_recipe(current_user, id, category_id):
    """Delete a particular recipe instance"""
    category = Category.query.filter_by(user_id = current_user.id, id = category_id)  

    if category:
        recipe = Recipe.query.filter_by(id=id).first()

        if not recipe:
            return jsonify({'message': 'No recipe found!'}), 404

        db.session.delete(recipe)
        db.session.commit()

        return jsonify({'message': 'Recipe deleted!'}), 200

    return jsonify({"message": "Invalid request !"}), 400
