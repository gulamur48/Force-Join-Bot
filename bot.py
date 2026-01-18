"""
================================================================================
PROJECT: SUPREME GOD MODE BOT (ULTIMATE EDITION) - FIXED VERSION
VERSION: v500.1 (Stable)
AUTHOR: AI ASSISTANT
DATE: 2026-01-18
TYPE: Telegram Channel Management & Marketing Bot
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
from typing import List, Dict, Union, Optional, Set
import traceback

# Third-party imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
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

TOKEN = "8510787985:AAH2aosQ5T5Ol-Yw4KIc37eIh9XQQcOYO0U"
ADMIN_IDS = {6406804999}
DB_NAME = "supreme_ultra_max.db"
LOG_LEVEL = logging.INFO
START_TIME = time.time()

# Conversation States
STATE_EDIT_VALUE = 1
STATE_POST_CAPTION = 2
STATE_POST_MEDIA = 3
STATE_POST_BUTTONS = 4
STATE_POST_CONFIRM = 5
STATE_BROADCAST_MSG = 6
STATE_ADD_CHANNEL_ID = 7
STATE_ADD_CHANNEL_NAME = 8
STATE_ADD_CHANNEL_LINK = 9

# ==============================================================================
# 📝 LOGGING SYSTEM
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_logs.txt')
    ]
)
logger = logging.getLogger("SupremeBot")

# ==============================================================================
# 🗄️ ENHANCED DATABASE MANAGER
# ==============================================================================
class EnhancedDatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.lock = threading.Lock()
        self.connect()
        self.initialize_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            logger.info("Database connected successfully.")
        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}")
            sys.exit(1)

    def initialize_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                join_date TEXT,
                last_active TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                added_date TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Posts history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                post_type TEXT,
                sent_date TEXT,
                status TEXT
            )
        """)
        
        self.conn.commit()
        self._set_defaults()

    def _set_defaults(self):
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
        
        with self.lock:
            for key, value in defaults.items():
                try:
                    self.conn.execute(
                        "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                        (key, value)
                    )
                except sqlite3.Error as e:
                    logger.error(f"Failed to set default for {key}: {e}")
            self.conn.commit()

    # === Configuration Methods ===
    def get_config(self, key: str) -> str:
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key=?", (key,))
            res = cursor.fetchone()
            return res[0] if res else ""

    def set_config(self, key: str, value: str):
        with self.lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            self.conn.commit()

    # === User Management ===
    def add_user(self, user_id: int, first_name: str, username: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, first_name, username, join_date, last_active) 
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, first_name, username, now, now))
                self.conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Failed to add user {user_id}: {e}")

    def update_user_activity(self, user_id: int):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            try:
                self.conn.execute(
                    "UPDATE users SET last_active = ? WHERE user_id = ?",
                    (now, user_id)
                )
                self.conn.commit()
            except sqlite3.Error:
                pass

    # === Statistics ===
    def get_stats(self):
        with self.lock:
            cursor = self.conn.cursor()
            total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")
            today = cursor.execute(
                "SELECT COUNT(*) FROM users WHERE date(join_date) = date(?)",
                (today_date,)
            ).fetchone()[0]
            return total, today

    def get_all_users(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]

    # === Channel Management ===
    def get_all_channels(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, link FROM channels WHERE status='active'")
            return cursor.fetchall()

    def add_channel(self, channel_id: str, name: str, link: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            try:
                self.conn.execute(
                    "INSERT OR REPLACE INTO channels (id, name, link, added_date) VALUES (?, ?, ?, ?)",
                    (channel_id, name, link, now)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f"Failed to add channel: {e}")
                return False

    def remove_channel(self, channel_id: str):
        with self.lock:
            try:
                self.conn.execute(
                    "UPDATE channels SET status='inactive' WHERE id=?",
                    (channel_id,)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f"Failed to remove channel: {e}")
                return False

# Initialize Database
db = EnhancedDatabaseManager(DB_NAME)

# ==============================================================================
# 🌐 HEALTH CHECK SERVER
# ==============================================================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
            response = {
                "status": "online",
                "uptime": uptime,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.debug(f"HTTP {args[0]} {args[1]}")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Health server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server failed: {e}")

health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# ==============================================================================
# 🎨 UI BUILDER CLASS
# ==============================================================================
class UIBuilder:
    @staticmethod
    def decor_msg(text: str, user=None) -> str:
        """Adds header and footer to messages"""
        if user:
            name = mention_html(user.id, user.first_name)
        else:
            name = "System"
        
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        date_str = datetime.datetime.now().strftime('%d %B, %Y')
        
        header = "🌺🍃 <b>SUPREME GOD MODE</b> 🍃🌺\n" + "━"*35 + "\n"
        footer = f"\n" + "━"*35 + f"\n👤 <b>User:</b> {name}\n📅 <b>Date:</b> {date_str}\n⏰ <b>Time:</b> {time_str}"
        
        return header + text + footer

    @staticmethod
    def main_menu_kb() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📝 Message Editor", callback_data="menu_msg")],
            [InlineKeyboardButton("🔗 Link Settings", callback_data="menu_links")],
            [InlineKeyboardButton("📢 Channel Manager", callback_data="menu_channels")],
            [InlineKeyboardButton("🛡️ Security Guard", callback_data="menu_security")],
            [InlineKeyboardButton("📡 Marketing Zone", callback_data="menu_marketing")],
            [InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")],
            [InlineKeyboardButton("❌ Close Panel", callback_data="close_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_main_kb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")]])

ui = UIBuilder()

# ==============================================================================
# 🔐 SECURITY MANAGER
# ==============================================================================
class SecurityManager:
    @staticmethod
    async def check_membership(user_id: int, bot) -> List[Dict]:
        """Check if user is member of required channels"""
        if db.get_config("force_join") != "ON":
            return []
        
        missing = []
        channels = db.get_all_channels()
        
        for channel_id, name, link in channels:
            try:
                # Handle both username and ID formats
                if isinstance(channel_id, str) and channel_id.startswith('@'):
                    chat_id = channel_id
                else:
                    chat_id = int(channel_id)
                
                member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    missing.append({
                        "id": channel_id,
                        "name": name,
                        "link": link
                    })
            except Exception as e:
                logger.warning(f"Failed to check channel {channel_id}: {e}")
                # If we can't check, assume user is not member
                missing.append({
                    "id": channel_id,
                    "name": name,
                    "link": link
                })
        
        return missing

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    db.update_user_activity(user.id)
    
    # Check maintenance mode
    if db.get_config("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html(
            ui.decor_msg("🚧 <b>System Under Maintenance!</b>\n\nPlease try again later.", user)
        )
        return
    
    # Check channel membership
    missing = await SecurityManager.check_membership(user.id, context.bot)
    
    if missing:
        # User hasn't joined all channels
        lock_msg = db.get_config("lock_msg")
        keyboard = []
        
        for channel in missing:
            keyboard.append([
                InlineKeyboardButton(
                    f"📢 Join: {channel['name']}",
                    url=channel['link']
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("✅ Verify Membership", callback_data="verify_membership")
        ])
        
        await update.message.reply_photo(
            photo=db.get_config("welcome_photo"),
            caption=ui.decor_msg(lock_msg, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    else:
        # User has joined all channels
        welcome_msg = db.get_config("welcome_msg")
        button_text = db.get_config("btn_text")
        watch_url = db.get_config("watch_url")
        
        keyboard = [[
            InlineKeyboardButton(button_text, url=watch_url)
        ]]
        
        await update.message.reply_photo(
            photo=db.get_config("welcome_photo"),
            caption=ui.decor_msg(welcome_msg, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - Admin Panel"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Access Denied!")
        return
    
    db.update_user_activity(user.id)
    await show_admin_panel(update, context)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False):
    """Display admin panel with statistics"""
    user = update.effective_user
    
    # Get statistics
    total_users, today_users = db.get_stats()
    sys_ram = psutil.virtual_memory().percent
    sys_cpu = psutil.cpu_percent(interval=1)
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    
    # Get channel count
    channels = db.get_all_channels()
    channel_count = len(channels)
    
    panel_text = (
        "👑 <b>SUPREME GOD ADMIN PANEL</b>\n\n"
        "📊 <b>System Statistics:</b>\n"
        f"• Total Users: <code>{total_users}</code>\n"
        f"• Today's Users: <code>{today_users}</code>\n"
        f"• Channels: <code>{channel_count}</code>\n"
        f"• Uptime: <code>{uptime}</code>\n"
        f"• RAM Usage: <code>{sys_ram}%</code>\n"
        f"• CPU Usage: <code>{sys_cpu}%</code>\n\n"
        "👇 <b>Select an option:</b>"
    )
    
    if is_callback:
        await update.callback_query.edit_message_text(
            ui.decor_msg(panel_text, user),
            reply_markup=ui.main_menu_kb(),
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(
            ui.decor_msg(panel_text, user),
            reply_markup=ui.main_menu_kb()
        )

# ==============================================================================
# 🔄 CALLBACK QUERY HANDLER
# ==============================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    # Update user activity
    db.update_user_activity(user.id)
    
    # Admin check for admin functions
    admin_only_actions = {
        'menu_msg', 'menu_links', 'menu_channels', 'menu_security',
        'menu_marketing', 'menu_stats', 'main_menu', 'edit_', 'tog_',
        'broad_start', 'wiz_start', 'add_channel', 'remove_channel_'
    }
    
    if any(data.startswith(prefix) for prefix in admin_only_actions) and user.id not in ADMIN_IDS:
        await query.message.reply_text("⛔ Admin access required!")
        return
    
    # Route callback actions
    if data == "main_menu":
        await show_admin_panel(update, context, is_callback=True)
    
    elif data == "close_panel":
        await query.delete_message()
    
    elif data == "verify_membership":
        missing = await SecurityManager.check_membership(user.id, context.bot)
        
        if not missing:
            await query.answer("✅ Verified! Access granted.", show_alert=True)
            
            # Send welcome message
            welcome_msg = db.get_config("welcome_msg")
            button_text = db.get_config("btn_text")
            watch_url = db.get_config("watch_url")
            
            keyboard = [[
                InlineKeyboardButton(button_text, url=watch_url)
            ]]
            
            try:
                await query.message.delete()
            except:
                pass
            
            await query.message.reply_photo(
                photo=db.get_config("welcome_photo"),
                caption=ui.decor_msg(welcome_msg, user),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("❌ Still missing channels!", show_alert=True)
    
    elif data == "menu_msg":
        keyboard = [
            [InlineKeyboardButton("✏️ Welcome Message", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("✏️ Lock Message", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ Welcome Photo URL", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            ui.decor_msg("📝 <b>Message Editor</b>\nSelect what to edit:", user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_links":
        current_btn = db.get_config("btn_text")
        current_url = db.get_config("watch_url")
        current_delete = db.get_config("auto_delete")
        
        text = (
            f"🔗 <b>Link Settings</b>\n\n"
            f"Current Settings:\n"
            f"• Button Text: <code>{current_btn}</code>\n"
            f"• Watch URL: <code>{current_url}</code>\n"
            f"• Auto Delete: <code>{current_delete} seconds</code>\n\n"
            f"Select what to edit:"
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Button Text", callback_data="edit_btn_text")],
            [InlineKeyboardButton("🔗 Watch URL", callback_data="edit_watch_url")],
            [InlineKeyboardButton("⏱️ Auto Delete Time", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            ui.decor_msg(text, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_channels":
        channels = db.get_all_channels()
        
        if not channels:
            text = "📢 <b>Channel Manager</b>\n\nNo channels added yet."
            keyboard = [
                [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ]
        else:
            text = "📢 <b>Channel Manager</b>\n\nCurrent Channels:\n"
            for idx, (ch_id, name, link) in enumerate(channels, 1):
                text += f"{idx}. {name}\n"
            
            keyboard = []
            for ch_id, name, _ in channels:
                keyboard.append([
                    InlineKeyboardButton(f"❌ Remove {name}", callback_data=f"remove_channel_{ch_id}")
                ])
            
            keyboard.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        await query.edit_message_text(
            ui.decor_msg(text, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_security":
        maint_status = "🟢 ON" if db.get_config("maint_mode") == "ON" else "🔴 OFF"
        force_status = "🟢 ON" if db.get_config("force_join") == "ON" else "🔴 OFF"
        
        text = (
            f"🛡️ <b>Security Settings</b>\n\n"
            f"Current Status:\n"
            f"• Maintenance Mode: {maint_status}\n"
            f"• Force Join: {force_status}\n\n"
            f"Select option:"
        )
        
        keyboard = [
            [InlineKeyboardButton(f"🔄 Maintenance Mode", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"🔄 Force Join", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            ui.decor_msg(text, user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_marketing":
        keyboard = [
            [InlineKeyboardButton("📝 Create Post", callback_data="wiz_start")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="broad_start")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            ui.decor_msg("📡 <b>Marketing Zone</b>\nSelect action:", user),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_stats":
        total_users, today_users = db.get_stats()
        channels = db.get_all_channels()
        
        text = (
            f"📊 <b>Detailed Statistics</b>\n\n"
            f"📈 <b>User Stats:</b>\n"
            f"• Total Users: {total_users}\n"
            f"• Today's New: {today_users}\n\n"
            f"📢 <b>Channel Stats:</b>\n"
            f"• Total Channels: {len(channels)}\n\n"
        )
        
        if channels:
            text += f"<b>Channel List:</b>\n"
            for idx, (ch_id, name, link) in enumerate(channels, 1):
                text += f"{idx}. {name}\n"
        
        await query.edit_message_text(
            ui.decor_msg(text, user),
            reply_markup=ui.back_to_main_kb(),
            parse_mode=ParseMode.HTML
        )
    
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        
        current_value = db.get_config(key)
        
        await query.message.reply_text(
            f"✏️ <b>Editing:</b> <code>{key}</code>\n"
            f"Current value: <code>{current_value}</code>\n\n"
            "Please send the new value:",
            parse_mode=ParseMode.HTML
        )
        return STATE_EDIT_VALUE
    
    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        current = db.get_config(key)
        new_value = "OFF" if current == "ON" else "ON"
        db.set_config(key, new_value)
        
        await query.answer(f"✅ {key} set to {new_value}", show_alert=True)
        # Refresh the menu
        await callback_handler(update, context)
    
    elif data.startswith("remove_channel_"):
        channel_id = data.replace("remove_channel_", "")
        if db.remove_channel(channel_id):
            await query.answer("✅ Channel removed!", show_alert=True)
        else:
            await query.answer("❌ Failed to remove!", show_alert=True)
        # Refresh channel menu
        query.data = "menu_channels"
        await callback_handler(update, context)
    
    elif data == "add_channel":
        await query.message.reply_text(
            "📝 <b>Add New Channel</b>\n\n"
            "Please send the Channel ID (e.g., @channelname or -1001234567890):",
            parse_mode=ParseMode.HTML
        )
        return STATE_ADD_CHANNEL_ID
    
    elif data == "wiz_start":
        await query.message.reply_text(
            "📝 <b>Post Wizard - Step 1/4</b>\n\n"
            "Please send the post caption:",
            parse_mode=ParseMode.HTML
        )
        return STATE_POST_CAPTION
    
    elif data == "broad_start":
        await query.message.reply_text(
            "📢 <b>Broadcast Mode</b>\n\n"
            "Please send the message to broadcast (text, photo, or video):",
            parse_mode=ParseMode.HTML
        )
        return STATE_BROADCAST_MSG

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================
async def edit_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing configuration values"""
    key = context.user_data.get('edit_key')
    new_value = update.message.text
    
    if key:
        db.set_config(key, new_value)
        await update.message.reply_text(
            f"✅ <b>Successfully updated!</b>\n\n"
            f"<code>{key}</code> = <code>{new_value}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Error: No key specified")
    
    return ConversationHandler.END

async def add_channel_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get channel ID"""
    context.user_data['channel_id'] = update.message.text
    
    await update.message.reply_text(
        "📝 <b>Step 2/3</b>\n\n"
        "Please send the Channel Name:",
        parse_mode=ParseMode.HTML
    )
    return STATE_ADD_CHANNEL_NAME

async def add_channel_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get channel name"""
    context.user_data['channel_name'] = update.message.text
    
    await update.message.reply_text(
        "📝 <b>Step 3/3</b>\n\n"
        "Please send the Channel Link (t.me/...):",
        parse_mode=ParseMode.HTML
    )
    return STATE_ADD_CHANNEL_LINK

async def add_channel_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get channel link and save"""
    channel_id = context.user_data.get('channel_id')
    channel_name = context.user_data.get('channel_name')
    channel_link = update.message.text
    
    if db.add_channel(channel_id, channel_name, channel_link):
        await update.message.reply_text(
            f"✅ <b>Channel added successfully!</b>\n\n"
            f"• ID: <code>{channel_id}</code>\n"
            f"• Name: {channel_name}\n"
            f"• Link: {channel_link}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Failed to add channel!")
    
    # Clear temporary data
    context.user_data.clear()
    return ConversationHandler.END

async def post_wizard_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get post caption"""
    context.user_data['post_caption'] = update.message.text_html if update.message.text else update.message.caption_html
    
    await update.message.reply_text(
        "📝 <b>Post Wizard - Step 2/4</b>\n\n"
        "Please send media (photo/video) or type /skip:",
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_MEDIA

async def post_wizard_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get media or skip"""
    if update.message.photo:
        context.user_data['post_media'] = update.message.photo[-1].file_id
        context.user_data['post_type'] = 'photo'
    elif update.message.video:
        context.user_data['post_media'] = update.message.video.file_id
        context.user_data['post_type'] = 'video'
    else:
        context.user_data['post_media'] = None
        context.user_data['post_type'] = 'text'
    
    await update.message.reply_text(
        "📝 <b>Post Wizard - Step 3/4</b>\n\n"
        "Send button text (or /skip for default):",
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_BUTTONS

async def post_wizard_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get button text"""
    if update.message.text and update.message.text != "/skip":
        context.user_data['button_text'] = update.message.text
    else:
        context.user_data['button_text'] = db.get_config("btn_text")
    
    # Get channels for selection
    channels = db.get_all_channels()
    
    if not channels:
        await update.message.reply_text("❌ No channels added yet!")
        return ConversationHandler.END
    
    keyboard = []
    for ch_id, name, _ in channels:
        keyboard.append([
            InlineKeyboardButton(f"📤 Send to {name}", callback_data=f"sendpost_{ch_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("📤 Send to ALL", callback_data="sendpost_all")
    ])
    
    # Preview the post
    caption = context.user_data.get('post_caption', '')
    media = context.user_data.get('post_media')
    post_type = context.user_data.get('post_type')
    button_text = context.user_data.get('button_text', db.get_config("btn_text"))
    watch_url = db.get_config("watch_url")
    
    preview_text = (
        f"📝 <b>Post Wizard - Step 4/4</b>\n\n"
        f"<b>Preview:</b>\n"
        f"Type: {post_type.upper() if post_type else 'TEXT'}\n"
        f"Button: {button_text}\n\n"
        f"Select where to send:"
    )
    
    if post_type == 'photo' and media:
        await update.message.reply_photo(
            photo=media,
            caption=caption + f"\n\n[Preview] Button: {button_text}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=watch_url)]]),
            parse_mode=ParseMode.HTML
        )
    
    await update.message.reply_text(
        preview_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_CONFIRM

async def post_wizard_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 4: Send post to selected channels"""
    query = update.callback_query
    await query.answer()
    
    target = query.data.replace("sendpost_", "")
    caption = context.user_data.get('post_caption', '')
    media = context.user_data.get('post_media')
    post_type = context.user_data.get('post_type')
    button_text = context.user_data.get('button_text', db.get_config("btn_text"))
    watch_url = db.get_config("watch_url")
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=watch_url)]])
    channels = db.get_all_channels()
    
    success = 0
    failed = 0
    
    if target == "all":
        target_channels = channels
    else:
        target_channels = [ch for ch in channels if str(ch[0]) == target]
    
    status_msg = await query.message.reply_text(f"⏳ Sending to {len(target_channels)} channel(s)...")
    
    for ch_id, name, _ in target_channels:
        try:
            if post_type == 'photo' and media:
                await context.bot.send_photo(
                    chat_id=ch_id,
                    photo=media,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            elif post_type == 'video' and media:
                await context.bot.send_video(
                    chat_id=ch_id,
                    video=media,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=ch_id,
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            success += 1
        except Exception as e:
            logger.error(f"Failed to send to {ch_id}: {e}")
            failed += 1
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    await status_msg.edit_text(
        f"✅ <b>Posting Complete!</b>\n\n"
        f"• Successful: {success}\n"
        f"• Failed: {failed}\n\n"
        f"Total channels: {len(target_channels)}",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcasting to all users"""
    message = update.message
    users = db.get_all_users()
    
    if not users:
        await message.reply_text("❌ No users to broadcast!")
        return ConversationHandler.END
    
    total = len(users)
    status_msg = await message.reply_text(f"📤 Starting broadcast to {total} users...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            if message.photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption_html if message.caption else None,
                    parse_mode=ParseMode.HTML
                )
            elif message.video:
                await context.bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption_html if message.caption else None,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message.text_html,
                    parse_mode=ParseMode.HTML
                )
            success += 1
        except Exception as e:
            failed += 1
        
        # Update status every 20 users
        if (success + failed) % 20 == 0:
            await status_msg.edit_text(
                f"📤 Broadcasting...\n"
                f"Progress: {success + failed}/{total}\n"
                f"Success: {success} | Failed: {failed}"
            )
        
        await asyncio.sleep(0.1)  # Rate limiting
    
    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"• Total users: {total}\n"
        f"• Successfully sent: {success}\n"
        f"• Failed: {failed}",
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================
def main():
    """Start the bot"""
    logger.info("🚀 Starting Supreme God Mode Bot...")
    
    # Create application
    app = ApplicationBuilder() \
        .token(TOKEN) \
        .connection_pool_size(8) \
        .pool_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()
    
    # Add initial channels if database is empty
    if not db.get_all_channels():
        initial_channels = [
            ("@virallink259", "Viral Link 2026 🔥", "https://t.me/virallink259"),
            ("-1002279183424", "Premium Apps 💎", "https://t.me/+5PNLgcRBC0IxYjll"),
            ("@virallink246", "BD Beauty 🍑", "https://t.me/virallink246"),
            ("@viralexpress1", "FB Insta Links 🔗", "https://t.me/viralexpress1"),
            ("@movietime467", "Movie Time 🎬", "https://t.me/movietime467"),
            ("@viralfacebook9", "BD MMS Video 🔞", "https://t.me/viralfacebook9"),
            ("@viralfb24", "Deshi Bhabi 🔥", "https://t.me/viralfb24"),
            ("@fbviral24", "Kochi Meye 🎀", "https://t.me/fbviral24"),
            ("-1001550993047", "Request Zone 📥", "https://t.me/+WAOUc1rX6Qk3Zjhl"),
            ("-1002011739504", "Viral BD 🌍", "https://t.me/+la630-IFwHAwYWVl"),
            ("-1002444538806", "AI Studio 🎨", "https://t.me/+AHsGXIDzWmJlZjVl")
        ]
        
        for ch_id, name, link in initial_channels:
            db.add_channel(ch_id, name, link)
        logger.info("Initial channels added to database")
    
    # ===== CONVERSATION HANDLERS =====
    
    # Editor conversation
    editor_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern="^edit_")],
        states={
            STATE_EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_value_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        map_to_parent={ConversationHandler.END: ConversationHandler.END}
    )
    
    # Add channel conversation
    add_channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern="^add_channel$")],
        states={
            STATE_ADD_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id_handler)],
            STATE_ADD_CHANNEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name_handler)],
            STATE_ADD_CHANNEL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)]
    )
    
    # Post wizard conversation
    post_wizard_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern="^wiz_start$")],
        states={
            STATE_POST_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard_caption)],
            STATE_POST_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, post_wizard_media)],
            STATE_POST_BUTTONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard_buttons)],
            STATE_POST_CONFIRM: [CallbackQueryHandler(post_wizard_send, pattern="^sendpost_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)]
    )
    
    # Broadcast conversation
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern="^broad_start$")],
        states={
            STATE_BROADCAST_MSG: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)]
    )
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", admin_command))
    
    # Callback query handler (must be after conversations)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Conversation handlers
    app.add_handler(editor_conv)
    app.add_handler(add_channel_conv)
    app.add_handler(post_wizard_conv)
    app.add_handler(broadcast_conv)
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is now running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Log the full traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")
    
    # Notify admin
    try:
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Bot Error:\n{context.error}"
                )
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
