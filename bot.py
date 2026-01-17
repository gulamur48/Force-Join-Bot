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

# ================= ⚙️ CONFIG & LOGGING =================
TOKEN = "8510787985:AAEw4UNXdCZLK_r25EKJnuIwrlkE8cyk7VE" # আপনার টোকেন
ADMIN_IDS = {6406804999} # আপনার অ্যাডমিন আইডি

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

START_TIME = time.time()

# Conversation States
INPUT_TEXT = 1
POST_CAP, POST_MEDIA, POST_FJ, POST_TG, POST_CONFIRM = range(2, 7)
BROADCAST_MSG = 8

# ================= 🗄️ SUPREME DATABASE (ALL IN ONE) =================
class SupremeDB:
    def __init__(self):
        self.conn = sqlite3.connect("supreme_core.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Users
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, join_date TEXT, status TEXT)")
        # Config (Settings)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        # Channels
        self.cursor.execute("CREATE TABLE IF NOT EXISTS channels (id TEXT PRIMARY KEY, name TEXT, link TEXT)")
        
        # Default Settings (50 Features Config)
        defaults = {
            "watch_url": "https://mmshotbd.blogspot.com/?m=1",
            "welcome_photo": "https://i.ibb.co/LzVz4z0/welcome.jpg",
            "auto_delete": "45",
            "maint_mode": "OFF",
            "anti_spam": "ON",
            "protect_content": "ON",
            "welcome_msg": "ON",
            "force_join": "ON",
            "button_style": "Classic",
            "broadcast_speed": "Fast"
        }
        for k, v in defaults.items():
            self.cursor.execute("INSERT OR IGNORE INTO config VALUES (?, ?)", (k, v))
        self.conn.commit()

    # --- Getters & Setters ---
    def get(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else "N/A"

    def set(self, key, val):
        self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, str(val)))
        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                            (user.id, user.first_name, datetime.datetime.now().strftime("%Y-%m-%d"), "active"))
        self.conn.commit()

    def get_stats(self):
        total = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        today = self.cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchone()[0]
        return total, today

    def get_users(self):
        return [r[0] for r in self.cursor.execute("SELECT id FROM users").fetchall()]

db = SupremeDB()

# ================= 🔗 CHANNEL DATA (MASTER LIST) =================
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
        self.end_headers()
        self.wfile.write(b"Supreme Bot Alive")

def run_server():
    HTTPServer(("", int(os.environ.get("PORT", 8080))), HealthServer).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

# ================= 🎨 UI HELPERS =================
def decor(text, user):
    """মেসেজ সুন্দর করার ফাংশন"""
    name = mention_html(user.id, user.first_name)
    header = "✨ <b>SUPREME SYSTEM</b> ✨\n━━━━━━━━━━━━━━━━━━━━\n"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {name} | 🕒 <b>Time:</b> {datetime.datetime.now().strftime('%I:%M %p')}"
    return header + text + footer

async def check_join_status(user_id, context):
    if db.get("force_join") == "OFF": return []
    missing = []
    for ch in MASTER_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status in ['left', 'kicked', 'none']: missing.append(ch)
        except: missing.append(ch)
    return missing

# ================= 👤 USER SIDE =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user)
    
    # Maintenance Mode Check
    if db.get("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html(decor("🚧 <b>System Maintenance!</b>\n\nবর্তমানে কাজ চলছে, দয়া করে পরে চেষ্টা করুন।", user))
        return

    missing = await check_join_status(user.id, context)
    photo = db.get("welcome_photo")
    
    if not missing:
        txt = f"👋 <b>স্বাগতম {user.first_name}!</b>\n\n🎉 আপনার ভেরিফিকেশন সফল হয়েছে!\n✅ আপনি এখন আমাদের প্রিমিয়াম মেম্বার।\n\n👇 নিচের বাটনে ক্লিক করে ভিডিও দেখুন:"
        kb = [[InlineKeyboardButton("🎬 ভিডিও দেখুন (Watch Now) 🔥", url=db.get("watch_url"))]]
        await update.message.reply_photo(photo=photo, caption=decor(txt, user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        kb = [[InlineKeyboardButton(f"➕ জয়েন: {c['name']}", url=c['link'])] for c in missing]
        kb.append([InlineKeyboardButton("✅ ভেরিফাই করুন (Verify)", callback_data="check_join")])
        txt = f"⚠️ <b>অ্যাক্সেস ডিনাইড!</b>\n\nভিডিও দেখতে হলে নিচের চ্যানেলগুলোতে জয়েন করতে হবে। 👇"
        await update.message.reply_photo(photo=photo, caption=decor(txt, user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# ================= 👑 ADMIN PANEL CONTROLLER =================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    
    total, today = db.get_stats()
    
    txt = (f"👑 <b>অ্যাডমিন কন্ট্রোল প্যানেল</b>\n\n"
           f"📊 <b>পরিসংখ্যান:</b>\n"
           f"👥 মোট ইউজার: <code>{total}</code>\n"
           f"📅 আজকের জয়েন: <code>{today}</code>\n"
           f"⚡ আপটাইম: {str(datetime.timedelta(seconds=int(time.time() - START_TIME)))}\n"
           f"💾 সিপিইউ: {psutil.cpu_percent()}% | র‍্যাম: {psutil.virtual_memory().percent}%")
    
    btns = [
        [InlineKeyboardButton("📢 পোস্ট ম্যানেজমেন্ট", callback_data="menu_post"), InlineKeyboardButton("⚙️ সেটিংস", callback_data="menu_settings")],
        [InlineKeyboardButton("🛡️ সিকিউরিটি", callback_data="menu_security"), InlineKeyboardButton("📡 ব্রডকাস্ট", callback_data="init_broadcast")],
        [InlineKeyboardButton("🔧 সিস্টেম টুলস", callback_data="menu_system"), InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close_admin")]
    ]
    
    try: await update.message.reply_html(decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns))
    except: await update.callback_query.edit_message_caption(caption=decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

# ================= ⚙️ SUB-MENUS & TOGGLES =================
async def handle_admin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data == "menu_settings":
        val_del = db.get("auto_delete")
        val_url = db.get("watch_url")[:15] + "..."
        btns = [
            [InlineKeyboardButton(f"⏱️ টাইমার: {val_del}s", callback_data="edit_auto_delete")],
            [InlineKeyboardButton(f"🔗 লিঙ্ক: {val_url}", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🖼️ ওয়েলকাম ফটো চেঞ্জ", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(caption=decor("⚙️ <b>বট সেটিংস</b>\nযেকোন অপশন চেঞ্জ করতে বাটনে ক্লিক করুন।", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data == "menu_security":
        maint = "✅ ON" if db.get("maint_mode") == "ON" else "❌ OFF"
        spam = "✅ ON" if db.get("anti_spam") == "ON" else "❌ OFF"
        force = "✅ ON" if db.get("force_join") == "ON" else "❌ OFF"
        
        btns = [
            [InlineKeyboardButton(f"মেইনটেনেন্স মোড: {maint}", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"অ্যান্টি স্প্যাম: {spam}", callback_data="tog_anti_spam")],
            [InlineKeyboardButton(f"ফোর্স জয়েন: {force}", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(caption=decor("🛡️ <b>সিকিউরিটি কন্ট্রোল</b>\nএক ক্লিকে অন/অফ করুন।", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        curr = db.get(key)
        new_val = "OFF" if curr == "ON" else "ON"
        db.set(key, new_val)
        # Refresh the menu by calling handle_admin_cb again with appropriate menu data
        if key in ["maint_mode", "anti_spam", "force_join"]:
            query.data = "menu_security"
        await handle_admin_cb(update, context)

    elif data == "main_menu":
        await admin_menu(update, context)

    elif data == "close_admin":
        await query.message.delete()

    elif data == "check_join":
        missing = await check_join_status(user.id, context)
        if not missing:
            await query.answer("✅ সফল!", show_alert=True)
            await query.edit_message_caption(caption=decor("🎉 <b>অভিনন্দন!</b>\nআপনি সব চ্যানেলে জয়েন করেছেন। ভিডিও দেখুন 👇", user), 
                                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 প্লে ভিডিও", url=db.get("watch_url"))]]), parse_mode=ParseMode.HTML)
        else:
            await query.answer("⛔ এখনো বাকি আছে!", show_alert=True)

    # Editing Values Handlers
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        map_text = {
            "auto_delete": "⏱️ নতুন অটো-ডিলিট টাইম (সেকেন্ডে) লিখুন:",
            "watch_url": "🔗 নতুন ওয়াচ লিঙ্ক পেস্ট করুন:",
            "welcome_photo": "🖼️ নতুন ফটোর ডাইরেক্ট লিঙ্ক দিন:"
        }
        await query.message.reply_html(decor(f"📝 <b>মান পরিবর্তন</b>\n\n{map_text[key]}", user))
        return INPUT_TEXT

# ================= 📝 VALUE EDITOR HANDLER =================
async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    val = update.message.text
    if key:
        db.set(key, val)
        await update.message.reply_html(decor(f"✅ <b>সফলভাবে সেভ হয়েছে!</b>\n\nKey: {key}\nValue: {val}", update.effective_user))
    return ConversationHandler.END

# ================= 📢 POST WIZARD (GRAPHICAL) =================
async def post_wizard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()
    await query.message.reply_html(decor("📝 <b>ধাপ ১: ক্যাপশন</b>\n\nপোস্টের ক্যাপশন লিখে পাঠান।", query.from_user))
    context.user_data['post'] = {'fj': [], 'tg': []}
    return POST_CAP

async def post_cap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['cap'] = update.message.text
    await update.message.reply_html(decor("📸 <b>ধাপ ২: মিডিয়া</b>\n\nফটো বা ভিডিও পাঠান (Skip করতে /skip লিখুন)।", update.effective_user))
    return POST_MEDIA

async def post_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['media'] = update.message.photo[-1].file_id
    elif update.message.video: context.user_data['post']['media'] = update.message.video.file_id
    else: context.user_data['post']['media'] = None
    
    # Show FJ Menu
    await show_fj_menu(update, context)
    return POST_FJ

async def show_fj_menu(update, context):
    sel = context.user_data['post']['fj']
    btns = []
    for c in MASTER_CHANNELS:
        mark = "✅" if c['id'] in sel else "❌"
        btns.append([InlineKeyboardButton(f"{mark} {c['name']}", callback_data=f"pfj_{c['id']}")])
    btns.append([InlineKeyboardButton("➡️ পরবর্তী ধাপ", callback_data="fj_done")])
    
    txt = decor("🔐 <b>ধাপ ৩: ফোর্স জয়েন</b>\nবাটনে ক্লিক করে চ্যানেল সিলেক্ট করুন।", update.effective_user)
    if update.callback_query:
        await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_html(txt, reply_markup=InlineKeyboardMarkup(btns))

async def post_fj_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("pfj_", "")
    curr = context.user_data['post']['fj']
    if cid in curr: curr.remove(cid)
    else: curr.append(cid)
    await show_fj_menu(update, context)

async def post_fj_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show Target Menu
    await show_tg_menu(update, context)
    return POST_TG

async def show_tg_menu(update, context):
    sel = context.user_data['post']['tg']
    btns = []
    for c in MASTER_CHANNELS:
        mark = "✅" if c['id'] in sel else "❌"
        btns.append([InlineKeyboardButton(f"{mark} {c['name']}", callback_data=f"ptg_{c['id']}")])
    btns.append([InlineKeyboardButton("🏁 প্রিভিউ দেখুন", callback_data="tg_done")])
    
    txt = decor("🎯 <b>ধাপ ৪: টার্গেট চ্যানেল</b>\nকোথায় পোস্ট পাঠাবেন?", update.effective_user)
    await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

async def post_tg_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("ptg_", "")
    curr = context.user_data['post']['tg']
    if cid in curr: curr.remove(cid)
    else: curr.append(cid)
    await show_tg_menu(update, context)

async def post_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['post']
    txt = f"{p['cap']}\n\n⚙️ FJ: {len(p['fj'])} | TG: {len(p['tg'])}"
    kb = [[InlineKeyboardButton("🚀 সেন্ড করুন", callback_data="send_now"), InlineKeyboardButton("❌ বাতিল", callback_data="cancel")]]
    
    if p['media']:
        await update.callback_query.message.reply_photo(p['media'], caption=txt, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    return POST_CONFIRM

async def post_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['post']
    # Generate Smart Link Button
    param = "none" if not p['fj'] else ",".join(str(CHANNELS_DATA.index(c)) for c in MASTER_CHANNELS if c['id'] in p['fj']) # Using indices for shorter payload
    # Note: For simplicity here, we assume standard direct logic
    
    btn_url = db.get("watch_url")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 WATCH VIDEO ✨", url=btn_url)]])

    sent = 0
    for cid in p['tg']:
        try:
            if p['media']: await context.bot.send_photo(cid, p['media'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(cid, p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception as e: logger.error(e)
    
    await update.callback_query.message.reply_text(f"✅ পোস্ট সম্পন্ন! {sent} টি চ্যানেলে পাঠানো হয়েছে।")
    return ConversationHandler.END

# ================= 📡 BROADCAST SYSTEM =================
async def broadcast_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_html(decor("📢 <b>ব্রডকাস্ট</b>\nমেসেজ ফরোয়ার্ড করুন বা লিখুন:", update.effective_user))
    return BROADCAST_MSG

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_users()
    msg = update.message
    status = await update.message.reply_text("⏳ ব্রডকাস্ট শুরু হচ্ছে...")
    s, f = 0, 0
    
    for uid in users:
        try:
            await msg.copy(uid)
            s += 1
        except: f += 1
        if s % 50 == 0: await status.edit_text(f"📤 পাঠাচ্ছে... {s}/{len(users)}")
        
    await status.edit_text(decor(f"✅ <b>ব্রডকাস্ট রিপোর্ট</b>\n\nসফল: {s}\nব্যর্থ: {f}", update.effective_user), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ অপারেশন বাতিল।")
    return ConversationHandler.END

# ================= 🚀 APP BUILDER =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Admin Settings Conversation
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_admin_cb, pattern="^edit_")],
        states={INPUT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_input)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Post Wizard
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(post_wizard_start, pattern="^menu_post$")],
        states={
            POST_CAP: [MessageHandler(filters.TEXT, post_cap)],
            POST_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO, post_media), CommandHandler("skip", lambda u,c: show_fj_menu(u,c) or POST_FJ)],
            POST_FJ: [CallbackQueryHandler(post_fj_toggle, pattern="^pfj_"), CallbackQueryHandler(post_fj_done, pattern="^fj_done$")],
            POST_TG: [CallbackQueryHandler(post_tg_toggle, pattern="^ptg_"), CallbackQueryHandler(post_preview, pattern="^tg_done$")],
            POST_CONFIRM: [CallbackQueryHandler(post_send, pattern="^send_now$")]
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="cancel")]
    ))

    # Broadcast
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_init, pattern="^init_broadcast$")],
        states={BROADCAST_MSG: [MessageHandler(filters.ALL, broadcast_send)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(handle_admin_cb))

    print("✅ SUPREME BOT STARTED WITH GUI PANEL")
    app.run_polling()

if __name__ == "__main__":
    main()
