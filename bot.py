import asyncio
import os
import requests
from datetime import datetime
from telegram import Bot

# توکن از متغیر محیطی خوانده می‌شود
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003246659367

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN تنظیم نشده است!")

async def get_tgju_data():
    try:
        r = requests.get("https://call5.tgju.org/ajax.json", timeout=15)
        return r.json()["current"]
    except Exception as e:
        print("خطا در دریافت داده tgju:", e)
        return None

async def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,tether,binancecoin,solana,ripple,cardano,dogecoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        r = requests.get(url, params=params, timeout=15)
        return r.json()
    except Exception as e:
        print("خطا در دریافت کریپتو:", e)
        return None

def format_price(price_str):
    try:
        price = int(str(price_str).replace(",", ""))
        toman = price // 10
        return f"{toman:,}"
    except:
        return str(price_str)

def get_change_emoji(change_type, percent):
    if change_type == "high":
        return f"🟢 +{percent}%"
    elif change_type == "low":
        return f"🔴 {percent}%"
    else:
        return "➖ ۰٪"

async def create_message():
    data = await get_tgju_data()
    crypto = await get_crypto_prices()

    if not data:
        return "⚠️ خطا در دریافت قیمت‌ها."

    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    msg = f"""📊 **قیمت لحظه‌ای بازار**
🕐 {now}

💵 **ارز آزاد**
• دلار: {format_price(data['price_dollar_rl']['p'])} تومان {get_change_emoji(data['price_dollar_rl']['dt'], data['price_dollar_rl']['dp'])}
• یورو: {format_price(data['price_eur']['p'])} تومان {get_change_emoji(data['price_eur']['dt'], data['price_eur']['dp'])}
• درهم: {format_price(data['price_aed']['p'])} تومان {get_change_emoji(data['price_aed']['dt'], data['price_aed']['dp'])}
• لیر ترکیه: {format_price(data['price_try']['p'])} تومان {get_change_emoji(data['price_try']['dt'], data['price_try']['dp'])}
• دینار کویت: {format_price(data['price_kwd']['p'])} تومان {get_change_emoji(data['price_kwd']['dt'], data['price_kwd']['dp'])}

🥇 **طلا و سکه**
• طلای ۱۸ عیار: {format_price(data['geram18']['p'])} تومان {get_change_emoji(data['geram18']['dt'], data['geram18']['dp'])}
• سکه امامی: {format_price(data['sekee']['p'])} تومان {get_change_emoji(data['sekee']['dt'], data['sekee']['dp'])}
• سکه بهار آزادی: {format_price(data['sekeb']['p'])} تومان {get_change_emoji(data['sekeb']['dt'], data['sekeb']['dp'])}
"""

    if crypto:
        msg += "\n🪙 **ارز دیجیتال (دلار)**\n"
        coins = {
            "bitcoin": "بیت‌کوین",
            "ethereum": "اتریوم",
            "tether": "تتر",
            "binancecoin": "بایننس‌کوین",
            "solana": "سولانا",
            "ripple": "ریپل",
            "cardano": "کاردانو",
            "dogecoin": "دوج‌کوین"
        }
        for coin_id, name in coins.items():
            if coin_id in crypto:
                price = crypto[coin_id]["usd"]
                change = crypto[coin_id].get("usd_24h_change", 0)
                emoji = "🟢" if change >= 0 else "🔴"
                msg += f"• {name}: ${price:,.2f}  {emoji} {change:.2f}%\n"

    msg += "\n#قیمت #ارز #طلا #کریپتو"
    return msg

async def send_to_channel(bot):
    try:
        message = await create_message()
        await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] پیام با موفقیت ارسال شد.")
    except Exception as e:
        print("خطا در ارسال:", e)

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("ربات روی Railway شروع به کار کرد...")

    # اولین پست
    await send_to_channel(bot)

    while True:
        await asyncio.sleep(1800)  # هر ۳۰ دقیقه
        await send_to_channel(bot)

if __name__ == "__main__":
    asyncio.run(main())
