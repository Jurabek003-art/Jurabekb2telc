import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    text = """
🇩🇪 Assalomu alaykum!

Jurabek B2 TELC botiga xush kelibsiz! 👋

Bu yerda siz nemis tilini tez va oson o‘rganishingiz hamda TELC B2 imtihoniga tayyorlanishingiz mumkin.

📚 Mavzularni o‘rganing
📝 Testlarni ishlang
📋 Shpargalkalardan foydalaning
🏆 Natijalaringizni yaxshilang

👇 Boshlash uchun pastdagi tugmani bosing.
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

bot.infinity_polling()
