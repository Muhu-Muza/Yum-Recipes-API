from datetime import datetime
from app.extentions import db
from marshmallow import Schema, fields, validate

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='creater', cascade = 'all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), nullable=False, unique=True)
    ingredients = db.Column(db.String())
    instructions = db.Column(db.String())
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self):
        return f"< {self.title}, {self.category} >"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(80), unique=True, nullable=False)
    description = db.Column(db.String(200))
    recipes = db.relationship('Recipe', backref='kategory', cascade = 'all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self):
        return f"< {self.title} >"

class UserSchema(Schema):
    id = fields.Int(dump_only = True)
    firstname = fields.Str(required = True, validate = validate.Length(min=3))
    lastname = fields.Str(required = True, validate = validate.Length(min=3))
    username = fields.Str(required = True, validate = validate.Length(min=4))
    email = fields.Email(required = True, validate = validate.Email())
    password = fields.Str(required = True, validate = validate.Length(min=5))

class CategorySchema(Schema):
    id = fields.Int(dump_only = True)
    title = fields.Str(required = True, unique = True, validate = validate.Length(min=4))
    description = fields.Str(required = True, validate = validate.Length(min=5))
    user_id = fields.Int(dump_only = True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
class RecipeSchema(Schema):
    id = fields.Int(dump_only = True)
    title = fields.Str(required = True, unique = True, validate = validate.Length(min=3))
    ingredients = fields.Str(required = True, validate = validate.Length(min=4))
    instructions = fields.Str(required = True, validate = validate.Length(min=4))
    category = fields.Int(dump_only = True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


