import logging, os, threading, sqlite3, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ================== HEALTH CHECK ==================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================== CONFIG ==================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = [6406804999]  # নিজের Telegram User ID
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(level=logging.INFO)

# ================== DATABASE ==================
db = sqlite3.connect("forcejoin.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS channels(
    id TEXT PRIMARY KEY,
    name TEXT,
    link TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    unlocked INTEGER DEFAULT 0
)
""")
db.commit()

# ================== INITIAL CHANNELS ==================
INITIAL_CHANNELS = [
    ("@virallink259","ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬🔥❤️","https://t.me/virallink259"),
    ("-1002279183424","Primium App Zone","https://t.me/+5PNLgcRBC0IxYjll"),
    ("@virallink246","Bd beauty viral","https://t.me/virallink246"),
    ("@viralexpress1","Facebook🔥 Instagram Link🔥","https://t.me/viralexpress1"),
    ("@movietime467","🎬MOVIE🔥 TIME💥","https://t.me/movietime467"),
    ("@viralfacebook9","BD MMS VIDEO🔥🔥","https://t.me/viralfacebook9"),
    ("@viralfb24","দেশি ভাবি ভাইরাল🔥🥵","https://t.me/viralfb24"),
    ("@fbviral24","কচি মেয়েদের ভাইরাল ভিদিও🔥","https://t.me/fbviral24"),
    ("-1001550993047","ভাইরাল ভিদিও রিকুয়েষ্ট🥵","https://t.me/+WAOUc1rX6Qk3Zjhl"),
    ("-1002011739504","Viral Video BD 🌍🔥","https://t.me/+la630-IFwHAwYWVl"),
    ("-1002444538806","Ai Prompt Studio 🎨📸","https://t.me/+AHsGXIDzWmJlZjVl")
]

for c in INITIAL_CHANNELS:
    cur.execute("INSERT OR IGNORE INTO channels VALUES(?,?,?)", c)
db.commit()

# ================== UTIL ==================
def is_admin(uid):
    return uid in ADMIN_IDS

async def check_all_joined(user_id, bot):
    not_joined = []
    for cid, name, link in cur.execute("SELECT * FROM channels"):
        try:
            member = await bot.get_chat_member(cid, user_id)
            if member.status not in ["member","administrator","creator"]:
                not_joined.append((cid,name,link))
        except:
            not_joined.append((cid,name,link))
    return not_joined

# ================== STATES ==================
BROADCAST_MODE = {}
POST_TITLE, POST_PHOTO, POST_CHANNELS, POST_WEBSITE = range(4)
POST_CREATION = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message is None: return
    uid = user.id
    
    if user.first_name and user.last_name:
        stylish_name = f"<b>{user.first_name} {user.last_name}</b>"
    else:
        stylish_name = f"<b>{user.first_name or 'User'}</b>"

    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(uid,))
    db.commit()
    not_joined = await check_all_joined(uid, context.bot)

    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await update.message.reply_text(
            f"🎉 স্বাগতম 👤 {stylish_name}\n✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]),
            parse_mode=ParseMode.HTML
        )
    else:
        buttons = [[InlineKeyboardButton(f"Join {name}", url=link)] for _,name,link in not_joined]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check")])
        caption = (f"Hello 👤 {stylish_name},\n\n🚨 <b>Attention Please!</b>\n\nViral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\nসবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\nJoin শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅")
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        context.job_queue.run_once(reminder, 120, data=uid)

# ================== CHECK ==================
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    not_joined = await check_all_joined(uid, context.bot)
    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await update.message.reply_text("✅ অভিনন্দন! সব চ্যানেল Join সম্পন্ন হয়েছে।", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await update.message.reply_text("❌ এখনও সব Channel Join হয়নি!")

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    not_joined = await check_all_joined(uid, context.bot)
    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await query.edit_message_text("✅ সব চ্যানেল Join সফল হয়েছে! ❤️", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await query.answer("❌ এখনো সব চ্যানেল Join করেননি!", show_alert=True)

# ================== REMINDER ==================
async def reminder(context):
    uid = context.data
    cur.execute("SELECT unlocked FROM users WHERE user_id=?",(uid,))
    r = cur.fetchone()
    if r and r[0] == 0:
        try: await context.bot.send_message(uid, "⏰ <b>Reminder!</b>\nভিডিও এখনও Unlock হয়নি 🔒", parse_mode=ParseMode.HTML)
        except: pass

# ================== POST CREATION (FIXED) ==================
async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    POST_CREATION[update.effective_user.id] = {'channels': set()}
    await update.message.reply_text("📝 Please send the <b>Post Title</b>:", parse_mode=ParseMode.HTML)
    return POST_TITLE

async def post_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📸 Now send the <b>Post Photo</b>:", parse_mode=ParseMode.HTML)
    return POST_PHOTO

async def post_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Photo পাঠান!")
        return POST_PHOTO
    POST_CREATION[update.effective_user.id]['photo'] = update.message.photo[-1].file_id
    buttons = [[InlineKeyboardButton(name, callback_data=f"pchan|{cid}")] for cid,name,link in cur.execute("SELECT * FROM channels")]
    buttons.append([InlineKeyboardButton("✅ Done Selecting", callback_data="pchan_done")])
    await update.message.reply_text("📌 Select channels:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_CHANNELS

async def post_channels_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "pchan_done":
        await query.edit_message_text("✅ URL দিন (অথবা 'skip' লিখুন):")
        return POST_WEBSITE
    cid = query.data.split("|")[1]
    POST_CREATION[uid]['channels'].add(cid)
    await query.answer("Added!")
    return POST_CHANNELS

async def post_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = POST_CREATION[uid]
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("Visit Website 🌐", url=update.message.text)]]) if update.message.text.lower() != 'skip' else None
    for cid in data['channels']:
        try: await context.bot.send_photo(cid, data['photo'], caption=data['title'], reply_markup=btn, parse_mode=ParseMode.HTML)
        except: pass
    await update.message.reply_text("✅ Post Sent!")
    POST_CREATION.pop(uid, None)
    return ConversationHandler.END

async def post_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION.pop(update.effective_user.id, None)
    BROADCAST_MODE.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ Cancelled!")
    return ConversationHandler.END

# ================== ADMIN & BROADCAST ==================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    BROADCAST_MODE[update.effective_user.id] = True
    await update.message.reply_text("📢 Broadcast Mode ON. Send Msg or /postcancel")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not BROADCAST_MODE.get(uid): return
    BROADCAST_MODE.pop(uid)
    users = cur.execute("SELECT user_id FROM users").fetchall()
    sent = 0
    for (u_id,) in users:
        try:
            await update.message.copy(u_id)
            sent += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {sent} users")

async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args)<3: return
    cur.execute("INSERT OR REPLACE INTO channels VALUES(?,?,?)",(context.args[0], " ".join(context.args[2:]).strip('"'), context.args[1]))
    db.commit()
    await update.message.reply_text("✅ Added")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg = "".join([f"• {n}\n" for _,n,_ in cur.execute("SELECT * FROM channels")])
    await update.message.reply_text(msg or "Empty")

# ================== RUN BOT ==================
app = Application.builder().token(TOKEN).build()

# Post Conversation
post_handler = ConversationHandler(
    entry_points=[CommandHandler("newpost", newpost)],
    states={
        POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title_handler)],
        POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo_handler)],
        POST_CHANNELS: [CallbackQueryHandler(post_channels_callback, pattern="^pchan")],
        POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_website_handler)]
    },
    fallbacks=[CommandHandler("postcancel", post_cancel)]
)

app.add_handler(post_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("addchannel", addchannel))
app.add_handler(CommandHandler("listchannels", listchannels))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("postcancel", post_cancel))
app.add_handler(CallbackQueryHandler(check_callback, pattern="check"))
app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_broadcast))

print("🔥 FULL FORCE JOIN BOT RUNNING...")
app.run_polling()
