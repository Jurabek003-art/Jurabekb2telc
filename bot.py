import os
import threading
from flask import Flask
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Jurabek B2 TELC bot ishlayapti!"

@bot.message_handler(commands=["start"])
def start(message):
    text = """
🇩🇪 Assalomu alaykum!

Jurabek B2 TELC botiga xush kelibsiz! 👋

Bu yerda siz nemis tilini tez va oson o‘rganishingiz hamda TELC B2 imtihoniga tayyorlanishingiz mumkin.

📚 Mavzular
📝 Testlar
📋 Shpargalka
🏆 Reyting

Boshlash uchun tugmani bosing 👇
"""

    markup = telebot.types.InlineKeyboardMarkup()

    button = telebot.types.InlineKeyboardButton(
        "🚀 O‘qishni boshlash",
        web_app=telebot.types.WebAppInfo(
            "https://jurabek003-art.github.io/Jurabekb2telc/"
        )
    )

    markup.add(button)
    bot.send_message(message.chat.id, text, reply_markup=markup)

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
