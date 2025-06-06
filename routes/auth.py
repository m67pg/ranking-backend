#!/usr/bin/env python3.7
from flask import Blueprint, jsonify, request, session
from models import User
from database import db
from util.decorators import login_required # デコレーターをインポート

auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/api/register', methods=['POST'])
# def register_user():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
# 
#     if not username or not password:
#         return jsonify({"error": "ユーザー名とパスワードが必要です。"}), 400
# 
#     if User.query.filter_by(username=username).first():
#         return jsonify({"error": "このユーザー名は既に存在します。"}), 409
# 
#     new_user = User(username=username)
#     new_user.set_password(password)
#     db.session.add(new_user)
#     db.session.commit()
# 
#     return jsonify({"message": "ユーザー登録が成功しました。"}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['username'] = user.username
        return jsonify({"message": "ログイン成功", "username": user.username}), 200
    else:
        return jsonify({"error": "無効なユーザー名またはパスワードです。"}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@login_required # ログアウトもログイン状態である必要はないが、セッション管理の一貫性のため適用
def logout_user():
    session.pop('username', None)
    return jsonify({"message": "ログアウトしました。"}), 200

# @auth_bp.route('/api/check_login', methods=['GET'])
# def check_login_status():
#     if 'username' in session:
#         return jsonify({"isLoggedIn": True, "username": session['username']}), 200
#     else:
#         return jsonify({"isLoggedIn": False}), 200