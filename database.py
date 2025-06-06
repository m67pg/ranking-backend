#!/usr/bin/env python3.7
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all() # アプリケーションコンテキスト内でテーブルを作成