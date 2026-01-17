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
ADMIN_IDS = [6406804999]
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
    cur.execute("SELECT * FROM channels")
    rows = cur.fetchall()
    for cid, name, link in rows:
        try:
            member = await bot.get_chat_member(cid, user_id)
            if member.status not in ["member","administrator","creator"]:
                not_joined.append((cid,name,link))
        except:
            not_joined.append((cid,name,link))
    return not_joined

async def check_specific_channels(user_id, bot, channel_list):
    not_joined = []
    for cid in channel_list:
        cur.execute("SELECT name, link FROM channels WHERE id=?", (cid,))
        res = cur.fetchone()
        if res:
            try:
                member = await bot.get_chat_member(cid, user_id)
                if member.status not in ["member","administrator","creator"]:
                    not_joined.append((cid, res[0], res[1]))
            except:
                not_joined.append((cid, res[0], res[1]))
    return not_joined

# ================== STATES ==================
BROADCAST_MODE = {}
POST_TITLE, POST_PHOTO, POST_WEBSITE, POST_FORCE_CHANS, POST_TARGET_CHANS, POST_CONFIRM = range(6)
POST_CREATION = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message is None: return
    uid = user.id
    stylish_name = f"<b>{user.first_name} {user.last_name or ''}</b>"

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

# ================== CHECK CALLBACK ==================
async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    not_joined = await check_all_joined(uid, context.bot)
    if not not_joined:
        cur.execute("UPDATE users SET unlocked=1 WHERE user_id=?",(uid,))
        db.commit()
        await query.edit_message_text("✅ সব চ্যানেল Join সফল হয়েছে! ❤️", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)]]))
    else:
        await query.answer("❌ এখনো সব চ্যানেল Join করেননি!", show_alert=True)

# ================== NEW POST WIZARD ==================
def get_channel_markup(selected_list, prefix):
    keyboard = []
    cur.execute("SELECT id, name FROM channels")
    for cid, name in cur.fetchall():
        status = "✅" if cid in selected_list else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"{prefix}|{cid}")])
    keyboard.append([InlineKeyboardButton("➡️ Selected (Done)", callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(keyboard)

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    POST_CREATION[update.effective_user.id] = {'force': set(), 'target': set()}
    await update.message.reply_text("📝 **ধাপ ১:** পোস্টের ক্যাপশন বা টাইটেল দিন:", parse_mode=ParseMode.MARKDOWN)
    return POST_TITLE

async def post_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_CREATION[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📸 **ধাপ ২:** পোস্টের জন্য একটি ফটো পাঠান:", parse_mode=ParseMode.MARKDOWN)
    return POST_PHOTO

async def post_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ ফটো পাঠান!")
        return POST_PHOTO
    POST_CREATION[update.effective_user.id]['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("🔗 **ধাপ ৩:** ওয়েবসাইট বা ভিডিও লিঙ্ক দিন (বা 'skip' লিখুন):", parse_mode=ParseMode.MARKDOWN)
    return POST_WEBSITE

async def post_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    POST_CREATION[update.effective_user.id]['link'] = WATCH_NOW_URL if text.lower() == 'skip' else text
    uid = update.effective_user.id
    await update.message.reply_text("🛡️ **ধাপ ৪:** ফোর্স জয়েন চ্যানেলগুলো সিলেক্ট করুন:", 
                                   reply_markup=get_channel_markup(POST_CREATION[uid]['force'], "fsel"), parse_mode=ParseMode.MARKDOWN)
    return POST_FORCE_CHANS

async def post_force_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    if query.data == "fsel_done":
        await query.edit_message_text("📢 **ধাপ ৫:** পোস্টটি কোন কোন চ্যানেলে পাঠাতে চান? সিলেক্ট করুন:", 
                                     reply_markup=get_channel_markup(POST_CREATION[uid]['target'], "tsel"))
        return POST_TARGET_CHANS
    cid = query.data.split("|")[1]
    if cid in POST_CREATION[uid]['force']: POST_CREATION[uid]['force'].remove(cid)
    else: POST_CREATION[uid]['force'].add(cid)
    await query.edit_message_reply_markup(get_channel_markup(POST_CREATION[uid]['force'], "fsel"))
    return POST_FORCE_CHANS

async def post_target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    if query.data == "tsel_done":
        if not POST_CREATION[uid]['target']:
            await query.answer("❌ অন্তত ১টি টার্গেট চ্যানেল সিলেক্ট করুন!", show_alert=True)
            return POST_TARGET_CHANS
        await query.message.reply_text("⚠️ আপনি কি নিশ্চিত? সব সিলেক্ট করা চ্যানেলে পোস্ট পাঠানো হবে।", 
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("✅ Yes, Send Now!", callback_data="final_send")],
                                          [InlineKeyboardButton("❌ Cancel", callback_data="post_cancel")]
                                      ]))
        return POST_CONFIRM
    cid = query.data.split("|")[1]
    if cid in POST_CREATION[uid]['target']: POST_CREATION[uid]['target'].remove(cid)
    else: POST_CREATION[uid]['target'].add(cid)
    await query.edit_message_reply_markup(get_channel_markup(POST_CREATION[uid]['target'], "tsel"))
    return POST_TARGET_CHANS

async def final_send_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = POST_CREATION[uid]
    force_ids = ",".join(data['force']) if data['force'] else "none"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Video 🔞", callback_data=f"v|{force_ids}|{data['link']}")]])
    success = 0
    for t_cid in data['target']:
        try:
            await context.bot.send_photo(chat_id=t_cid, photo=data['photo'], caption=data['title'], reply_markup=btn, parse_mode=ParseMode.HTML)
            success += 1
            await asyncio.sleep(0.1)
        except: pass
    await query.message.reply_text(f"✅ পোস্ট সফলভাবে {success}টি চ্যানেলে পাঠানো হয়েছে!")
    POST_CREATION.pop(uid, None)
    return ConversationHandler.END

# ================== WATCH CALLBACK ==================
async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    _, force_str, url = query.data.split("|", 2)
    required_ids = [] if force_str == "none" else force_str.split(",")
    not_joined = await check_specific_channels(uid, context.bot, required_ids)
    if not not_joined:
        await query.answer("✅ Access Granted!")
        try: await context.bot.send_message(uid, f"🚀 **Your Video Link:**\n{url}", parse_mode=ParseMode.HTML)
        except: await query.answer("❌ Please start the bot in private first!", show_alert=True)
    else:
        await query.answer("❌ Access Denied!", show_alert=True)
        buttons = [[InlineKeyboardButton(f"Join {n}", url=l)] for _, n, l in not_joined]
        buttons.append([InlineKeyboardButton("♻️ Try Again", callback_data=query.data)])
        await context.bot.send_message(uid, "🚫 **ভিডিওটি দেখতে নিচের চ্যানেলগুলোতে জয়েন থাকতে হবে:**", reply_markup=InlineKeyboardMarkup(buttons))

# ================== BROADCAST ==================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    BROADCAST_MODE[update.effective_user.id] = True
    await update.message.reply_text("📢 Broadcast Mode ON. Send message or /postcancel")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not BROADCAST_MODE.get(uid): return
    BROADCAST_MODE.pop(uid)
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    sent = 0
    for (u_id,) in users:
        try:
            await update.message.copy(u_id)
            sent += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {sent} users")

async def post_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    POST_CREATION.pop(uid, None)
    BROADCAST_MODE.pop(uid, None)
    await (update.message or update.callback_query.message).reply_text("❌ Cancelled!")
    return ConversationHandler.END

# ================== APP SETUP ==================
app = Application.builder().token(TOKEN).build()

post_handler = ConversationHandler(
    entry_points=[CommandHandler("newpost", newpost)],
    states={
        POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title_handler)],
        POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo_handler)],
        POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_website_handler)],
        POST_FORCE_CHANS: [CallbackQueryHandler(post_force_callback, pattern="^fsel")],
        POST_TARGET_CHANS: [CallbackQueryHandler(post_target_callback, pattern="^tsel")],
        POST_CONFIRM: [CallbackQueryHandler(final_send_handler, pattern="^final_send"),
                       CallbackQueryHandler(post_cancel, pattern="^post_cancel")]
    },
    fallbacks=[CommandHandler("postcancel", post_cancel)]
)

app.add_handler(post_handler)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("postcancel", post_cancel))
app.add_handler(CallbackQueryHandler(check_callback, pattern="^check$"))
app.add_handler(CallbackQueryHandler(watch_callback, pattern="^v\|"))
app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_broadcast))

print("🔥 FULL POWER BOT RUNNING...")
app.run_polling()
