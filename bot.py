import os, threading, time, random, sqlite3, json, hmac, hashlib
from urllib.parse import parse_qsl
from flask import Flask, request, jsonify
import telebot

TOKEN=os.getenv("BOT_TOKEN","")
ADMIN_IDS=881119277
PUBLIC_API_URL=os.getenv("PUBLIC_API_URL","").rstrip("/")
WEBAPP_URL=os.getenv("WEBAPP_URL","https://jurabek003-art.github.io/Jurabekb2telc/")
bot=telebot.TeleBot(TOKEN) if TOKEN else None
app=Flask(__name__)
DB=os.getenv("DB_PATH","jurabek_b2.db")
MESSAGES=["🔔 TELC B2 sizni kutmoqda! 🇩🇪\n\nXatolaringizni takrorlang. B2 sertifikatini tezroq oling. Kelajagingiz uchun harakat qiling. 💪","📚 Bugun yana bir qadam oldinga!\n\nO‘zlashtirilmagan savollaringizni qayta ishlang va B2 maqsadingizga yaqinlashing. 🇩🇪","🎯 B2 maqsadingizni unutmang!\n\nKichik mashg‘ulot ham katta natijaga olib keladi. Hozir bir nechta savol ishlab ko‘ring. 💪"]

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,chat_id TEXT,first_name TEXT,last_name TEXT,username TEXT,xp INTEGER DEFAULT 0,completed INTEGER DEFAULT 0,correct INTEGER DEFAULT 0,wrong INTEGER DEFAULT 0,mastered INTEGER DEFAULT 0,total_questions INTEGER DEFAULT 637,readiness INTEGER DEFAULT 0,last_active REAL,created_at REAL,blocked INTEGER DEFAULT 0,is_admin INTEGER DEFAULT 0)')
        c.execute('CREATE TABLE IF NOT EXISTS broadcasts(id INTEGER PRIMARY KEY AUTOINCREMENT,text TEXT,created_at REAL,sent INTEGER DEFAULT 0)')
init_db()

@app.after_request
def cors(r):
    r.headers['Access-Control-Allow-Origin']='*';r.headers['Access-Control-Allow-Headers']='Content-Type';r.headers['Access-Control-Allow-Methods']='GET,POST,OPTIONS';return r

def tg_user(init_data):
    if not init_data or not TOKEN:return None
    vals=dict(parse_qsl(init_data,keep_blank_values=True)); got=vals.pop('hash',None)
    if not got:return None
    data='\n'.join(f'{k}={v}' for k,v in sorted(vals.items()))
    secret=hmac.new(b'WebAppData',TOKEN.encode(),hashlib.sha256).digest()
    calc=hmac.new(secret,data.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc,got):return None
    try:return json.loads(vals.get('user','{}'))
    except:return None

def auth():
    u=tg_user(request.headers.get('X-Telegram-Init-Data',''))
    if not u:
        data=request.get_json(silent=True) or {}; uid=str(data.get('user_id',''))
        if os.getenv('ALLOW_DEV_AUTH')=='1' and uid:return {'id':uid,'first_name':data.get('name','Dev')}
        return None
    return u

def upsert(u,stats=None):
    uid=str(u['id']); now=time.time(); stats=stats or {}
    with db() as c:
        c.execute('INSERT INTO users(id,chat_id,first_name,last_name,username,last_active,created_at,is_admin) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET chat_id=excluded.chat_id,first_name=excluded.first_name,last_name=excluded.last_name,username=excluded.username,last_active=excluded.last_active,is_admin=MAX(users.is_admin,excluded.is_admin)',(uid,uid,u.get('first_name',''),u.get('last_name',''),u.get('username',''),now,now,1 if uid in ADMIN_IDS else 0))
        if stats:
            c.execute('UPDATE users SET xp=?,completed=?,correct=?,wrong=?,mastered=?,total_questions=?,readiness=?,last_active=? WHERE id=?',(int(stats.get('xp',0)),int(stats.get('completed',0)),int(stats.get('correct',0)),int(stats.get('wrong',0)),int(stats.get('mastered',0)),int(stats.get('total_questions',637)),int(stats.get('readiness',0)),now,uid))

def is_admin(uid):
    if str(uid) in ADMIN_IDS:return True
    with db() as c:
        r=c.execute('SELECT is_admin FROM users WHERE id=?',(str(uid),)).fetchone();return bool(r and r['is_admin'])

def require_admin():
    u=auth()
    if not u or not is_admin(u['id']):return None
    return u

@app.route('/')
def home(): return 'Jurabek B2 TELC bot ishlayapti!'
@app.route('/api/me',methods=['GET','POST','OPTIONS'])
def me():
    if request.method=='OPTIONS':return ('',204)
    u=auth()
    if not u:return jsonify(ok=False),401
    upsert(u);return jsonify(ok=True,user=u,is_admin=is_admin(u['id']))
@app.route('/api/sync',methods=['POST','OPTIONS'])
def sync():
    if request.method=='OPTIONS':return ('',204)
    u=auth()
    if not u:return jsonify(ok=False),401
    d=request.get_json(silent=True) or {};upsert(u,d.get('stats') or {})
    return jsonify(ok=True,is_admin=is_admin(u['id']))
@app.route('/api/leaderboard',methods=['GET'])
def leaderboard():
    with db() as c: rows=c.execute('SELECT id,first_name,last_name,username,xp,completed,mastered,readiness FROM users WHERE blocked=0 ORDER BY xp DESC,mastered DESC,last_active DESC LIMIT 100').fetchall()
    return jsonify([dict(x) for x in rows])
@app.route('/api/admin/users',methods=['POST','OPTIONS'])
def admin_users():
    if request.method=='OPTIONS':return ('',204)
    a=require_admin()
    if not a:return jsonify(ok=False),403
    with db() as c: rows=c.execute('SELECT * FROM users ORDER BY last_active DESC').fetchall()
    return jsonify(ok=True,users=[dict(x) for x in rows])
@app.route('/api/admin/action',methods=['POST','OPTIONS'])
def admin_action():
    if request.method=='OPTIONS':return ('',204)
    a=require_admin()
    if not a:return jsonify(ok=False),403
    d=request.get_json(silent=True) or {};uid=str(d.get('user_id',''));act=d.get('action')
    with db() as c:
        if act=='block':c.execute('UPDATE users SET blocked=1 WHERE id=?',(uid,))
        elif act=='unblock':c.execute('UPDATE users SET blocked=0 WHERE id=?',(uid,))
        elif act=='reset':c.execute('UPDATE users SET xp=0,completed=0,correct=0,wrong=0,mastered=0,readiness=0 WHERE id=?',(uid,))
        elif act=='make_admin':c.execute('UPDATE users SET is_admin=1 WHERE id=?',(uid,))
        elif act=='remove_admin' and uid not in ADMIN_IDS:c.execute('UPDATE users SET is_admin=0 WHERE id=?',(uid,))
        else:return jsonify(ok=False,error='unknown action'),400
    return jsonify(ok=True)
@app.route('/api/admin/broadcast',methods=['POST','OPTIONS'])
def broadcast():
    if request.method=='OPTIONS':return ('',204)
    a=require_admin()
    if not a:return jsonify(ok=False),403
    d=request.get_json(silent=True) or {};text=str(d.get('text','')).strip()
    if not text:return jsonify(ok=False),400
    sent=0
    if bot:
        with db() as c: rows=c.execute('SELECT chat_id FROM users WHERE blocked=0').fetchall()
        for r in rows:
            try:bot.send_message(r['chat_id'],text);sent+=1
            except:pass
    return jsonify(ok=True,sent=sent)

if bot:
 @bot.message_handler(commands=['start'])
 def start(message):
    u={'id':message.from_user.id,'first_name':message.from_user.first_name or '','last_name':message.from_user.last_name or '','username':message.from_user.username or ''};upsert(u)
    url=WEBAPP_URL
    if PUBLIC_API_URL:url += ('&' if '?' in url else '?')+'api='+PUBLIC_API_URL
    markup=telebot.types.InlineKeyboardMarkup();markup.add(telebot.types.InlineKeyboardButton('🚀 O‘qishni boshlash',web_app=telebot.types.WebAppInfo(url)))
    bot.send_message(message.chat.id,'🇩🇪 Assalomu alaykum!\n\nJurabek B2 TELC botiga xush kelibsiz! 👋\n\nTELC B2 tayyorgarligini boshlash uchun tugmani bosing 👇',reply_markup=markup)

def reminder_loop():
    while True:
        if bot:
            now=time.time()
            with db() as c: rows=c.execute('SELECT chat_id,last_active FROM users WHERE blocked=0').fetchall()
            for u in rows:
                if u['last_active'] and now-u['last_active']>=4*3600:
                    try:bot.send_message(u['chat_id'],random.choice(MESSAGES))
                    except:pass
        time.sleep(300)
def run_bot():
    if bot:bot.infinity_polling(skip_pending=True)
if __name__=='__main__':
    threading.Thread(target=run_bot,daemon=True).start();threading.Thread(target=reminder_loop,daemon=True).start();app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
