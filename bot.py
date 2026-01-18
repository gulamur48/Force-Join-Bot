import os
import sys
import time
import sqlite3
import asyncio
import logging
import threading
import psutil
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, 
    filters, ApplicationBuilder
)

# ================= 🔧 CONFIGURATION =================
TOKEN = "8510787985:AAEw4UNXdCZLK_r25EKJnuIwrlkE8cyk7VE"
ADMIN_IDS = {6406804999}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
START_TIME = time.time()

# States
INPUT_TEXT = 1
POST_CAP, POST_MEDIA, POST_FJ, POST_TG, POST_CONFIRM = range(2, 7)
BROADCAST_MSG = 8

# ================= 🗄️ DATABASE =================
class SupremeDB:
    def __init__(self):
        self.conn = sqlite3.connect("supreme_love_fixed.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, join_date TEXT, status TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        
        defaults = {
            "watch_url": "https://mmshotbd.blogspot.com/?m=1",
            "welcome_photo": "https://cdn.pixabay.com/photo/2016/02/13/12/26/aurora-1197753_1280.jpg",
            "auto_delete": "45",
            "maint_mode": "OFF",
            "force_join": "ON",
            "welcome_msg": "💖✨ <b>স্বাগতম জানু!</b> ✨💖\n\nনিচের বাটনে ক্লিক করে ভিডিও দেখো। 👇",
            "lock_msg": "💔 <b>ওহ নো! জয়েন করোনি?</b> 😢\n\nপ্লিজ সোনা, নিচের চ্যানেলগুলোতে জয়েন করো! 👇",
            "btn_text": "🎬 ভিডিও দেখুন (Watch Now) ✨"
        }
        for k, v in defaults.items():
            self.cursor.execute("INSERT OR IGNORE INTO config VALUES (?, ?)", (k, v))
        self.conn.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else "Not Set"

    def set(self, key, val):
        self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, str(val)))
        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                            (user.id, user.first_name, datetime.datetime.now().strftime("%Y-%m-%d"), "active"))
        self.conn.commit()

    def get_stats(self):
        try:
            total = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            today = self.cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchone()[0]
            return total, today
        except: return 0, 0

    def get_users(self):
        return [r[0] for r in self.cursor.execute("SELECT id FROM users").fetchall()]

db = SupremeDB()

# ================= 🔗 MASTER CHANNELS =================
MASTER_CHANNELS = [
    {"id": "@virallink259", "name": "Viral Link 2026 🔥", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Premium Apps 💎", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "BD Beauty 🍑", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "FB Insta Links 🔗", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "Movie Time 🎬", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS Video 🔞", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "Deshi Bhabi 🔥", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "Kochi Meye 🎀", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "Request Zone 📥", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral BD 🌍", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "AI Studio 🎨", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= 🌐 HEALTH SERVER =================
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.wfile.write(b"Bot Active")

def run_server():
    try: HTTPServer(("", int(os.environ.get("PORT", 8080))), HealthServer).serve_forever()
    except: pass
threading.Thread(target=run_server, daemon=True).start()

# ================= 🎨 DECORATOR =================
def decor(text, user):
    name = mention_html(user.id, user.first_name)
    return f"🌺🍃 <b>SUPREME LOVE ZONE</b> 🍃🌺\n━━━━━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {name}"

async def check_join_status(user_id, context):
    if db.get("force_join") == "OFF": return []
    missing = []
    for ch in MASTER_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status in ['left', 'kicked', 'restricted']: missing.append(ch)
        except: missing.append(ch)
    return missing

# ================= 👤 START & USER =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user)
    
    if db.get("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html("🚧 <b>System Maintenance!</b>")
        return

    missing = await check_join_status(user.id, context)
    photo_url = db.get("welcome_photo")
    
    if not missing:
        txt = db.get("welcome_msg")
        kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
    else:
        txt = db.get("lock_msg")
        kb = [[InlineKeyboardButton(f"💞 জয়েন: {c['name']}", url=c['link'])] for c in missing]
        kb.append([InlineKeyboardButton("✨ Verify Me Love ✨", callback_data="check_join")])

    try:
        await update.message.reply_photo(photo=photo_url, caption=decor(txt, user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_html(decor(txt, user), reply_markup=InlineKeyboardMarkup(kb))

# ================= 👑 ADMIN PANEL & NAVIGATION =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    
    total, today = db.get_stats()
    txt = (f"👑 <b>ADMIN PANEL</b>\n\n📊 Total Users: {total}\n📅 Today: {today}\n⚡ Uptime: {str(datetime.timedelta(seconds=int(time.time() - START_TIME)))}")
    
    btns = [
        [InlineKeyboardButton("📝 লাভ মেসেজ এডিটর", callback_data="menu_msg"), InlineKeyboardButton("🔗 লিঙ্ক সেটিংস", callback_data="menu_links")],
        [InlineKeyboardButton("🛡️ সিকিউরিটি গার্ড", callback_data="menu_security"), InlineKeyboardButton("📢 পোস্ট & ব্রডকাস্ট", callback_data="menu_post")],
        [InlineKeyboardButton("❌ প্যানেল বন্ধ করুন", callback_data="close_admin")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_caption(decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_html(decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns))

# ================= 🎮 BUTTON HANDLER (NAVIGATION) =================
async def navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # এই লাইনটি খুব জরুরি - এটি লোডিং অ্যানিমেশন বন্ধ করে
    await query.answer()
    
    data = query.data
    user = query.from_user

    if data == "menu_msg":
        btns = [
            [InlineKeyboardButton("✍️ ওয়েলকাম মেসেজ", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("✍️ লক মেসেজ", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ ওয়েলকাম ফটো", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📝 <b>মেসেজ এডিটর</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_links":
        btns = [
            [InlineKeyboardButton("🔗 ওয়াচ লিঙ্ক", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🔘 বাটন টেক্সট", callback_data="edit_btn_text")],
            [InlineKeyboardButton("⏱️ টাইমার", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("🔗 <b>লিঙ্ক সেটিংস</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_security":
        maint = "✅ ON" if db.get("maint_mode") == "ON" else "❌ OFF"
        force = "✅ ON" if db.get("force_join") == "ON" else "❌ OFF"
        btns = [
            [InlineKeyboardButton(f"Maintenance: {maint}", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"Force Join: {force}", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("🛡️ <b>সিকিউরিটি</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_post":
        btns = [
            [InlineKeyboardButton("✨ নতুন পোস্ট (Wizard)", callback_data="wiz_start")],
            [InlineKeyboardButton("📡 ব্রডকাস্ট", callback_data="broadcast_init")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📢 <b>মার্কেটিং</b>", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "main_menu":
        await admin_panel(update, context)

    elif data == "close_admin":
        await query.message.delete()

    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        db.set(key, "OFF" if db.get(key) == "ON" else "ON")
        # রিফ্রেশ করার জন্য আবার ওই মেনুতে পাঠানো হচ্ছে
        if key in ["maint_mode", "force_join"]:
            # Manually trigger menu_security logic to refresh
            query.data = "menu_security"
            await navigation_handler(update, context)

    elif data == "check_join":
        missing = await check_join_status(user.id, context)
        if not missing:
            await query.answer("✅ সফল!", show_alert=True)
            try: await query.message.delete()
            except: pass
            kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
            await query.message.reply_photo(photo=db.get("welcome_photo"), caption=decor(db.get("welcome_msg"), user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ জয়েন করেননি!", show_alert=True)

# ================= 📝 EDITORS & WIZARDS =================
async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("edit_", "")
    context.user_data['edit_key'] = key
    await query.message.reply_html(decor(f"✍️ <b>নতুন ভ্যালু দিন:</b>\nKey: {key}", query.from_user))
    return INPUT_TEXT

async def edit_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    db.set(key, update.message.text)
    await update.message.reply_html("✅ <b>Saved Successfully!</b>")
    return ConversationHandler.END

# Post Wizard Handlers
async def wiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_html("📝 <b>Step 1:</b> ক্যাপশন দিন:")
    context.user_data['post'] = {}
    return POST_CAP

async def wiz_cap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['cap'] = update.message.text
    await update.message.reply_html("📸 <b>Step 2:</b> ফটো/ভিডিও দিন (বা /skip):")
    return POST_MEDIA

async def wiz_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['med'] = update.message.photo[-1].file_id
    elif update.message.video: context.user_data['post']['med'] = update.message.video.file_id
    else: context.user_data['post']['med'] = None
    
    btns = [[InlineKeyboardButton(c['name'], callback_data=f"send_{c['id']}")] for c in MASTER_CHANNELS]
    await update.message.reply_html("🚀 <b>Send To:</b>", reply_markup=InlineKeyboardMarkup(btns))
    return POST_CONFIRM

async def wiz_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("send_", "")
    p = context.user_data['post']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]])
    try:
        if p['med']: await context.bot.send_photo(cid, p['med'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        else: await context.bot.send_message(cid, p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        await update.callback_query.message.reply_text("✅ Sent!")
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ Error: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ================= 🚀 MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # 1. Editor Conversation (Must be before general handler)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_start, pattern="^edit_")],
        states={INPUT_TEXT: [MessageHandler(filters.TEXT, edit_save)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # 2. Post Wizard
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wiz_start, pattern="^wiz_start$")],
        states={
            POST_CAP: [MessageHandler(filters.TEXT, wiz_cap)],
            POST_MEDIA: [MessageHandler(filters.ALL, wiz_media)],
            POST_CONFIRM: [CallbackQueryHandler(wiz_send, pattern="^send_")]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # 3. Broadcast (Optional, simplified)
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.reply_text("Coming Soon!"), pattern="^broadcast_"))

    # 4. Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    # 5. General Navigation Handler (The Fix for your buttons)
    # This catches ALL other buttons like menu_msg, main_menu, close_admin
    app.add_handler(CallbackQueryHandler(navigation_handler))

    print("✅ BOT STARTED - BUTTONS FIXED")
    app.run_polling()

if __name__ == "__main__":
    main()
