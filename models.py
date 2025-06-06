#!/usr/bin/env python3.7
from database import db # database.py から db インスタンスをインポート
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    store_name = db.Column(db.String(255))
    popularity = db.Column(db.Integer)
    region = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": self.followers,
            "storeName": self.store_name,
            "popularity": self.popularity,
            "region": self.region
        }