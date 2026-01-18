"""
================================================================================
PROJECT: SUPREME GOD MODE BOT - COMPLETE WORKING VERSION
VERSION: v600.0 (Fully Functional)
AUTHOR: AI ASSISTANT
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
import traceback

# Third-party imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.constants import ParseMode
    from telegram.helpers import mention_html
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler,
        ContextTypes, ConversationHandler, MessageHandler, 
        filters, ApplicationBuilder
    )
except ImportError:
    print("Please install: pip install python-telegram-bot")
    sys.exit(1)

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================

TOKEN = "8510787985:AAH2aosQ5T5Ol-Yw4KIc37eIh9XQQcOYO0U"
ADMIN_IDS = {6406804999}
DB_NAME = "supreme_bot.db"
LOG_LEVEL = logging.INFO
START_TIME = time.time()

# Conversation States
STATE_EDIT = 1
STATE_POST_CAPTION = 2
STATE_POST_MEDIA = 3
STATE_POST_BUTTON = 4
STATE_POST_CONFIRM = 5
STATE_BROADCAST = 6
STATE_CHANNEL_ID = 7
STATE_CHANNEL_NAME = 8
STATE_CHANNEL_LINK = 9

# ==============================================================================
# 📝 LOGGING SETUP
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 🗄️ SIMPLE DATABASE MANAGER
# ==============================================================================
class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()
        self._initialized = True
    
    def setup_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Config table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Channels table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.initialize_defaults()
    
    def initialize_defaults(self):
        defaults = {
            'welcome_msg': '''💖✨ <b>ওগো শুনছো! স্বাগতম জানাই তোমাকে!</b> ✨💖

🌹 <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা খুশিতে নেচে উঠলো! 😍💃

👇 <b>দেরি না করে নিচের বাটনে আলতো করে ক্লিক করো সোনা:</b> 👇''',
            
            'lock_msg': '''💔 <b>ওহ নো বেবি! তুমি এখনো জয়েন করোনি?</b> 😢💔

আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀''',
            
            'welcome_photo': 'https://cdn.pixabay.com/photo/2018/01/14/23/12/nature-3082832_1280.jpg',
            'watch_url': 'https://mmshotbd.blogspot.com/?m=1',
            'btn_text': '🎬 ভিডিও দেখুন (Watch Now) ✨😍',
            'auto_delete': '45',
            'maint_mode': 'OFF',
            'force_join': 'ON'
        }
        
        for key, value in defaults.items():
            self.cursor.execute('''
                INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
            ''', (key, value))
        
        # Add default channels if empty
        self.cursor.execute("SELECT COUNT(*) FROM channels")
        if self.cursor.fetchone()[0] == 0:
            default_channels = [
                ('@virallink259', 'Viral Link 2026 🔥', 'https://t.me/virallink259'),
                ('-1002279183424', 'Premium Apps 💎', 'https://t.me/+5PNLgcRBC0IxYjll'),
                ('@virallink246', 'BD Beauty 🍑', 'https://t.me/virallink246'),
                ('@viralexpress1', 'FB Insta Links 🔗', 'https://t.me/viralexpress1'),
                ('@movietime467', 'Movie Time 🎬', 'https://t.me/movietime467')
            ]
            for ch_id, name, link in default_channels:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO channels (channel_id, name, link) VALUES (?, ?, ?)
                ''', (ch_id, name, link))
        
        self.conn.commit()
    
    def get_config(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else ""
    
    def set_config(self, key, value):
        self.cursor.execute('''
            INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name):
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            self.conn.commit()
        except:
            pass
    
    def get_all_users(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        total = self.cursor.fetchone()[0]
        
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?", (today,))
        today_count = self.cursor.fetchone()[0]
        
        return total, today_count
    
    def get_channels(self):
        self.cursor.execute("SELECT channel_id, name, link FROM channels ORDER BY name")
        return self.cursor.fetchall()
    
    def add_channel(self, channel_id, name, link):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link) VALUES (?, ?, ?)
            ''', (channel_id, name, link))
            self.conn.commit()
            return True
        except:
            return False
    
    def remove_channel(self, channel_id):
        try:
            self.cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            self.conn.commit()
            return True
        except:
            return False

db = Database()

# ==============================================================================
# 🌐 HEALTH SERVER
# ==============================================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            uptime = time.time() - START_TIME
            response = {
                'status': 'online',
                'uptime': str(datetime.timedelta(seconds=int(uptime)))
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# ==============================================================================
# 🎨 UI HELPER
# ==============================================================================
class UI:
    @staticmethod
    def format_text(text, user=None):
        if user:
            name = mention_html(user.id, user.first_name or "User")
        else:
            name = "User"
        
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        header = "="*40 + "\n"
        footer = f"\n" + "="*40 + f"\n👤 User: {name}\n🕐 Time: {time_str}"
        return header + text + footer

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    # Check maintenance
    if db.get_config('maint_mode') == 'ON' and user.id not in ADMIN_IDS:
        await update.message.reply_text("🔧 Bot is under maintenance. Please try later.")
        return
    
    # Check if admin
    if user.id in ADMIN_IDS:
        keyboard = [[InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")]]
        await update.message.reply_text(
            "👋 Welcome Admin!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Check force join
    if db.get_config('force_join') == 'ON':
        missing = []
        channels = db.get_channels()
        for ch_id, name, link in channels:
            try:
                member = await context.bot.get_chat_member(ch_id, user.id)
                if member.status in ['left', 'kicked']:
                    missing.append((name, link))
            except:
                missing.append((name, link))
        
        if missing:
            # Show lock message
            lock_msg = db.get_config('lock_msg')
            keyboard = []
            for name, link in missing:
                keyboard.append([InlineKeyboardButton(f"Join {name}", url=link)])
            keyboard.append([InlineKeyboardButton("✅ I Joined All", callback_data="check_join")])
            
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=lock_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            return
    
    # Show welcome message
    welcome_msg = db.get_config('welcome_msg')
    btn_text = db.get_config('btn_text')
    watch_url = db.get_config('watch_url')
    
    keyboard = [[InlineKeyboardButton(btn_text, url=watch_url)]]
    
    await update.message.reply_photo(
        photo=db.get_config('welcome_photo'),
        caption=welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    await show_admin_panel(update, context)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    """Show admin panel"""
    total, today = db.get_stats()
    uptime = time.time() - START_TIME
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    text = f"""
👑 <b>ADMIN PANEL</b>

📊 <b>Statistics:</b>
• Total Users: {total}
• Today: {today}
• Uptime: {uptime_str}

<b>Select option:</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Edit Messages", callback_data="edit_msg")],
        [InlineKeyboardButton("🔗 Edit Links", callback_data="edit_link")],
        [InlineKeyboardButton("📢 Channel Manager", callback_data="channel_mgr")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("📤 Create Post", callback_data="create_post")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("❌ Close", callback_data="close_admin")]
    ]
    
    if message:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

# ==============================================================================
# 🔄 CALLBACK HANDLER
# ==============================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    if user.id not in ADMIN_IDS and data not in ['check_join', 'close_admin']:
        await query.message.reply_text("🚫 Admin only!")
        return
    
    # Main routing
    if data == 'admin_panel':
        await show_admin_panel(update, context)
    
    elif data == 'close_admin':
        await query.delete_message()
    
    elif data == 'check_join':
        # Check if user joined all channels
        missing = []
        channels = db.get_channels()
        for ch_id, name, link in channels:
            try:
                member = await context.bot.get_chat_member(ch_id, user.id)
                if member.status in ['left', 'kicked']:
                    missing.append((name, link))
            except:
                missing.append((name, link))
        
        if missing:
            await query.answer("❌ Still missing some channels!", show_alert=True)
            # Show join buttons again
            keyboard = []
            for name, link in missing:
                keyboard.append([InlineKeyboardButton(f"Join {name}", url=link)])
            keyboard.append([InlineKeyboardButton("✅ Check Again", callback_data="check_join")])
            
            await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
        else:
            await query.answer("✅ Verified! Showing content...", show_alert=True)
            # Show welcome message
            welcome_msg = db.get_config('welcome_msg')
            btn_text = db.get_config('btn_text')
            watch_url = db.get_config('watch_url')
            
            keyboard = [[InlineKeyboardButton(btn_text, url=watch_url)]]
            
            await query.message.edit_caption(
                caption=welcome_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
    
    elif data == 'edit_msg':
        keyboard = [
            [InlineKeyboardButton("📝 Welcome Message", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("📝 Lock Message", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ Welcome Photo", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        await query.edit_message_text(
            "✏️ <b>Edit Messages</b>\nSelect what to edit:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == 'edit_link':
        current_url = db.get_config('watch_url')
        current_btn = db.get_config('btn_text')
        current_del = db.get_config('auto_delete')
        
        text = f"""
🔗 <b>Link Settings</b>

Current:
• Watch URL: {current_url[:50]}...
• Button Text: {current_btn}
• Auto Delete: {current_del} seconds

Select to edit:
"""
        keyboard = [
            [InlineKeyboardButton("🔗 Watch URL", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🔄 Button Text", callback_data="edit_btn_text")],
            [InlineKeyboardButton("⏱️ Auto Delete", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    elif data == 'channel_mgr':
        channels = db.get_channels()
        text = "📢 <b>Channel Manager</b>\n\n"
        
        if channels:
            for idx, (ch_id, name, link) in enumerate(channels, 1):
                text += f"{idx}. {name}\n"
        else:
            text += "No channels added.\n"
        
        keyboard = []
        for ch_id, name, _ in channels:
            keyboard.append([InlineKeyboardButton(f"❌ Remove {name}", callback_data=f"remove_{ch_id}")])
        
        keyboard.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    elif data == 'settings':
        maint = db.get_config('maint_mode')
        force = db.get_config('force_join')
        
        text = f"""
⚙️ <b>Settings</b>

• Maintenance Mode: {maint}
• Force Join: {force}

Toggle:
"""
        keyboard = [
            [InlineKeyboardButton(f"🔄 Maintenance: {maint}", callback_data="toggle_maint")],
            [InlineKeyboardButton(f"🔄 Force Join: {force}", callback_data="toggle_force")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    elif data == 'create_post':
        await query.message.reply_text(
            "📝 <b>Post Creation</b>\n\nSend me the caption/text for your post:",
            parse_mode=ParseMode.HTML
        )
        context.user_data['post_data'] = {}
        return STATE_POST_CAPTION
    
    elif data == 'broadcast':
        await query.message.reply_text(
            "📢 <b>Broadcast</b>\n\nSend the message you want to broadcast to all users:",
            parse_mode=ParseMode.HTML
        )
        return STATE_BROADCAST
    
    elif data.startswith('edit_'):
        key = data.replace('edit_', '')
        context.user_data['edit_key'] = key
        current = db.get_config(key)
        
        await query.message.reply_text(
            f"✏️ Editing: <b>{key}</b>\nCurrent: <code>{current}</code>\n\nSend new value:",
            parse_mode=ParseMode.HTML
        )
        return STATE_EDIT
    
    elif data.startswith('remove_'):
        channel_id = data.replace('remove_', '')
        if db.remove_channel(channel_id):
            await query.answer("✅ Channel removed!", show_alert=True)
        else:
            await query.answer("❌ Failed to remove!", show_alert=True)
        # Refresh channel manager
        query.data = 'channel_mgr'
        await callback_handler(update, context)
    
    elif data == 'add_channel':
        await query.message.reply_text(
            "➕ <b>Add Channel</b>\n\nSend Channel ID (e.g., @channelname or -1001234567890):",
            parse_mode=ParseMode.HTML
        )
        return STATE_CHANNEL_ID
    
    elif data == 'toggle_maint':
        current = db.get_config('maint_mode')
        new_val = 'OFF' if current == 'ON' else 'ON'
        db.set_config('maint_mode', new_val)
        await query.answer(f"Maintenance: {new_val}", show_alert=True)
        query.data = 'settings'
        await callback_handler(update, context)
    
    elif data == 'toggle_force':
        current = db.get_config('force_join')
        new_val = 'OFF' if current == 'ON' else 'ON'
        db.set_config('force_join', new_val)
        await query.answer(f"Force Join: {new_val}", show_alert=True)
        query.data = 'settings'
        await callback_handler(update, context)
    
    else:
        await query.message.reply_text("Unknown action!")

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================
async def edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing config values"""
    key = context.user_data.get('edit_key')
    new_value = update.message.text
    
    if key:
        db.set_config(key, new_value)
        await update.message.reply_text(f"✅ <b>{key}</b> updated successfully!", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ Error: No key specified")
    
    context.user_data.clear()
    return ConversationHandler.END

async def post_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get post caption"""
    caption = update.message.text
    context.user_data['post_data']['caption'] = caption
    
    await update.message.reply_text(
        "📸 <b>Step 2/4</b>\n\nSend photo or video for post (or type /skip for text only):",
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_MEDIA

async def post_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get media"""
    if update.message.photo:
        context.user_data['post_data']['media'] = update.message.photo[-1].file_id
        context.user_data['post_data']['type'] = 'photo'
    elif update.message.video:
        context.user_data['post_data']['media'] = update.message.video.file_id
        context.user_data['post_data']['type'] = 'video'
    else:
        context.user_data['post_data']['media'] = None
        context.user_data['post_data']['type'] = 'text'
    
    await update.message.reply_text(
        "🔘 <b>Step 3/4</b>\n\nSend button text (or /skip to use default):",
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_BUTTON

async def post_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get button text"""
    if update.message.text and update.message.text != '/skip':
        context.user_data['post_data']['button_text'] = update.message.text
    else:
        context.user_data['post_data']['button_text'] = db.get_config('btn_text')
    
    # Show channel selection
    channels = db.get_channels()
    keyboard = []
    for ch_id, name, _ in channels:
        keyboard.append([InlineKeyboardButton(f"📤 Post to {name}", callback_data=f"post_to_{ch_id}")])
    
    if channels:
        keyboard.append([InlineKeyboardButton("📤 Post to ALL", callback_data="post_to_all")])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_post")])
    
    await update.message.reply_text(
        "✅ <b>Step 4/4</b>\n\nSelect where to post:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    return STATE_POST_CONFIRM

async def post_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 4: Confirm and post"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == 'cancel_post':
        await query.message.edit_text("❌ Post cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
    
    # Get post data
    post_data = context.user_data.get('post_data', {})
    caption = post_data.get('caption', '')
    media = post_data.get('media')
    post_type = post_data.get('type', 'text')
    button_text = post_data.get('button_text', db.get_config('btn_text'))
    watch_url = db.get_config('watch_url')
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=watch_url)]])
    
    # Get target channels
    channels = db.get_channels()
    if data == 'post_to_all':
        target_channels = channels
    else:
        channel_id = data.replace('post_to_', '')
        target_channels = [ch for ch in channels if ch[0] == channel_id]
    
    # Send posts
    success = 0
    failed = 0
    
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
            await asyncio.sleep(0.5)  # Rate limit
        except Exception as e:
            failed += 1
            logger.error(f"Failed to post to {ch_id}: {e}")
    
    await query.message.edit_text(
        f"✅ <b>Posting Complete!</b>\n\nSuccess: {success}\nFailed: {failed}",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast"""
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
                await message.copy(user_id)
            elif message.video:
                await message.copy(user_id)
            else:
                await context.bot.send_message(user_id, message.text)
            success += 1
        except:
            failed += 1
        
        # Update progress every 20 users
        if (success + failed) % 20 == 0:
            await status_msg.edit_text(f"📤 Sent: {success}/{total} | Failed: {failed}")
        
        await asyncio.sleep(0.1)
    
    await status_msg.edit_text(f"✅ Broadcast complete!\nSuccess: {success}\nFailed: {failed}")
    return ConversationHandler.END

async def add_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get channel ID"""
    context.user_data['channel_id'] = update.message.text
    
    await update.message.reply_text(
        "📝 <b>Step 2/3</b>\n\nSend channel name:",
        parse_mode=ParseMode.HTML
    )
    return STATE_CHANNEL_NAME

async def add_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get channel name"""
    context.user_data['channel_name'] = update.message.text
    
    await update.message.reply_text(
        "🔗 <b>Step 3/3</b>\n\nSend channel link (t.me/...):",
        parse_mode=ParseMode.HTML
    )
    return STATE_CHANNEL_LINK

async def add_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get channel link and save"""
    channel_id = context.user_data.get('channel_id')
    channel_name = context.user_data.get('channel_name')
    channel_link = update.message.text
    
    if db.add_channel(channel_id, channel_name, channel_link):
        await update.message.reply_text(
            f"✅ Channel added!\nID: {channel_id}\nName: {channel_name}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Failed to add channel!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================
def main():
    """Start the bot"""
    logger.info("Starting Supreme Bot...")
    
    # Create application
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ===== CONVERSATION HANDLERS =====
    
    # Edit conversation
    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={
            STATE_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_value)]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    
    # Post creation conversation
    post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post$')],
        states={
            STATE_POST_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_caption)],
            STATE_POST_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, post_media)],
            STATE_POST_BUTTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_button)],
            STATE_POST_CONFIRM: [CallbackQueryHandler(post_confirm, pattern='^post_to_|^cancel_post$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    
    # Broadcast conversation
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast$')],
        states={
            STATE_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    
    # Add channel conversation
    channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel$')],
        states={
            STATE_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id)],
            STATE_CHANNEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name)],
            STATE_CHANNEL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link)]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('admin', admin_command))
    app.add_handler(CommandHandler('stats', admin_command))
    
    # Conversation handlers (MUST be before callback handler)
    app.add_handler(edit_conv)
    app.add_handler(post_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(channel_conv)
    
    # Callback query handler (catch-all, must be LAST)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to notify admin
    try:
        error_msg = f"⚠️ Error: {context.error}\n"
        if update and update.effective_message:
            error_msg += f"Chat: {update.effective_chat.id}\n"
        
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(admin_id, error_msg)
    except:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
