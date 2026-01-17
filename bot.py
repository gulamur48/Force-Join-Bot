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

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

threading.Thread(target=run_health, daemon=True).start()

# ================== CONFIG ==================
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = [6406804999]
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(level=logging.INFO)

# ================== DATABASE ==================
db = sqlite3.connect("forcejoin.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS channels(
    id TEXT PRIMARY KEY,
    name TEXT,
    link TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY
)""")
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
    cur.execute("INSERT OR IGNORE INTO channels VALUES (?,?,?)", c)
db.commit()

# ================== UTIL ==================
def is_admin(uid): 
    return uid in ADMIN_IDS

async def check_join(uid, bot, ids):
    for cid in ids:
        try:
            m = await bot.get_chat_member(cid, uid)
            if m.status not in ("member","administrator","creator"):
                return False
        except:
            return False
    return True

# ================== STATES ==================
POST_TITLE, POST_PHOTO, POST_FORCE, POST_TARGET, POST_URL = range(5)
POST = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cur.execute("INSERT OR IGNORE INTO users VALUES(?)",(uid,))
    db.commit()

    cur.execute("SELECT * FROM channels")
    rows = cur.fetchall()

    not_joined = []
    for cid,n,l in rows:
        try:
            m = await context.bot.get_chat_member(cid, uid)
            if m.status not in ("member","administrator","creator"):
                not_joined.append((n,l))
        except:
            not_joined.append((n,l))

    if not not_joined:
        await update.message.reply_text(
            "✅ সব চ্যানেল Join করা আছে",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
            )
        )
    else:
        btn = [[InlineKeyboardButton(f"Join {n}", url=l)] for n,l in not_joined]
        btn.append([InlineKeyboardButton("Check Joined ✅", callback_data="check")])
        await update.message.reply_text(
            "🚫 ভিডিও দেখতে নিচের চ্যানেলগুলো Join করতে হবে",
            reply_markup=InlineKeyboardMarkup(btn)
        )

# ================== CHECK ==================
async def check_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.callback_query.from_user.id
    cur.execute("SELECT id FROM channels")
    ids = [i[0] for i in cur.fetchall()]
    if await check_join(uid, context.bot, ids):
        await update.callback_query.edit_message_text(
            "✅ Verified!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]
            )
        )
    else:
        await update.callback_query.answer("❌ এখনো Join বাকি", show_alert=True)

# ================== NEW POST ==================
async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    POST[update.effective_user.id] = {"force":set(),"target":set()}
    await update.message.reply_text("📝 Post Title পাঠান")
    return POST_TITLE

async def post_title(update, context):
    POST[update.effective_user.id]["title"] = update.message.text
    await update.message.reply_text("📸 Photo পাঠান")
    return POST_PHOTO

async def post_photo(update, context):
    if not update.message.photo:
        await update.message.reply_text("❌ Photo দিন")
        return POST_PHOTO
    POST[update.effective_user.id]["photo"] = update.message.photo[-1].file_id
    return await show_channels(update, context, POST_FORCE)

async def show_channels(update, context, state):
    cur.execute("SELECT id,name FROM channels")
    kb=[]
    for cid,n in cur.fetchall():
        kb.append([InlineKeyboardButton(n, callback_data=f"{state}|{cid}")])
    kb.append([InlineKeyboardButton("Done ✅", callback_data=f"{state}|done")])
    await update.message.reply_text(
        "Select Channels:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return state

async def select_force(update, context):
    q=update.callback_query
    uid=q.from_user.id
    _,cid=q.data.split("|")
    if cid=="done":
        await q.message.delete()
        return await show_channels(update, context, POST_TARGET)
    POST[uid]["force"].add(cid)
    await q.answer("Added")
    return POST_FORCE

async def select_target(update, context):
    q=update.callback_query
    uid=q.from_user.id
    _,cid=q.data.split("|")
    if cid=="done":
        await q.message.reply_text("🔗 URL দিন বা skip লিখুন")
        return POST_URL
    POST[uid]["target"].add(cid)
    await q.answer("Added")
    return POST_TARGET

async def post_url(update, context):
    uid=update.effective_user.id
    data=POST[uid]
    url = WATCH_NOW_URL if update.message.text.lower()=="skip" else update.message.text
    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎬 Watch Video", callback_data=f"watch|{','.join(data['force'])}|{url}")]]
    )
    for t in data["target"]:
        try:
            await context.bot.send_photo(t,data["photo"],caption=data["title"],reply_markup=btn)
        except: pass
    await update.message.reply_text("✅ Post Sent")
    POST.pop(uid,None)
    return ConversationHandler.END

# ================== WATCH ==================
async def watch(update, context):
    q=update.callback_query
    _,chs,url = q.data.split("|",2)
    ids = chs.split(",") if chs else []
    if await check_join(q.from_user.id, context.bot, ids):
        await context.bot.send_message(q.from_user.id, f"🔗 {url}")
    else:
        await q.answer("❌ Join required", show_alert=True)

# ================== APP ==================
app = Application.builder().token(TOKEN).build()

post_conv = ConversationHandler(
    entry_points=[CommandHandler("newpost", newpost)],
    states={
        POST_TITLE:[MessageHandler(filters.TEXT, post_title)],
        POST_PHOTO:[MessageHandler(filters.PHOTO | filters.TEXT, post_photo)],
        POST_FORCE:[CallbackQueryHandler(select_force)],
        POST_TARGET:[CallbackQueryHandler(select_target)],
        POST_URL:[MessageHandler(filters.TEXT, post_url)]
    },
    fallbacks=[CommandHandler("postcancel", lambda u,c: ConversationHandler.END)]
)

app.add_handler(post_conv)
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_cb, pattern="^check$"))
app.add_handler(CallbackQueryHandler(watch, pattern="^watch"))
app.run_polling()
