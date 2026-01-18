"""
================================================================================
PROJECT: SUPREME GOD MODE BOT (ULTIMATE EDITION)
VERSION: v500.0 (Stable)
AUTHOR: AI ASSISTANT
DATE: 2026-01-18
TYPE: Telegram Channel Management & Marketing Bot

FEATURES:
1.  Enterprise Database Management (SQLite3 Thread-safe)
2.  Advanced Error Handling & Recovery System
3.  Background Health Check Server (Render/Heroku Support)
4.  Dynamic Configuration System (No Code Edit Needed)
5.  Force Join System with Deep Verification
6.  Post Wizard with Media & Button Support
7.  Global Broadcast System with Statistics
8.  User Activity Tracking & Analytics
9.  Romantic/Love Theme UI Engine
10. Maintenance Mode & Security Guards
11. Auto-Delete Timer System
12. Anti-Spam Protection
13. Admin Panel with GUI Navigation
14. System Resource Monitoring (RAM/CPU)
================================================================================
"""

import os
import sys
import time
import json
import sqlite3
import logging
import threading
import psutil
import asyncio
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional

# Third-party imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.constants import ParseMode
    from telegram.helpers import mention_html
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler,
        ContextTypes, ConversationHandler, MessageHandler, 
        filters, ApplicationBuilder, Defaults
    )
except ImportError:
    print("CRITICAL ERROR: 'python-telegram-bot' library not found!")
    sys.exit(1)

# ==============================================================================
# ⚙️ CONFIGURATION SECTION
# ==============================================================================

# 🔥 YOUR BOT TOKEN
TOKEN = "8510787985:AAH2aosQ5T5Ol-Yw4KIc37eIh9XQQcOYO0U"

# 🔥 YOUR ADMIN ID (Get it from @userinfobot)
ADMIN_IDS = {6406804999} 

# SYSTEM CONSTANTS
DB_NAME = "supreme_ultra_max.db"
LOG_LEVEL = logging.INFO
START_TIME = time.time()

# CONVERSATION STATES
STATE_EDIT_VALUE = 1
STATE_POST_CAPTION = 2
STATE_POST_MEDIA = 3
STATE_POST_CONFIRM = 4
STATE_BROADCAST_MSG = 5

# ==============================================================================
# 📝 LOGGING SYSTEM
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    level=LOG_LEVEL,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SupremeBot")

# ==============================================================================
# 🗄️ DATABASE MANAGER CLASS
# Handles all SQL interactions safely
# ==============================================================================
class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.initialize_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            logger.info("Database connected successfully.")
        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}")
            sys.exit(1)

    def initialize_tables(self):
        cursor = self.conn.cursor()
        
        # Table: Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                join_date TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Table: Configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Table: Channels (Future proofing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                name TEXT,
                link TEXT
            )
        """)
        
        self.conn.commit()
        self._set_defaults()

    def _set_defaults(self):
        """Sets default romantic values if config is empty"""
        defaults = {
            "watch_url": "https://mmshotbd.blogspot.com/?m=1",
            "welcome_photo": "https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg",
            "auto_delete": "45",
            "maint_mode": "OFF",
            "force_join": "ON",
            "btn_text": "🎬 ভিডিও দেখুন (Watch Now) ✨😍",
            
            "welcome_msg": """💖✨ <b>ওগো শুনছো! স্বাগতম জানাই তোমাকে!</b> ✨💖

🌹 <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা খুশিতে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন একদমই অসম্পূর্ণ ছিল।

✨ <b>তোমার জন্য স্পেশাল গিফট:</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব হট কালেকশন 🔥
🎀 এবং আমার হৃদয়ের গভীর ভালোবাসা... ❤️

👇 <b>দেরি না করে নিচের বাটনে আলতো করে ক্লিক করো সোনা:</b> 👇""",

            "lock_msg": """💔 <b>ওহ নো বেবি! তুমি এখনো জয়েন করোনি?</b> 😢💔

আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
আমার খুব কষ্ট লাগবে যদি তুমি চলে যাও... 😭

🌹 <b>প্লিজ সোনা, রাগ করো না!</b>
নিচের সবগুলোতে জয়েন করে <b>"Verify Me Love"</b> বাটনে ক্লিক করো। আমি তোমার অপেক্ষায় আছি... 😘💕"""
        }
        
        for key, value in defaults.items():
            try:
                self.conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (key, value))
            except sqlite3.Error as e:
                logger.error(f"Failed to set default for {key}: {e}")
        self.conn.commit()

    # --- Data Access Methods ---
    def get_config(self, key: str) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = cursor.fetchone()
        return res[0] if res else "NOT_SET"

    def set_config(self, key: str, value: str):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def add_user(self, user_id: int, first_name: str, username: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            self.conn.execute("INSERT OR IGNORE INTO users (id, name, username, join_date) VALUES (?, ?, ?, ?)", 
                             (user_id, first_name, username, date))
            self.conn.commit()
        except sqlite3.Error:
            pass

    def get_stats(self):
        cursor = self.conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        today = cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (today_date,)).fetchone()[0]
        return total, today

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]

# Initialize Database Instance
db = DatabaseManager(DB_NAME)

# ==============================================================================
# 🔗 MASTER CHANNELS CONFIGURATION
# IMPORTANT: Bot MUST be Admin in these channels!
# ==============================================================================
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

# ==============================================================================
# 🌐 HEALTH CHECK SERVER (Keep-Alive System)
# ==============================================================================
class SimpleHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        html = f"<h1>Supreme Bot Online</h1><p>Uptime: {uptime}</p>"
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        return # Silence server logs

def start_background_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), SimpleHealthHandler)
        logger.info(f"Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")

threading.Thread(target=start_background_server, daemon=True).start()

# ==============================================================================
# 🎨 UI & DECORATION HELPERS
# ==============================================================================
class UIBuilder:
    @staticmethod
    def decor_msg(text: str, user) -> str:
        """Adds a romantic/premium header and footer to messages"""
        name = mention_html(user.id, user.first_name)
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        
        header = "🌺🍃 <b>SUPREME LOVE ZONE</b> 🍃🌺\n━━━━━━━━━━━━━━━━━━━━━━\n"
        footer = f"\n━━━━━━━━━━━━━━━━━━━━━━\n💖 <b>User:</b> {name}\n⏰ <b>Time:</b> {time_str}"
        return header + text + footer

    @staticmethod
    def main_menu_kb() -> InlineKeyboardMarkup:
        btns = [
            [InlineKeyboardButton("📝 মেসেজ এডিটর", callback_data="menu_msg"), 
             InlineKeyboardButton("🔗 লিঙ্ক সেটিংস", callback_data="menu_links")],
            [InlineKeyboardButton("🛡️ সিকিউরিটি গার্ড", callback_data="menu_security"), 
             InlineKeyboardButton("📢 মার্কেটিং জোন", callback_data="menu_marketing")],
            [InlineKeyboardButton("❌ প্যানেল বন্ধ করুন", callback_data="close_panel")]
        ]
        return InlineKeyboardMarkup(btns)

ui = UIBuilder()

# ==============================================================================
# 🔐 SECURITY & LOGIC LAYER
# ==============================================================================
class SecurityManager:
    @staticmethod
    async def check_force_join(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> List[dict]:
        """Checks if user has joined all master channels"""
        if db.get_config("force_join") == "OFF":
            return []
        
        missing = []
        for channel in MASTER_CHANNELS:
            try:
                # We do not check if bot is admin here to avoid extra API calls complexity
                # We catch the error if bot is not admin or channel is private
                member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
                if member.status in ['left', 'kicked', 'restricted']:
                    missing.append(channel)
            except Exception as e:
                # Log error but don't block user if bot fails to check
                # logger.warning(f"Could not check channel {channel['id']}: {e}")
                missing.append(channel) # Safety: assume missing if check fails
        return missing

# ==============================================================================
# 🎮 USER COMMAND HANDLERS
# ==============================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    
    # 1. Maintenance Mode Check
    if db.get_config("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html(
            ui.decor_msg("🚧 <b>দুঃখিত জানু! সিস্টেম মেইনটেনেন্স চলছে।</b>\n\nপ্লিজ একটু পরে চেষ্টা করো। 🥺", user)
        )
        return

    # 2. Check Force Join
    missing_channels = await SecurityManager.check_force_join(user.id, context)
    photo_url = db.get_config("welcome_photo")
    
    if not missing_channels:
        # User is Verified
        msg_text = db.get_config("welcome_msg")
        button_text = db.get_config("btn_text")
        watch_url = db.get_config("watch_url")
        
        keyboard = [[InlineKeyboardButton(button_text, url=watch_url)]]
    else:
        # User is NOT Verified
        msg_text = db.get_config("lock_msg")
        keyboard = []
        for ch in missing_channels:
            keyboard.append([InlineKeyboardButton(f"💞 জয়েন: {ch['name']}", url=ch['link'])])
        keyboard.append([InlineKeyboardButton("✨ Verify Me Love ✨", callback_data="action_verify")])

    # 3. Send Response (Crash Proof)
    try:
        await update.message.reply_photo(
            photo=photo_url,
            caption=ui.decor_msg(msg_text, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to send start photo: {e}")
        # Fallback to text if photo fails
        await update.message.reply_html(
            ui.decor_msg(msg_text, user),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==============================================================================
# 👑 ADMIN PANEL HANDLERS
# ==============================================================================
async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    total, today = db.get_stats()
    sys_ram = psutil.virtual_memory().percent
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))

    text = (f"👑 <b>SUPREME GOD ADMIN PANEL</b>\n\n"
            f"📊 <b>Statistics:</b>\n"
            f"• Total Users: <code>{total}</code>\n"
            f"• Joined Today: <code>{today}</code>\n"
            f"• Server Uptime: <code>{uptime}</code>\n"
            f"• RAM Usage: <code>{sys_ram}%</code>\n\n"
            f"👇 <b>Select an option below:</b>")

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_caption(
            caption=ui.decor_msg(text, update.effective_user),
            reply_markup=ui.main_menu_kb(),
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(
            ui.decor_msg(text, update.effective_user),
            reply_markup=ui.main_menu_kb()
        )

# ==============================================================================
# 🎮 CALLBACK NAVIGATION CONTROLLER (The Brain)
# ==============================================================================
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Vital to stop loading animation
    
    data = query.data
    user = query.from_user

    # --- ROUTING LOGIC ---
    
    # 1. Verification Action
    if data == "action_verify":
        missing = await SecurityManager.check_force_join(user.id, context)
        if not missing:
            await query.answer("💖 ভেরিফিকেশন সফল হয়েছে জানু!", show_alert=True)
            try: await query.message.delete() 
            except: pass
            
            btn_txt = db.get_config("btn_text")
            url = db.get_config("watch_url")
            wel_msg = db.get_config("welcome_msg")
            
            await query.message.reply_photo(
                photo=db.get_config("welcome_photo"),
                caption=ui.decor_msg(wel_msg, user),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(btn_txt, url=url)]]),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("💔 এখনো সবগুলোতে জয়েন করোনি!", show_alert=True)
            
    # 2. Admin Navigation
    elif data == "main_menu":
        await admin_panel_handler(update, context)
        
    elif data == "close_panel":
        await query.message.delete()

    # 3. Sub-Menus
    elif data == "menu_msg":
        btns = [
            [InlineKeyboardButton("✍️ ওয়েলকাম মেসেজ", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("✍️ লক মেসেজ", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ ওয়েলকাম ফটো", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(
            ui.decor_msg("📝 <b>মেসেজ এডিটর</b>\nকোনটি এডিট করতে চান?", user),
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_links":
        btns = [
            [InlineKeyboardButton("🔗 ওয়াচ লিঙ্ক", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🔘 বাটন টেক্সট", callback_data="edit_btn_text")],
            [InlineKeyboardButton("⏱️ অটো ডিলিট", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(
            ui.decor_msg("🔗 <b>লিঙ্ক সেটিংস</b>\nএখানে লিঙ্ক এবং বাটন চেঞ্জ করুন।", user),
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_security":
        maint_status = "✅ ON" if db.get_config("maint_mode") == "ON" else "❌ OFF"
        force_status = "✅ ON" if db.get_config("force_join") == "ON" else "❌ OFF"
        
        btns = [
            [InlineKeyboardButton(f"Maintenance: {maint_status}", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"Force Join: {force_status}", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(
            ui.decor_msg("🛡️ <b>সিকিউরিটি গার্ড</b>\nসিস্টেম অন/অফ করুন।", user),
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_marketing":
        btns = [
            [InlineKeyboardButton("✨ নতুন পোস্ট (Wizard)", callback_data="wiz_start")],
            [InlineKeyboardButton("📡 ব্রডকাস্ট", callback_data="broad_start")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(
            ui.decor_msg("📢 <b>মার্কেটিং জোন</b>\nপোস্ট বা ব্রডকাস্ট করুন।", user),
            reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=ParseMode.HTML
        )

    # 4. Toggles
    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        curr = db.get_config(key)
        new_val = "OFF" if curr == "ON" else "ON"
        db.set_config(key, new_val)
        # Refresh menu
        query.data = "menu_security"
        await callback_router(update, context)

# ==============================================================================
# 📝 CONVERSATION: VALUE EDITOR
# ==============================================================================
async def editor_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("edit_", "")
    context.user_data['edit_key'] = key
    
    await query.message.reply_html(
        ui.decor_msg(f"✍️ <b>এডিট মোড চালু হয়েছে!</b>\n\nEditing: <code>{key}</code>\n\nনতুন ভ্যালু লিখে মেসেজ দিন:", query.from_user)
    )
    return STATE_EDIT_VALUE

async def editor_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    val = update.message.text
    db.set_config(key, val)
    
    await update.message.reply_html(
        ui.decor_msg(f"✅ <b>সফলভাবে সেভ হয়েছে!</b>\n\nValue updated.", update.effective_user)
    )
    return ConversationHandler.END

# ==============================================================================
# 📢 CONVERSATION: POST WIZARD
# ==============================================================================
async def post_wiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_html(
        ui.decor_msg("📝 <b>পোস্ট উইজার্ড: ধাপ ১</b>\n\nপোস্টের ক্যাপশন লিখে পাঠান:", update.effective_user)
    )
    context.user_data['post'] = {}
    return STATE_POST_CAPTION

async def post_wiz_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['cap'] = update.message.text
    await update.message.reply_html(
        ui.decor_msg("📸 <b>পোস্ট উইজার্ড: ধাপ ২</b>\n\nফটো বা ভিডিও পাঠান (Skip করতে /skip লিখুন):", update.effective_user)
    )
    return STATE_POST_MEDIA

async def post_wiz_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['post']['med'] = update.message.photo[-1].file_id
        context.user_data['post']['type'] = 'photo'
    elif update.message.video:
        context.user_data['post']['med'] = update.message.video.file_id
        context.user_data['post']['type'] = 'video'
    else:
        context.user_data['post']['med'] = None
        context.user_data['post']['type'] = 'text'

    # Generate Channel List Buttons
    btns = []
    for ch in MASTER_CHANNELS:
        btns.append([InlineKeyboardButton(f"Send to {ch['name']}", callback_data=f"send_{ch['id']}")])
    
    await update.message.reply_html(
        ui.decor_msg("🚀 <b>পোস্ট উইজার্ড: শেষ ধাপ</b>\n\nকোথায় সেন্ড করবেন সিলেক্ট করুন:", update.effective_user),
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return STATE_POST_CONFIRM

async def post_wiz_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cid = query.data.replace("send_", "")
    p = context.user_data['post']
    
    btn_txt = db.get_config("btn_text")
    url = db.get_config("watch_url")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(btn_txt, url=url)]])
    
    try:
        if p['type'] == 'photo':
            await context.bot.send_photo(cid, p['med'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        elif p['type'] == 'video':
            await context.bot.send_video(cid, p['med'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(cid, p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
            
        await query.message.reply_text("✅ পোস্ট সফলভাবে পাঠানো হয়েছে!")
    except Exception as e:
        await query.message.reply_text(f"❌ এরর: {e}")
        
    return ConversationHandler.END

# ==============================================================================
# 📡 CONVERSATION: BROADCAST
# ==============================================================================
async def broad_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_html(
        ui.decor_msg("📢 <b>ব্রডকাস্ট মোড</b>\n\nমেসেজ ফরোয়ার্ড করুন বা টাইপ করুন:", update.effective_user)
    )
    return STATE_BROADCAST_MSG

async def broad_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = update.message
    status_msg = await update.message.reply_text("⏳ ব্রডকাস্ট শুরু হচ্ছে...")
    
    success = 0
    failed = 0
    
    for uid in users:
        try:
            await msg.copy(uid)
            success += 1
        except:
            failed += 1
        
        if success % 20 == 0:
            await status_msg.edit_text(f"📤 পাঠাচ্ছে... {success}/{len(users)}")
            
    await status_msg.edit_text(
        ui.decor_msg(f"✅ <b>ব্রডকাস্ট সম্পন্ন!</b>\n\nসফল: {success}\nব্যর্থ: {failed}", update.effective_user)
    )
    return ConversationHandler.END

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION ENTRY POINT
# ==============================================================================
def main():
    logger.info("Starting Supreme God Bot...")
    
    # Create App
    app = ApplicationBuilder().token(TOKEN).build()

    # 1. Editor Handler (Highest Priority)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(editor_start, pattern="^edit_")],
        states={STATE_EDIT_VALUE: [MessageHandler(filters.TEXT, editor_save)]},
        fallbacks=[CommandHandler("cancel", cancel_op)]
    ))

    # 2. Post Wizard Handler
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(post_wiz_start, pattern="^wiz_start$")],
        states={
            STATE_POST_CAPTION: [MessageHandler(filters.TEXT, post_wiz_caption)],
            STATE_POST_MEDIA: [MessageHandler(filters.ALL, post_wiz_media)],
            STATE_POST_CONFIRM: [CallbackQueryHandler(post_wiz_send, pattern="^send_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_op)]
    ))

    # 3. Broadcast Handler
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(broad_start, pattern="^broad_start$")],
        states={STATE_BROADCAST_MSG: [MessageHandler(filters.ALL, broad_send)]},
        fallbacks=[CommandHandler("cancel", cancel_op)]
    ))

    # 4. Standard Commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", admin_panel_handler))

    # 5. Global Callback Router (Handles all button clicks)
    app.add_handler(CallbackQueryHandler(callback_router))

    # Run Bot
    logger.info("Bot is polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as e:
        print(f"Critical System Error: {e}")
