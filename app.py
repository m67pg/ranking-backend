#!/usr/bin/env python3.7
from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.influencer_routes import influencer_bp

app = Flask(__name__)

# アプリケーション設定をロード
app.config.from_object(Config)

# CORS設定
CORS(app, origins=["https://ranking.cspm.fun", "https://ranking-zeta.vercel.app"], supports_credentials=True)

# データベースの初期化
init_db(app)

# Blueprintを登録
app.register_blueprint(auth_bp)
app.register_blueprint(influencer_bp)

if __name__ == '__main__':
    # 開発環境でのみデバッグモードを有効にする
    app.run(debug=True, port=5000)