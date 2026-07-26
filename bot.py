import os, threading, time, random
from flask import Flask, request, jsonify
import telebot

TOKEN=os.getenv("BOT_TOKEN")
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)
users={}
MESSAGES=[
"🔔 TELC B2 sizni kutmoqda! 🇩🇪\n\nXatolaringizni takrorlang. B2 sertifikatini tezroq oling. Kelajagingiz uchun harakat qiling. 💪",
"📚 Bugun yana bir qadam oldinga!\n\nO‘zlashtirilmagan savollaringizni qayta ishlang va B2 maqsadingizga yaqinlashing. 🇩🇪",
"🎯 B2 maqsadingizni unutmang!\n\nKichik mashg‘ulot ham katta natijaga olib keladi. Hozir bir nechta savol ishlab ko‘ring. 💪",
"🔥 Har bir tuzatilgan xato — B2 ga yana bir qadam.\n\nBugungi mashg‘ulotni davom ettiring! 🇩🇪"
]
URL="https://jurabek003-art.github.io/Jurabekb2telc/"

@app.route("/")
def home(): return "Jurabek B2 TELC bot ishlayapti!"

@app.route("/activity",methods=["POST"])
def activity():
    data=request.get_json(silent=True) or {}
    uid=str(data.get("user_id",""))
    if uid in users: users[uid]["last"]=time.time()
    return jsonify(ok=True)

@bot.message_handler(commands=["start"])
def start(message):
    uid=str(message.chat.id);users[uid]={"chat_id":message.chat.id,"last":time.time()}
    markup=telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 O‘qishni boshlash",web_app=telebot.types.WebAppInfo(URL)))
    bot.send_message(message.chat.id,"🇩🇪 Assalomu alaykum!\n\nJurabek B2 TELC botiga xush kelibsiz! 👋\n\nTELC B2 tayyorgarligini boshlash uchun tugmani bosing 👇",reply_markup=markup)

def reminder_loop():
    while True:
        now=time.time()
        for uid,u in list(users.items()):
            if now-u["last"]>=4*3600:
                try:
                    bot.send_message(u["chat_id"],random.choice(MESSAGES))
                    u["last"]=now
                except Exception: pass
        time.sleep(300)

def run_bot(): bot.infinity_polling(skip_pending=True)
if __name__=="__main__":
    threading.Thread(target=run_bot,daemon=True).start()
    threading.Thread(target=reminder_loop,daemon=True).start()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
