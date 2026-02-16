import firebase_admin
from firebase_admin import credentials, db
import json
import os
import random

# GitHubの「Secrets」に保存した FIREBASE_KEY を読み込む
firebase_key_raw = os.environ.get('FIREBASE_KEY')

if firebase_key_raw:
    # 金庫（Secrets）から鍵を取り出す
    try:
        key_dict = json.loads(firebase_key_raw)
        cred = credentials.Certificate(key_dict)
    except Exception as e:
        print(f"JSONの読み込みに失敗しました: {e}")
        raise
else:
    # もし金庫になければ、直接ファイルを探す（ローカル実行用）
    cred = credentials.Certificate("serviceAccountKey.json")

# Firebaseに接続（あなたのURL）
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cross-56caf-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# テストデータ更新：マクドナルドの利回りをランダムに変更
new_yield = round(random.uniform(1.0, 5.0), 2)
latest_data = {
    "2702": {
        "name": "日本マクドナルド",
        "yield": new_yield,
        "nikko": "◎",
        "rakuten": "△"
    }
}

db.reference('stocks/0').update(latest_data)
print(f"成功！新しい利回り: {new_yield}")
