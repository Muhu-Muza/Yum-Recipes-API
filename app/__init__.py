from flask import Flask
from .extentions import db

from .auth.views import user
from .categories.views import category
from .recipes.views import recipe
from flask_migrate import Migrate


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

    return app



app = create_app()
migrate = Migrate(app, db)
