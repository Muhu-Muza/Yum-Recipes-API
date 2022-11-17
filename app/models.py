import datetime
from .extentions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='creater', cascade = 'all, delete-orphan')
    # created_at = db.Column(db.DateTime, default=datetime.now())
    # updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), nullable=False)
    ingredients = db.Column(db.String())
    instructions = db.Column(db.String())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    # created_at = db.Column(db.DateTime, default=datetime.now())
    # updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), unique=True, nullable=False)
    description = db.Column(db.String(200))
    recipes = db.relationship('Recipe', backref='kategory', cascade = 'all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # created_at = db.Column(db.DateTime, default=datetime.now())
    # updated_at = db.Column(db.DateTime, onupdate=datetime.now())
