from flask import Flask
from app.extentions import db

from app.auth.views import user
from app.categories.views import category
from app.recipes.views import recipe
from flask_migrate import Migrate
from flasgger import Swagger


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    # app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/data"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "whatasecretkey"
    db.init_app(app)

    app.register_blueprint(category)
    app.register_blueprint(user)
    app.register_blueprint(recipe)

    swagger = Swagger(app,
                template={
                    "swagger": "2.0",
                    "info": {
                        "title": "Recipes API",
                        "description": """An API to keep track of food categories and recipes"""},
                        "contact": {
                            "name": "Muhumuza Ivan",
                            "email": "schumannivangmail.com",
                            "url": ""
                        },
                        "version": "1.0",
                        "basePath": "",
                        "schemes": [
                            "http",
                            "https"
                        ],
                        "securityDefinitions": {
                            "Bearer": {
                                "type": "apiKey",
                                "name": "Authorization",
                                "in": "header"
                            }
                        }
                })

    return app



app = create_app()
migrate = Migrate(app, db)
