import logging
import os
import threading
import sqlite3
import asyncio
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Set, Dict, Optional

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto,
    constants
)
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler,
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# ====================================================================
# 🔥 CONFIGURATION & CONSTANTS
# ====================================================================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = [6406804999]  # আপনার অ্যাডমিন আইডি
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

# Database File
DB_NAME = "premium_forcejoin.db"

# Conversation States
POST_TITLE, POST_PHOTO, POST_WEBSITE, POST_FORCE_CHANS, POST_TARGET_CHANS, POST_CONFIRM = range(6)
BROADCAST_MSG = 10

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================================================================
# 🌐 HEALTH CHECK SERVER (For 24/7 Hosting)
# ====================================================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Bot is Alive & Running! 🚀</h1>")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"🌍 Web server running on port {port}")
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ====================================================================
# 🗄️ DATABASE MANAGER
# ====================================================================
class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY, 
                name TEXT, 
                link TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        self.conn.commit()

    def get_total_users(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def add_channel(self, c_id, name, link):
        self.cursor.execute("INSERT OR REPLACE INTO channels VALUES(?,?,?)", (c_id, name, link))
        self.conn.commit()

    def delete_channel(self, c_id):
        self.cursor.execute("DELETE FROM channels WHERE id=?", (c_id,))
        self.conn.commit()

    def get_all_channels(self):
        self.cursor.execute("SELECT * FROM channels")
        return self.cursor.fetchall()
    
    def get_channel(self, c_id):
        self.cursor.execute("SELECT name, link FROM channels WHERE id=?", (c_id,))
        return self.cursor.fetchone()

    def get_all_user_ids(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]

db = DatabaseManager(DB_NAME)

# ====================================================================
# ⚡ INITIAL DATA SEEDING
# ====================================================================
INITIAL_CHANNELS = [
    ("@virallink259","🔥 Viral Video Express","https://t.me/virallink259"),
    ("-1002279183424","💎 Premium App Zone","https://t.me/+5PNLgcRBC0IxYjll"),
    ("@virallink246","🇧🇩 BD Beauty Viral","https://t.me/virallink246"),
    ("@viralexpress1","📸 FB/Insta Leaks","https://t.me/viralexpress1"),
    ("@movietime467","🎬 Movie Time 467","https://t.me/movietime467"),
    ("@viralfacebook9","🌶️ BD MMS Video","https://t.me/viralfacebook9"),
    ("@viralfb24","🥵 Deshi Vabi Viral","https://t.me/viralfb24"),
    ("@fbviral24","💃 Kachi Meyer Video","https://t.me/fbviral24"),
    ("-1001550993047","📥 Video Request","https://t.me/+WAOUc1rX6Qj3Zjhl"),
    ("-1002011739504","🌍 Viral World BD","https://t.me/+la630-IFwHAwYWVl"),
    ("-1002444538806","🎨 AI Prompt Studio","https://t.me/+AHsGXIDzWmJlZjVl")
]

for c in INITIAL_CHANNELS:
    db.add_channel(c[0], c[1], c[2])

# ====================================================================
# 🛠️ HELPER FUNCTIONS
# ====================================================================
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user.id not in ADMIN_IDS:
            await update.message.reply_text("⛔ <b>Access Denied!</b>")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

async def check_subscription(user_id, bot):
    not_joined = []
    channels = db.get_all_channels()
    for cid, name, link in channels:
        try:
            member = await bot.get_chat_member(cid, user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                not_joined.append((cid, name, link))
        except:
            not_joined.append((cid, name, link))
    return not_joined

async def check_specific_subscription(user_id, bot, channel_ids):
    not_joined = []
    for cid in channel_ids:
        res = db.get_channel(cid)
        if res:
            try:
                member = await bot.get_chat_member(cid, user_id)
                if member.status in ['left', 'kicked']:
                    not_joined.append((cid, res[0], res[1]))
            except:
                not_joined.append((cid, res[0], res[1]))
    return not_joined

def get_selection_markup(selected_ids, prefix):
    keyboard = []
    channels = db.get_all_channels()
    for cid, name, _ in channels:
        status = "✅" if cid in selected_ids else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"{prefix}|{cid}")])
    keyboard.append([InlineKeyboardButton("➡️ Selected (Next Step)", callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(keyboard)

# ====================================================================
# 🤖 BOT COMMAND HANDLERS
# ====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id)
    msg = await update.message.reply_text("⚡ <i>Processing...</i>", parse_mode=ParseMode.HTML)
    not_joined = await check_subscription(user.id, context.bot)
    if not not_joined:
        await msg.delete()
        await update.message.reply_text(f"🎉 <b>স্বাগতম {user.first_name}!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now 🎬", url=WATCH_NOW_URL)]]), parse_mode=ParseMode.HTML)
    else:
        keyboard = [[InlineKeyboardButton(f"Join {i+1} 🚀", url=c[2])] for i, c in enumerate(not_joined)]
        keyboard.append([InlineKeyboardButton("✅ I Have Joined (Verify) 🔄", callback_data="check_status")])
        await msg.edit_text("🔒 <b>Access Locked!</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    not_joined = await check_subscription(query.from_user.id, context.bot)
    if not not_joined:
        await query.message.edit_text("🎉 ভেরিফিকেশন সফল!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now 🎬", url=WATCH_NOW_URL)]]), parse_mode=ParseMode.HTML)
    else:
        await query.answer("❌ আপনি জয়েন করেননি!", show_alert=True)

# ====================================================================
# 📝 NEW POST WIZARD (আপনার চাহিদা মতো ফ্লো)
# ====================================================================
POST_DATA = {}

@admin_only
async def newpost_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    POST_DATA[user_id] = {'force': set(), 'target': set()}
    await update.message.reply_text("📝 **ধাপ ১:** পোস্টের ক্যাপশন পাঠান:")
    return POST_TITLE

async def p_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_DATA[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📸 **ধাপ ২:** এবার ফটো পাঠান:")
    return POST_PHOTO

async def p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_DATA[update.effective_user.id]['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("🔗 **ধাপ ৩:** ওয়েবসাইট লিঙ্ক পাঠান (বা 'skip' লিখুন):")
    return POST_WEBSITE

async def p_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    POST_DATA[update.effective_user.id]['link'] = WATCH_NOW_URL if text.lower() == 'skip' else text
    await update.message.reply_text("🛡️ **ধাপ ৪:** ফোর্স জয়েন চ্যানেলগুলো সিলেক্ট করুন:", reply_markup=get_selection_markup(POST_DATA[update.effective_user.id]['force'], "fsel"))
    return POST_FORCE_CHANS

async def p_force_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "fsel_done":
        await query.edit_message_text("📢 **ধাপ ৫:** কোন কোন চ্যানেলে পোস্ট করতে চান? সিলেক্ট করুন:", reply_markup=get_selection_markup(POST_DATA[uid]['target'], "tsel"))
        return POST_TARGET_CHANS
    cid = query.data.split("|")[1]
    if cid in POST_DATA[uid]['force']: POST_DATA[uid]['force'].remove(cid)
    else: POST_DATA[uid]['force'].add(cid)
    await query.edit_message_reply_markup(get_selection_markup(POST_DATA[uid]['force'], "fsel"))
    return POST_FORCE_CHANS

async def p_target_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "tsel_done":
        await query.message.reply_text("⚠️ নিশ্চিত? পোস্ট পাঠাতে ক্লিক করুন:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Confirm & Send", callback_data="post_confirm")], [InlineKeyboardButton("❌ Cancel", callback_data="post_cancel")]]))
        return POST_CONFIRM
    cid = query.data.split("|")[1]
    if cid in POST_DATA[uid]['target']: POST_DATA[uid]['target'].remove(cid)
    else: POST_DATA[uid]['target'].add(cid)
    await query.edit_message_reply_markup(get_selection_keyboard(POST_DATA[uid]['target'], "tsel"))
    return POST_TARGET_CHANS

async def p_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if query.data == "post_confirm":
        data = POST_DATA[uid]
        force_str = ",".join(data['force']) if data['force'] else "none"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now 🎬", callback_data=f"v|{force_str}|{data['link']}") ]])
        success = 0
        for t_cid in data['target']:
            try:
                await context.bot.send_photo(chat_id=t_cid, photo=data['photo'], caption=data['title'], reply_markup=btn, parse_mode=ParseMode.HTML)
                success += 1
            except: pass
        await query.message.reply_text(f"✅ সফল! {success}টি চ্যানেলে পাঠানো হয়েছে।")
    else:
        await query.message.reply_text("❌ বাতিল।")
    POST_DATA.pop(uid, None)
    return ConversationHandler.END

# ====================================================================
# 🎥 WATCH HANDLER & ADMIN TOOLS
# ====================================================================
async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    _, force_str, url = query.data.split("|", 2)
    db.add_user(uid)
    required_ids = [] if force_str == "none" else force_str.split(",")
    not_joined = await check_specific_subscription(uid, context.bot, required_ids)
    if not not_joined:
        try: await context.bot.send_message(uid, f"🚀 **Link:** {url}", parse_mode=ParseMode.HTML)
        except: await query.answer("❌ Please start the bot first!", show_alert=True)
    else:
        await query.answer("❌ জয়েন করেননি!", show_alert=True)
        btns = [[InlineKeyboardButton(f"Join {n}", url=l)] for _, n, l in not_joined]
        await context.bot.send_message(uid, "🚫 **ভিডিও দেখতে জয়েন করুন:**", reply_markup=InlineKeyboardMarkup(btns))

@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 মোট ইউজার: {db.get_total_users()}")

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ বাতিল।")
    return ConversationHandler.END

# ====================================================================
# 🚀 MAIN
# ====================================================================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="^check_status"))
    app.add_handler(CallbackQueryHandler(watch_callback, pattern="^v\|"))

    post_handler = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost_start)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, p_photo)],
            POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_website)],
            POST_FORCE_CHANS: [CallbackQueryHandler(p_force_cb, pattern="^fsel")],
            POST_TARGET_CHANS: [CallbackQueryHandler(p_target_cb, pattern="^tsel")],
            POST_CONFIRM: [CallbackQueryHandler(p_confirm, pattern="^post_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_op)]
    )
    app.add_handler(post_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
