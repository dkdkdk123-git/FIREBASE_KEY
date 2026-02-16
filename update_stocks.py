import firebase_admin
from firebase_admin import credentials, db
import yfinance as yf
import os
import json
from datetime import datetime, timedelta

# --- 1. Firebase認証 ---
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    raise ValueError("FIREBASE_KEY is not set")

cred_dict = json.loads(key_json)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cross-56caf-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def calculate_cost(price, shares, month):
    # 権利付最終日を「その月の最終営業日の3日前」と仮定（簡易計算）
    today = datetime.now()
    year = today.year if today.month <= month else today.year + 1
    # その月の月末日
    if month == 12:
        last_day = datetime(year, 12, 31)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # 権利付最終日の目安（月末から3日前）
    expiry_date = last_day - timedelta(days=3)
    days_to_expiry = (expiry_date - today).days
    days_to_expiry = max(1, days_to_expiry) # 最低1日

    # 日興証券の貸株料率 (年利3.9%)
    fee_rate = 0.039
    cost = price * shares * fee_rate * (days_to_expiry / 365)
    return int(cost)

def update_stock_data():
    # 銘柄リスト：ここで権利月(month)を設定！
    stock_settings = {
        "2702": {"name": "マクドナルド", "value": 5000, "shares": 100, "month": 6},
        "9861": {"name": "吉野家HD", "value": 2000, "shares": 100, "month": 8},
        "3048": {"name": "ビックカメラ", "value": 3000, "shares": 100, "month": 8},
        "8136": {"name": "サンリオ", "value": 4000, "shares": 100, "month": 3},
    }

    updated_data = {}
    for code, info in stock_settings.items():
        try:
            ticker = yf.Ticker(f"{code}.T")
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            # コストと実質利回りを計算
            cost = calculate_cost(current_price, info["shares"], info["month"])
            net_profit = info["value"] - cost
            real_yield = (net_profit / (current_price * info["shares"])) * 100

            updated_data[code] = {
                "name": info["name"],
                "yield": round(real_yield, 2),
                "month":
