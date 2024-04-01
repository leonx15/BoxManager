from . import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('boxes', lazy=True))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    ean_code = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    box = db.relationship('Box', backref=db.backref('items', lazy=True))
