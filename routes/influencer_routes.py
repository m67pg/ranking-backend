#!/usr/bin/env python3.7
from flask import Blueprint, jsonify, request, session
from database import db
from models import Influencer
from util.decorators import login_required # デコレーターをインポート
import openpyxl
from sqlalchemy import text # text をインポート
import os
import tempfile

influencer_bp = Blueprint('influencer', __name__)

@influencer_bp.route('/api/influencers/all', methods=['GET'])
def get_all_influencers_by_region():
    try:
        selected_region = request.args.get('selectedRegion', '')

        query = Influencer.query

        if selected_region:
            query = query.filter_by(region=selected_region)
        
        # Always order by followers in descending order
        query = query.order_by(Influencer.followers.desc())

        all_influencers = query.all()
        
        influencers_list = [influencer.to_dict() for influencer in all_influencers]

        response_data = {
            "items": influencers_list,
            "totalItems": len(influencers_list) # Total items is simply the count of the fetched list
        }
        response = jsonify(response_data)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch all influencers", "details": str(e)}), 500

@influencer_bp.route('/api/influencers', methods=['GET'])
@login_required
def get_influencers():
    try:
        page = request.args.get('page', 0, type=int)
        rows_per_page = request.args.get('rowsPerPage', 10, type=int)
        order_by = request.args.get('orderBy', 'popularity')
        order_direction = request.args.get('orderDirection', 'desc')
        search_term = request.args.get('searchTerm', '')
        selected_region = request.args.get('selectedRegion', '')

        query = Influencer.query

        if selected_region:
            query = query.filter_by(region=selected_region)
        
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                (Influencer.username.like(search_pattern)) |
                (Influencer.store_name.like(search_pattern)) |
                (Influencer.region.like(search_pattern))
            )

        if order_by:
            column_mapping = {
                'id': Influencer.id,
                'username': Influencer.username,
                'followers': Influencer.followers,
                'storeName': Influencer.store_name,
                'popularity': Influencer.popularity,
                'region': Influencer.region
            }
            sort_column = column_mapping.get(order_by)

            if sort_column:
                if order_direction == 'asc':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(Influencer.popularity.desc())

        total_items = query.count()
        paginated_influencers = query.offset(page * rows_per_page).limit(rows_per_page).all()
        
        influencers_list = [influencer.to_dict() for influencer in paginated_influencers]

        response_data = {
            "items": influencers_list,
            "totalItems": total_items
        }
        response = jsonify(response_data)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch influencers", "details": str(e)}), 500

@influencer_bp.route('/api/upload_influencers', methods=['POST'])
@login_required # login_required デコレータの定義は別途必要
def upload_influencers():
    if 'file' not in request.files:
        return jsonify({"error": "ファイルがアップロードされていません。"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "ファイルが選択されていません。"}), 400

    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return jsonify({"error": "Excelファイル（.xlsx または .xls）のみ受け付けます。"}), 400

    try:
        # DBセッションの開始とTRUNCATE
        # トランザクションはtry-exceptブロック全体で管理
        # SQLAlchemy 2.0.41ではtext()を明確に使用し、db.session.execute()で実行
        db.session.execute(text(f"TRUNCATE TABLE {Influencer.__tablename__}"))
        db.session.commit()
        print(f"テーブル {Influencer.__tablename__} をTRUNCATEしました。")

        # ファイルを一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel_file:
            file.stream.seek(0) # ストリームのポインタを先頭に戻す
            temp_excel_file.write(file.stream.read())
            temp_file_path = temp_excel_file.name

        # openpyxlで一時ファイルを読み込む
        workbook = openpyxl.load_workbook(temp_file_path)
        sheet = workbook.active

        header_skipped = False
        imported_count = 0
        skipped_count = 0
        errors = []

        for row_index, row in enumerate(sheet.iter_rows(min_row=1)):
            if not header_skipped:
                header_skipped = True
                continue

            try:
                username = row[0].value
                # Noneの場合は0に変換
                followers = int(row[1].value) if row[1].value is not None else 0
                store_name = row[2].value
                popularity = int(row[3].value) if row[3].value is not None else 0
                region = row[4].value

                if not username or followers is None: # followersがNoneになることは上記int()変換でなくなるが、念のため
                    errors.append(f"行 {row_index+1} ({username}): 必須フィールド (ユーザー名, フォロワー数) が不足しています。")
                    skipped_count += 1
                    continue

                new_influencer = Influencer(
                    username=username,
                    followers=followers,
                    store_name=store_name,
                    popularity=popularity,
                    region=region
                )
                db.session.add(new_influencer)
                
                imported_count += 1

            except ValueError as ve:
                errors.append(f"行 {row_index+1} ({username}): データ型変換エラー ({ve})。数値フィールドが不正です。")
                skipped_count += 1
            except IndexError:
                # このエラーは通常、row[インデックス] で範囲外にアクセスした場合に発生
                # 例えば、Excelの行にデータが全くない場合など
                errors.append(f"行 {row_index+1} ({'不明なユーザー名'}): カラム数が不足しています。Excelファイルの形式を確認してください。")
                skipped_count += 1
            except Exception as row_error:
                # 特定のユーザー名が取得できない場合を考慮
                current_username_for_error = username if 'username' in locals() else '不明なユーザー名'
                errors.append(f"行 {row_index+1} ({current_username_for_error}): 不明なエラー ({row_error})。")
                skipped_count += 1

        db.session.commit() # ループ後にまとめてコミット

        message = f"Excelファイルのインポートが完了しました。成功: {imported_count}件, スキップ: {skipped_count}件。"
        if errors:
            message += " エラー詳細: " + "; ".join(errors[:5]) + ("..." if len(errors) > 5 else "")
            return jsonify({"message": message, "errors": errors}), 200
        else:
            return jsonify({"message": message}), 200

    except Exception as e:
        db.session.rollback() # エラーが発生したらロールバック
        import traceback # 詳細なトレースバックを取得
        print(f"Excelファイル処理中に予期せぬエラーが発生しました: {traceback.format_exc()}")
        return jsonify({"error": f"サーバー側でのファイル処理中にエラーが発生しました: {e}"}), 500