import logging, os, threading, sqlite3, asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
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

# ================== BROADCAST STATE ==================
BROADCAST_MODE = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    # Stylish name
    if user.first_name and user.last_name:
        stylish_name = f"<b>{user.first_name} {user.last_name}</b>"
    elif user.first_name:
        stylish_name = f"<b>{user.first_name}</b>"
    else:
        stylish_name = "<b>User</b>"

    # Auto save user
    cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(uid,))
    db.commit()

    # Check channels
    not_joined = await check_all_joined(uid, context.bot)

    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await update.message.reply_text(
            f"🎉 স্বাগতম 👤 {stylish_name}\n✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
            ),
            parse_mode=ParseMode.HTML
        )
    else:
        # Button List
        buttons = [[InlineKeyboardButton(f"Join {name}", url=link)] for _,name,link in not_joined]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check")])

        caption = (
            f"Hello 👤 {stylish_name},\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
            "সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
            "Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅"
        )

        await update.message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
        # Reminder after 2 minutes
        context.job_queue.run_once(reminder, 120, data=uid)

# ================== CHECK JOIN ==================
async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    stylish_name = f"<b>{query.from_user.first_name}</b>"

    not_joined = await check_all_joined(uid, context.bot)

    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await query.edit_message_text(
            f"🎉 স্বাগতম 👤 {stylish_name}\n✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
            ),
            parse_mode=ParseMode.HTML
        )
    else:
        await query.answer("❌ এখনও সব Channel Join হয়নি!", show_alert=True)

# ================== REMINDER ==================
async def reminder(context):
    uid = context.data
    cur.execute("SELECT unlocked FROM users WHERE user_id=?",(uid,))
    r = cur.fetchone()
    if r and r[0] == 0:
        try:
            await context.bot.send_message(
                uid,
                "⏰ <b>Reminder!</b>\nভিডিও এখনও Unlock হয়নি 🔒",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

# ================== ADMIN COMMANDS ==================
async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    cid = context.args[0]
    link = context.args[1]
    name = " ".join(context.args[2:]).strip('"')
    cur.execute("INSERT OR REPLACE INTO channels VALUES(?,?,?)",(cid,name,link))
    db.commit()
    await update.message.reply_text("✅ Channel Added Successfully")

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    cur.execute("DELETE FROM channels WHERE id=?",(context.args[0],))
    db.commit()
    await update.message.reply_text("❌ Channel Removed")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg=""
    for i,(cid,n,l) in enumerate(cur.execute("SELECT * FROM channels"),1):
        msg+=f"{i}️⃣ {n}\n"
    await update.message.reply_text(msg or "No Channel Found")

# ================== BROADCAST ==================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    BROADCAST_MODE[update.effective_user.id] = True
    await update.message.reply_text(
        "📢 Broadcast Mode ON\n"
        "➡️ Text or Photo পাঠান\n"
        "➡️ Caption এ লিখুন:\n"
        "ButtonText | https://button-link.com\n"
        "❌ Cancel করতে /cancel"
    )

async def handle_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not BROADCAST_MODE.get(uid):
        return

    BROADCAST_MODE.pop(uid)

    button = None
    text = update.message.caption or update.message.text

    if "|" in text:
        btn_text, btn_url = text.split("|",1)
        button = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text.strip(), url=btn_url.strip())]])
        text = text.split("|")[0].strip()

    users = cur.execute("SELECT user_id FROM users").fetchall()
    sent = 0

    for (user_id,) in users:
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=update.message.photo[-1].file_id,
                    caption=text,
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast Done\n👥 Sent to {sent} users")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BROADCAST_MODE.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ Broadcast Cancelled")

# ================== RUN BOT ==================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_callback, "check"))
app.add_handler(CommandHandler("addchannel", addchannel))
app.add_handler(CommandHandler("removechannel", removechannel))
app.add_handler(CommandHandler("listchannels", listchannels))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(MessageHandler(filters.ALL, handle_broadcast_content))

print("🔥 FORCE JOIN BOT with Broadcast running...")
app.run_polling()
