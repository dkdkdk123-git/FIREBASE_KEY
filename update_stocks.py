import firebase_admin
from firebase_admin import credentials, db
import json
import os
import random

# GitHubのSecretsから鍵を読み込む
key_json = os.environ.get('FIREBASE_KEY')
if key_json:
    key_dict = json.loads(key_json)
    cred = credentials.Certificate(key_dict)
else:
    # ローカル実行用（一応残しておきます）
    cred = credentials.Certificate("serviceAccountKey.json")

# Firebaseに接続（あなたのURLに書き換えてください！）
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cross-56caf-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# テストデータ：利回りをランダムに変更
new_yield = round(random.uniform(1.0, 5.0), 2)
latest_data = {
    "2702": {
        "name": "日本マクドナルド",
        "yield": new_yield,
        "nikko": "◎",
        "rakuten": "△"
    }
}

# Firebaseの stocks/0 に上書き
db.reference('stocks/0').update(latest_data)
print(f"Update Success! New Yield: {new_yield}")
