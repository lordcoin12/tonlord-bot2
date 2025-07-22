
import os
import json
import random
import time
import threading
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "users.json"
FAKE_USERS_FILE = "fake_users.json"
LAST_WINNERS_FILE = "last_winners.json"

DRAW_TIME = "12:00"
DRAW_INTERVAL = timedelta(days=1)
TICKET_PRICE_USD = 1
REWARD_POOL = 1000
ADVERTISEMENT_INTERVAL = 15 * 60

def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def get_binance_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
        return float(r.json()["price"])
    except:
        return None

def get_prices():
    ton_price = get_binance_price("TONUSDT")
    btc_price = get_binance_price("BTCUSDT")
    return ton_price, btc_price

def create_donation_text(ton, btc):
    return f"""
💰 Ödeme Bilgileri:

• USDT (Aptos): `0xa19d80c585aadf4cbc64957405b3ab6b52d85fa0356f81d1af5d2e07874ad495`
• BTC (Aptos): `0xa19d80c585aadf4cbc64957405b3ab6b52d85fa0356f81d1af5d2e07874ad495`
• TON: `UQCw6PPwak4JJxLSHynwwAiGviu5JBsRdZx4Sc8DOZj7Ncr9`

🎟 1 Bilet = 1 USDT
📈 Anlık fiyatlar:
• TON ≈ {ton:.2f} USD
• BTC ≈ {btc:.2f} USD
"""

def get_draw_time():
    now = datetime.now()
    draw_today = now.replace(hour=12, minute=0, second=0, microsecond=0)
    return draw_today if now < draw_today else draw_today + timedelta(days=1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(DATA_FILE, {})
    if user_id not in users:
        users[user_id] = {"tickets": 0, "ref": None, "username": update.effective_user.first_name}
        save_json(DATA_FILE, users)

    keyboard = [
        [InlineKeyboardButton("🎟 Bilet satın al", callback_data="buy_ticket")],
        [InlineKeyboardButton("💰 Ödeme bilgisi", callback_data="payment_info")],
        [InlineKeyboardButton("🏆 Sıralama tablosu", callback_data="leaderboard")],
        [InlineKeyboardButton("🕒 Sonraki çekiliş", callback_data="next_draw")],
        [InlineKeyboardButton("🎉 Son çekiliş sonucu", callback_data="last_winner")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎉 LordTon Botuna Hoş Geldin! Menülerden birini seç:", reply_markup=reply_markup)

if TOKEN:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
else:
    print("❌ BOT_TOKEN bulunamadı! Railway'de environment variable olarak ekleyin.")
