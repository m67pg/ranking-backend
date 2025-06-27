#!/usr/local/bin/python3.7

import sys
import os
from wsgiref.handlers import CGIHandler

# ----------------------------------------------------------------------
# 環境変数の設定
# ----------------------------------------------------------------------
ROOT_PATH = os.getenv('ROOT_PATH')
sys.path.insert(0, ROOT_PATH)
VENV_PATH = ROOT_PATH + '/venv/Lib/site-packages'
if VENV_PATH not in sys.path:
    sys.path.insert(0, VENV_PATH)

FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))
if FLASK_APP_DIR not in sys.path:
    sys.path.insert(0, FLASK_APP_DIR)

# ----------------------------------------------------------------------
# Flaskアプリケーションのロードと実行
# ----------------------------------------------------------------------
try:
    # app.py から Flask アプリケーションインスタンス 'app' をロード
    from app import app as application

    # CGIHandlerでWSGIアプリケーションを実行
    CGIHandler().run(application)

except Exception as e:
    # エラー発生時のデバッグ用メッセージ
    print("Content-type: text/html\n")
    print("<html><body><h1>Application Error</h1>")
    print("<p>An error occurred:</p>")
    print("<pre>")
    import traceback
    print(traceback.format_exc())
    print("</pre></body></html>")