import firebase_admin
from firebase_admin import credentials, db
import yfinance as yf
import os
import json

# 1. Firebaseの認証設定
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    raise ValueError("FIREBASE_KEY is not set")

cred_dict = json.loads(key_json)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cross-56caf-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def update_stock_data():
    # 2. 銘柄の設定（ここで優待価値やコストを決める）
    # 銘柄コード: { 優待価値, クロスコスト, 必要株数, 名前 }
    stock_settings = {
        "2702": {"name": "日本マクドナルド", "value": 5000, "cost": 600, "shares": 100},
        # 他の銘柄を増やすときはここに行を追加するだけ！
    }

    updated_data = {}

    for code, info in stock_settings.items():
        try:
            # 3. Yahoo Financeから本物の株価を取得 (.Tは東証)
            ticker_symbol = f"{code}.T"
            ticker = yf.Ticker(ticker_symbol)
            
            # 最新の終値を取得
            history = ticker.history(period="1d")
            if history.empty:
                print(f"Could not find data for {ticker_symbol}")
                continue
            
            current_price = history['Close'].iloc[-1]

            # 4. 利回りの計算式
            # (優待価値 - コスト) / (株価 * 株数) * 100
            net_profit = info["value"] - info["cost"]
            investment = current_price * info["shares"]
            real_yield = (net_profit / investment) * 100

            # Firebaseに送る形に整える
            updated_data[code] = {
                "name": info["name"],
                "yield": round(real_yield, 2),  # 小数点2位まで
                "nikko": "○", # ここは後で自動化も可能
                "rakuten": "×"
            }
            print(f"{info['name']}: 株価={current_price}, 利回り={round(real_yield, 2)}%")

        except Exception as e:
            print(f"Error updating {code}: {e}")

    # 5. Firebaseの「stocks/0」を更新
    if updated_data:
        db.reference('stocks/0').update(updated_data)
        print("Successfully updated Firebase!")

if __name__ == "__main__":
    update_stock_data()
