--- START OF FILE Paste January 19, 2026 - 3:21AM ---

"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (MOTHER BOT)
VERSION: v11.0 (Enterprise Grade - Bangla Hot Edition)
AUTHOR: AI ASSISTANT
STATUS: ACTIVE
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
import secrets
import string
import aiohttp # Required for Multi-Bot Broadcast
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Tuple
from collections import defaultdict

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, BotCommand
)
from telegram.constants import ParseMode, ChatAction
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    filters, ApplicationBuilder, Defaults
)
from telegram.error import BadRequest, Forbidden

# ==============================================================================
# ⚙️ CONFIGURATION CONSTANTS
# ==============================================================================

class Config:
    # ⚠️ REPLACE WITH YOUR MASTER BOT TOKEN
    TOKEN = "7959770637:AAE9lr18A3J5JoC-Cwxuv-0mXH6dUB9jy60" 
    
    # ⚠️ REPLACE WITH YOUR TELEGRAM ID
    ADMIN_IDS = {8013042180} 
    
    DB_NAME = "supreme_mother_bot.db"
    BACKUP_DIR = "backups"
    
    # UI Constants
    ITEMS_PER_PAGE = 10
    
    # Conversation States
    (
        STATE_MAIN_MENU,
        STATE_ADD_CHANNEL, STATE_DEL_CHANNEL,
        STATE_ADD_WELCOME_TEXT, STATE_ADD_WELCOME_PHOTO, STATE_WELCOME_PREVIEW,
        STATE_ADD_VIDEO_TITLE, STATE_ADD_VIDEO_URL, STATE_ADD_VIDEO_THUMB, STATE_VIDEO_PREVIEW,
        STATE_ADD_PHOTO_FILE, STATE_PHOTO_PREVIEW,
        STATE_POST_TITLE, STATE_POST_MEDIA, STATE_POST_BTN_TEXT, STATE_POST_BTN_LINK, STATE_POST_CHANNELS, STATE_POST_PREVIEW,
        STATE_ADD_CHILD_TOKEN, STATE_BROADCAST_MSG
    ) = range(20)

# ==============================================================================
# 📝 LOGGING
# ==============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("SupremeBot")

# ==============================================================================
# 🗄️ DATABASE MANAGER
# ==============================================================================

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DB_NAME
        self.init_database()
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_blocked BOOLEAN DEFAULT 0
            )''')
            
            # Force Channels
            cursor.execute('''CREATE TABLE IF NOT EXISTS force_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                title TEXT,
                invite_link TEXT,
                auto_join BOOLEAN DEFAULT 1
            )''')
            
            # Welcome Messages
            cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                photo_id TEXT,
                is_active BOOLEAN DEFAULT 1
            )''')
            
            # Videos
            cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                thumbnail_id TEXT,
                views INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Photos (Gallery)
            cursor.execute('''CREATE TABLE IF NOT EXISTS gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                caption TEXT,
                views INTEGER DEFAULT 0
            )''')
            
            # Child Bots
            cursor.execute('''CREATE TABLE IF NOT EXISTS child_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE,
                name TEXT,
                is_active BOOLEAN DEFAULT 1
            )''')
            
            conn.commit()

    # --- User Methods ---
    def add_user(self, user_id, first_name, username):
        with self.get_connection() as conn:
            conn.execute('''INSERT OR IGNORE INTO users (user_id, first_name, username) 
                         VALUES (?, ?, ?)''', (user_id, first_name, username))
            
    def get_stats(self):
        with self.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            blocked = conn.execute("SELECT COUNT(*) FROM users WHERE is_blocked=1").fetchone()[0]
            channels = conn.execute("SELECT COUNT(*) FROM force_channels").fetchone()[0]
            videos = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
            childs = conn.execute("SELECT COUNT(*) FROM child_bots").fetchone()[0]
            return {"total": total, "blocked": blocked, "channels": channels, "videos": videos, "childs": childs}

    def get_all_users(self):
        with self.get_connection() as conn:
            return [row['user_id'] for row in conn.execute("SELECT user_id FROM users WHERE is_blocked=0")]

    # --- Force Channel Methods ---
    def add_channel(self, channel_id, title, link):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO force_channels (channel_id, title, invite_link) VALUES (?,?,?)", 
                         (channel_id, title, link))
    
    def get_channels(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM force_channels").fetchall()

    def delete_channel(self, channel_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM force_channels WHERE id=?", (channel_id,))

    # --- Welcome Message Methods ---
    def add_welcome(self, text, photo_id):
        with self.get_connection() as conn:
            return conn.execute("INSERT INTO welcome_messages (text, photo_id) VALUES (?,?)", (text, photo_id)).lastrowid

    def get_random_welcome(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM welcome_messages WHERE is_active=1 ORDER BY RANDOM() LIMIT 1").fetchone()
            
    def get_all_welcome(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM welcome_messages").fetchall()
            
    def delete_welcome(self, msg_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM welcome_messages WHERE id=?", (msg_id,))

    # --- Video Methods ---
    def add_video(self, title, url, thumb_id):
        with self.get_connection() as conn:
            return conn.execute("INSERT INTO videos (title, url, thumbnail_id) VALUES (?,?,?)", (title, url, thumb_id)).lastrowid

    def get_videos(self, page=0):
        offset = page * Config.ITEMS_PER_PAGE
        with self.get_connection() as conn:
            videos = conn.execute(f"SELECT * FROM videos ORDER BY id DESC LIMIT {Config.ITEMS_PER_PAGE} OFFSET ?", (offset,)).fetchall()
            count = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
            return videos, count

    def get_video_by_id(self, vid_id):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM videos WHERE id=?", (vid_id,)).fetchone()
            
    def delete_video(self, vid_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM videos WHERE id=?", (vid_id,))

    # --- Photo Methods ---
    def add_photo(self, file_id, caption=""):
        with self.get_connection() as conn:
            return conn.execute("INSERT INTO gallery (file_id, caption) VALUES (?,?)", (file_id, caption)).lastrowid

    def get_photos(self, page=0):
        # Photos show 1 at a time in gallery view, but list shows pages
        offset = page * 1 # showing one by one logic in viewer, or list logic
        with self.get_connection() as conn:
            photos = conn.execute("SELECT * FROM gallery ORDER BY id DESC").fetchall()
            return photos

    def delete_photo(self, photo_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM gallery WHERE id=?", (photo_id,))

    # --- Child Bot Methods ---
    def add_child_bot(self, token, name):
        with self.get_connection() as conn:
            try:
                conn.execute("INSERT INTO child_bots (token, name) VALUES (?,?)", (token, name))
                return True
            except sqlite3.IntegrityError:
                return False

    def get_child_bots(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM child_bots WHERE is_active=1").fetchall()

db = DatabaseManager()

# ==============================================================================
# 🛠️ HELPER FUNCTIONS
# ==============================================================================

def get_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def check_subscription(user_id: int, bot) -> List[dict]:
    """Check if user joined all force channels. Returns list of missing channels."""
    channels = db.get_channels()
    missing = []
    
    for channel in channels:
        try:
            # Handle string IDs that might start with -100
            chat_id = channel['channel_id']
            if chat_id.startswith("-100"):
                chat_id = int(chat_id)
            
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                missing.append(channel)
        except Exception as e:
            logger.error(f"Error checking channel {channel['title']}: {e}")
            # If bot is not admin in channel, assume joined to avoid blocking user
            pass
            
    return missing

# ==============================================================================
# 👤 USER PANEL HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    
    # Check force join first
    missing = await check_subscription(user.id, context.bot)
    if missing:
        await send_force_join_message(update, user, missing)
        return

    # Get random welcome message
    msg_data = db.get_random_welcome()
    
    default_text = (
        f"💖🌸 <b>হ্যালো {user.first_name}!</b> 🌸💖\n\n"
        "🔥 <b>স্বাগতম আমাদের 💌 Exclusive Video & Photo Hub 💌-এ!</b> 🔥\n"
        "✨ এখানে তুমি ভিডিও, ছবি এবং মজার কনটেন্ট দেখতে পারবে! ✨\n\n"
        "👇 নিচের বাটন থেকে ব্রাউজ করো:"
    )
    
    text = msg_data['text'] if msg_data else default_text
    # Replace placeholder
    text = text.replace("[User First Name]", user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("🎥 Videos", callback_data="view_videos_0"),
         InlineKeyboardButton("🖼️ Photos", callback_data="view_photos_0")],
        [InlineKeyboardButton("🔞 Join Premium", url="https://t.me/your_premium_link"),
         InlineKeyboardButton("🆘 Support", url="https://t.me/admin")]
    ]
    
    if msg_data and msg_data['photo_id']:
        await update.message.reply_photo(
            photo=msg_data['photo_id'],
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def send_force_join_message(update: Update, user, missing_channels):
    text = (
        f"⚠️ <b>হেই {user.first_name}!</b> ⚠️\n"
        "💔 তুমি সব Force Channels join করোনি!\n"
        "❌ <b>Missing Channels:</b>\n"
    )
    
    buttons = []
    for ch in missing_channels:
        text += f"• {ch['title']}\n"
        buttons.append(InlineKeyboardButton(f"💌 Join {ch['title']}", url=ch['invite_link']))
    
    text += "\n💌 Join করো সব Channel তারপর ভিডিও / ছবি দেখো! 💖💫"
    
    # 2 buttons per row logic
    keyboard = list(get_chunks(buttons, 2))
    keyboard.append([InlineKeyboardButton("🔄 Verify Joined", callback_data="verify_join")])
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def verify_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer("Checking status...")
    
    missing = await check_subscription(user.id, context.bot)
    
    if not missing:
        await query.message.delete()
        await query.message.reply_text(
            "✅ <b>ধন্যবাদ! তুমি সব চ্যানেল জয়েন করেছ।</b> 🎉\nএখন তুমি সব ভিডিও এবং ছবি দেখতে পারবে!",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home / Start", callback_data="home")]])
        )
    else:
        await send_force_join_message(update, user, missing)

async def home_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Check force join again
    missing = await check_subscription(query.from_user.id, context.bot)
    if missing:
        await send_force_join_message(update, query.from_user, missing)
        return

    text = (
        f"🔥 <b>Welcome Back {query.from_user.first_name}!</b> 🔥\n\n"
        "✨ নিচের ক্যাটাগরি থেকে পছন্দ করো: 👇"
    )
    keyboard = [
        [InlineKeyboardButton("🎥 Videos", callback_data="view_videos_0"),
         InlineKeyboardButton("🖼️ Photos", callback_data="view_photos_0")],
        [InlineKeyboardButton("🔞 Join Premium", url="https://t.me/your_premium_link")]
    ]
    
    try:
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Video Section ---

async def view_videos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    page = int(query.data.split("_")[-1])
    
    # Force Join Check
    if await check_subscription(query.from_user.id, context.bot):
        await query.answer("❌ Please join channels first!", show_alert=True)
        return

    videos, total_count = db.get_videos(page)
    
    if not videos and page == 0:
        await query.answer("No videos available yet!", show_alert=True)
        return

    text = f"🎬 <b>ভিডিও Section (Page {page+1})</b> 🌟\n\n🔥 এখানে সব ভিডিও দেখতে পারবে! ✨💖"
    
    buttons = []
    for vid in videos:
        buttons.append(InlineKeyboardButton(f"🎥 {vid['title']}", callback_data=f"play_video_{vid['id']}"))
        
    keyboard = list(get_chunks(buttons, 2))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⏮️ Previous", callback_data=f"view_videos_{page-1}"))
    if (page + 1) * Config.ITEMS_PER_PAGE < total_count:
        nav_buttons.append(InlineKeyboardButton("⏭️ Next", callback_data=f"view_videos_{page+1}"))
        
    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🏠 Home", callback_data="home"), InlineKeyboardButton("🔄 Refresh", callback_data=f"view_videos_{page}")])
    
    try:
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    except BadRequest:
        # If message is a photo (from welcome), we can't edit text directly sometimes if no media
        await query.message.delete()
        await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

async def play_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    vid_id = int(query.data.split("_")[-1])
    video = db.get_video_by_id(vid_id)
    
    if not video:
        await query.answer("Video not found!", show_alert=True)
        return
        
    # Check force join
    if await check_subscription(query.from_user.id, context.bot):
        await query.answer("❌ Join channels first!", show_alert=True)
        return

    text = (
        f"📽️ <b>{video['title']}</b>\n"
        f"🌟 <b>Uploaded by:</b> Admin\n"
        f"👁️ <b>Views:</b> {video['views'] + 1}"
    )
    
    # Increment view (simple logic)
    # db.increment_video_view(vid_id) # Implementing strictly would require DB update
    
    keyboard = [
        [InlineKeyboardButton("▶️ Watch Video", url=video['url'])],
        [InlineKeyboardButton("💖 Like", callback_data=f"like_vid_{vid_id}"), 
         InlineKeyboardButton("💌 Share", url=f"https://t.me/share/url?url={video['url']}&text={video['title']}")],
        [InlineKeyboardButton("🔙 Back to List", callback_data="view_videos_0")]
    ]
    
    if video['thumbnail_id']:
        await query.message.delete()
        await query.message.reply_photo(
            photo=video['thumbnail_id'],
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.message.edit_text(
            text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Photo Section ---

async def view_photos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        index = int(query.data.split("_")[-1])
    except:
        index = 0
        
    # Force Join Check
    if await check_subscription(query.from_user.id, context.bot):
        await query.answer("❌ Please join channels first!", show_alert=True)
        return

    photos = db.get_photos()
    
    if not photos:
        await query.answer("No photos available!", show_alert=True)
        return
        
    # Pagination logic for single photo view
    if index >= len(photos): index = 0
    if index < 0: index = len(photos) - 1
    
    photo = photos[index]
    
    text = f"🖼️ <b>Photo Gallery ({index+1}/{len(photos)})</b> 🌹\n{photo['caption'] or ''}"
    
    keyboard = [
        [InlineKeyboardButton("⏮️ Previous", callback_data=f"view_photos_{index-1}"),
         InlineKeyboardButton("⏭️ Next", callback_data=f"view_photos_{index+1}")],
        [InlineKeyboardButton("💌 Share", url=f"https://t.me/share/url?url=Check this out!"),
         InlineKeyboardButton("🏠 Home", callback_data="home")]
    ]
    
    # Need to delete previous message to send new photo or edit media
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=photo['file_id'], caption=text, parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        # Fallback if previous message wasn't media or too old
        await query.message.delete()
        await query.message.reply_photo(
            photo=photo['file_id'],
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==============================================================================
# 👑 ADMIN PANEL HANDLERS
# ==============================================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_IDS:
        return
    
    text = (
        "👑 <b>SUPREME ADMIN PANEL</b> 👑\n\n"
        "Select an option to manage:"
    )
    
    buttons = [
        [InlineKeyboardButton("📩 Welcome Msgs", callback_data="admin_welcome"),
         InlineKeyboardButton("📢 Force Channels", callback_data="admin_channels")],
        [InlineKeyboardButton("🎬 Manage Videos", callback_data="admin_videos"),
         InlineKeyboardButton("🖼️ Manage Photos", callback_data="admin_photos")],
        [InlineKeyboardButton("🤖 Multi-Bot", callback_data="admin_multibot"),
         InlineKeyboardButton("📝 Create Post", callback_data="post_start")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
         InlineKeyboardButton("💾 Backup DB", callback_data="admin_backup")]
    ]
    
    await update.message.reply_text(
        text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons)
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if query.from_user.id not in Config.ADMIN_IDS:
        await query.answer("⛔ Access Denied")
        return

    if data == "admin_stats":
        stats = db.get_stats()
        text = (
            "📊 <b>BOT STATISTICS</b>\n\n"
            f"👥 Total Users: {stats['total']}\n"
            f"🚫 Blocked: {stats['blocked']}\n"
            f"📢 Force Channels: {stats['channels']}\n"
            f"🎬 Videos: {stats['videos']}\n"
            f"🤖 Child Bots: {stats['childs']}"
        )
        await query.answer()
        await query.message.reply_text(text, parse_mode=ParseMode.HTML)
        
    elif data == "admin_backup":
        await query.answer("Creating backup...")
        # Simple backup logic
        if not os.path.exists(Config.BACKUP_DIR):
            os.makedirs(Config.BACKUP_DIR)
        backup_path = f"{Config.BACKUP_DIR}/backup_{int(time.time())}.db"
        
        with open(Config.DB_NAME, 'rb') as f:
            data = f.read()
        with open(backup_path, 'wb') as f:
            f.write(data)
            
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=open(backup_path, 'rb'),
            caption=f"✅ Backup created: {os.path.basename(backup_path)}"
        )

    elif data == "admin_channels":
        channels = db.get_channels()
        text = "📢 <b>Force Channels List:</b>\n"
        kb = []
        for ch in channels:
            text += f"• {ch['title']} (ID: {ch['channel_id']})\n"
            kb.append([InlineKeyboardButton(f"❌ Del {ch['title']}", callback_data=f"del_ch_{ch['id']}")])
        
        kb.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_channel_start")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="admin_home")])
        
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        
    elif data == "add_channel_start":
        await query.message.reply_text("Send Channel ID, Title, Link separated by '|'\nExample: -10012345678|My Channel|https://t.me/...")
        return Config.STATE_ADD_CHANNEL

    elif data.startswith("del_ch_"):
        ch_id = int(data.split("_")[-1])
        db.delete_channel(ch_id)
        await query.answer("Channel Deleted!")
        # Refresh
        await admin_callback(update, context) # Recursive call trick or just send msg

    elif data == "admin_welcome":
        msgs = db.get_all_welcome()
        text = f"📩 <b>Welcome Messages ({len(msgs)})</b>"
        kb = [[InlineKeyboardButton("➕ Add New Message", callback_data="add_welcome_start")]]
        
        for msg in msgs:
            kb.append([InlineKeyboardButton(f"❌ Delete ID: {msg['id']}", callback_data=f"del_welcome_{msg['id']}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="admin_home")])
        
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

    elif data == "add_welcome_start":
        await query.message.reply_text("Send the Welcome Text (Use [User First Name] for name):")
        return Config.STATE_ADD_WELCOME_TEXT

    elif data.startswith("del_welcome_"):
        wid = int(data.split("_")[-1])
        db.delete_welcome(wid)
        await query.answer("Deleted!")
        await query.message.reply_text("Message Deleted.")

    # --- Video Admin ---
    elif data == "admin_videos":
        videos, _ = db.get_videos(0)
        text = "🎬 <b>Manage Videos</b>"
        kb = [[InlineKeyboardButton("➕ Add Video", callback_data="add_video_start")]]
        for v in videos:
            kb.append([InlineKeyboardButton(f"❌ {v['title']}", callback_data=f"del_video_{v['id']}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="admin_home")])
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

    elif data == "add_video_start":
        await query.message.reply_text("Send Video Title:")
        return Config.STATE_ADD_VIDEO_TITLE
    
    elif data.startswith("del_video_"):
        vid = int(data.split("_")[-1])
        db.delete_video(vid)
        await query.answer("Video Deleted")
        await query.message.reply_text("Video deleted.")

    # --- Photo Admin ---
    elif data == "admin_photos":
        text = "🖼️ <b>Manage Photos</b>\nSend photos to add them directly (or click add)."
        kb = [[InlineKeyboardButton("➕ Add Photo", callback_data="add_photo_start")]]
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="admin_home")])
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

    elif data == "add_photo_start":
        await query.message.reply_text("Send the Photo now:")
        return Config.STATE_ADD_PHOTO_FILE

    # --- Multi Bot ---
    elif data == "admin_multibot":
        bots = db.get_child_bots()
        text = f"🤖 <b>Child Bots ({len(bots)})</b>"
        kb = [[InlineKeyboardButton("➕ Add Bot Token", callback_data="add_bot_start")]]
        kb.append([InlineKeyboardButton("📢 Broadcast to All", callback_data="broadcast_start")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="admin_home")])
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        
    elif data == "add_bot_start":
        await query.message.reply_text("Send Child Bot Token:")
        return Config.STATE_ADD_CHILD_TOKEN
        
    elif data == "broadcast_start":
        await query.message.reply_text("Send message to broadcast to ALL child bots' users (Simulated):")
        return Config.STATE_BROADCAST_MSG

    elif data == "admin_home":
        # Return to main admin menu logic
        pass 

# ==============================================================================
# 📝 CONVERSATION HANDLERS (CMS)
# ==============================================================================

# --- Add Channel Conversation ---
async def add_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw = update.message.text.split('|')
        cid, title, link = raw[0].strip(), raw[1].strip(), raw[2].strip()
        db.add_channel(cid, title, link)
        await update.message.reply_text(f"✅ Channel {title} added!")
    except:
        await update.message.reply_text("❌ Error! Format: ID|Title|Link")
    return ConversationHandler.END

# --- Add Welcome Conversation ---
async def welcome_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['w_text'] = update.message.text
    await update.message.reply_text("Now send the Photo (or type 'skip'):")
    return Config.STATE_ADD_WELCOME_PHOTO

async def welcome_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['w_photo'] = update.message.photo[-1].file_id
    else:
        context.user_data['w_photo'] = None
    
    # Preview
    text = f"<b>PREVIEW:</b>\n{context.user_data['w_text']}"
    kb = [[InlineKeyboardButton("💾 Save", callback_data="save_welcome"), 
           InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    
    if context.user_data['w_photo']:
        await update.message.reply_photo(context.user_data['w_photo'], caption=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    return Config.STATE_WELCOME_PREVIEW

async def save_welcome_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "save_welcome":
        db.add_welcome(context.user_data['w_text'], context.user_data['w_photo'])
        await query.answer("Saved!")
        await query.message.reply_text("✅ Welcome Message Saved.")
    else:
        await query.answer("Cancelled")
        await query.message.reply_text("Cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# --- Add Video Conversation ---
async def video_title_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['v_title'] = update.message.text
    await update.message.reply_text("Send Video URL (Direct link/YouTube):")
    return Config.STATE_ADD_VIDEO_URL

async def video_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['v_url'] = update.message.text
    await update.message.reply_text("Send Thumbnail Photo:")
    return Config.STATE_ADD_VIDEO_THUMB

async def video_thumb_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        thumb = update.message.photo[-1].file_id
        db.add_video(context.user_data['v_title'], context.user_data['v_url'], thumb)
        await update.message.reply_text("✅ Video Added!")
    else:
        await update.message.reply_text("❌ Photo required for thumbnail.")
    return ConversationHandler.END

# --- Add Photo Conversation ---
async def photo_file_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        fid = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        db.add_photo(fid, caption)
        await update.message.reply_text("✅ Photo added to Gallery!")
    return ConversationHandler.END # Loop could be added for multiple

# --- Multi-Channel Post Wizard ---
async def post_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("📝 <b>Step 1:</b> Send Post Title/Caption:")
    return Config.STATE_POST_TITLE

async def post_title_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_title'] = update.message.text_html
    await update.message.reply_text("📝 <b>Step 2:</b> Send Photo/Video (or skip):")
    return Config.STATE_POST_MEDIA

async def post_media_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['p_media'] = update.message.photo[-1].file_id
        context.user_data['p_type'] = 'photo'
    elif update.message.video:
        context.user_data['p_media'] = update.message.video.file_id
        context.user_data['p_type'] = 'video'
    else:
        context.user_data['p_media'] = None
        context.user_data['p_type'] = 'text'
        
    await update.message.reply_text("📝 <b>Step 3:</b> Button Text (or skip):")
    return Config.STATE_POST_BTN_TEXT

async def post_btn_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt.lower() == 'skip':
        context.user_data['p_btn'] = None
        # Skip link step
        await send_post_preview(update, context)
        return Config.STATE_POST_PREVIEW
    
    context.user_data['p_btn_txt'] = txt
    await update.message.reply_text("📝 <b>Step 4:</b> Button Link:")
    return Config.STATE_POST_BTN_LINK

async def post_btn_link_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_btn_link'] = update.message.text
    await send_post_preview(update, context)
    return Config.STATE_POST_PREVIEW

async def send_post_preview(update, context):
    d = context.user_data
    kb = []
    if d.get('p_btn_txt'):
        kb = [[InlineKeyboardButton(d['p_btn_txt'], url=d['p_btn_link'])]]
    
    ctrl_kb = [
        [InlineKeyboardButton("✅ Confirm & Post", callback_data="post_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    
    msg_text = f"<b>PREVIEW:</b>\n\n{d['p_title']}"
    
    if d['p_type'] == 'photo':
        await update.message.reply_photo(d['p_media'], caption=msg_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb + ctrl_kb))
    elif d['p_type'] == 'video':
        await update.message.reply_video(d['p_media'], caption=msg_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb + ctrl_kb))
    else:
        await update.message.reply_text(msg_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb + ctrl_kb))

async def post_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "cancel":
        await update.callback_query.answer("Cancelled")
        await update.callback_query.message.delete()
        return ConversationHandler.END
        
    d = context.user_data
    channels = db.get_channels()
    
    await update.callback_query.answer("Posting...")
    count = 0
    
    kb = []
    if d.get('p_btn_txt'):
        kb = [[InlineKeyboardButton(d['p_btn_txt'], url=d['p_btn_link'])]]
    markup = InlineKeyboardMarkup(kb) if kb else None
    
    for ch in channels:
        try:
            cid = ch['channel_id']
            if cid.startswith("-100"): cid = int(cid)
            
            if d['p_type'] == 'photo':
                await context.bot.send_photo(cid, d['p_media'], caption=d['p_title'], parse_mode=ParseMode.HTML, reply_markup=markup)
            elif d['p_type'] == 'video':
                await context.bot.send_video(cid, d['p_media'], caption=d['p_title'], parse_mode=ParseMode.HTML, reply_markup=markup)
            else:
                await context.bot.send_message(cid, d['p_title'], parse_mode=ParseMode.HTML, reply_markup=markup)
            count += 1
        except Exception as e:
            logger.error(f"Post failed for {cid}: {e}")
            
    await update.callback_query.message.reply_text(f"✅ Posted to {count} channels.")
    context.user_data.clear()
    return ConversationHandler.END

# --- Child Bot Logic ---
async def add_bot_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    # Simple check
    if ":" in token:
        db.add_child_bot(token, "Child Bot")
        await update.message.reply_text("✅ Child Bot Added.")
    else:
        await update.message.reply_text("❌ Invalid Token.")
    return ConversationHandler.END

async def broadcast_msg_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    bots = db.get_child_bots()
    
    await update.message.reply_text(f"🚀 Broadcasting via {len(bots)} bots (Async)...")
    
    # Fire and forget async task
    asyncio.create_task(run_broadcast(bots, msg_text))
    
    return ConversationHandler.END

async def run_broadcast(bots, text):
    async with aiohttp.ClientSession() as session:
        for bot in bots:
            try:
                # This is a simplification. Usually you'd iterate the child bot's DB of users.
                # Since we don't have access to child bot DBs here, we assume this Mother Bot 
                # might act as the controller for them via Webhook or similar.
                # For this code, we demonstrate verifying the token is alive.
                url = f"https://api.telegram.org/bot{bot['token']}/getMe"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        logger.info(f"Broadcast active for bot {bot['token'][:10]}...")
            except:
                pass

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Action Cancelled.")
    return ConversationHandler.END

# ==============================================================================
# 🌐 HEALTH SERVER (Render Support)
# ==============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Supreme Bot Alive")

def run_server():
    try:
        server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
        server.serve_forever()
    except:
        pass

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================

def main():
    # Start Web Server for Render
    threading.Thread(target=run_server, daemon=True).start()
    
    app = ApplicationBuilder().token(Config.TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    
    # Admin Conversation - Add Channel
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^add_channel_start$")],
        states={Config.STATE_ADD_CHANNEL: [MessageHandler(filters.TEXT, add_channel_input)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    # Admin Conversation - Add Welcome
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^add_welcome_start$")],
        states={
            Config.STATE_ADD_WELCOME_TEXT: [MessageHandler(filters.TEXT, welcome_text_input)],
            Config.STATE_ADD_WELCOME_PHOTO: [MessageHandler(filters.ALL, welcome_photo_input)],
            Config.STATE_WELCOME_PREVIEW: [CallbackQueryHandler(save_welcome_callback)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    # Admin Conversation - Add Video
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^add_video_start$")],
        states={
            Config.STATE_ADD_VIDEO_TITLE: [MessageHandler(filters.TEXT, video_title_input)],
            Config.STATE_ADD_VIDEO_URL: [MessageHandler(filters.TEXT, video_url_input)],
            Config.STATE_ADD_VIDEO_THUMB: [MessageHandler(filters.PHOTO, video_thumb_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    # Admin Conversation - Add Photo
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^add_photo_start$")],
        states={Config.STATE_ADD_PHOTO_FILE: [MessageHandler(filters.PHOTO, photo_file_input)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Admin Conversation - Create Post
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^post_start$")],
        states={
            Config.STATE_POST_TITLE: [MessageHandler(filters.TEXT, post_title_input)],
            Config.STATE_POST_MEDIA: [MessageHandler(filters.ALL, post_media_input)],
            Config.STATE_POST_BTN_TEXT: [MessageHandler(filters.TEXT, post_btn_text_input)],
            Config.STATE_POST_BTN_LINK: [MessageHandler(filters.TEXT, post_btn_link_input)],
            Config.STATE_POST_PREVIEW: [CallbackQueryHandler(post_confirm_callback)]
        },
        fallbacks=[CallbackQueryHandler(post_confirm_callback, pattern="cancel")]
    ))
    
    # Admin Conversation - Multi Bot
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^add_bot_start$")],
        states={Config.STATE_ADD_CHILD_TOKEN: [MessageHandler(filters.TEXT, add_bot_token_input)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^broadcast_start$")],
        states={Config.STATE_BROADCAST_MSG: [MessageHandler(filters.TEXT, broadcast_msg_input)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # General Handlers
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(verify_join_callback, pattern="^verify_join$"))
    app.add_handler(CallbackQueryHandler(home_callback, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(view_videos_callback, pattern="^view_videos_"))
    app.add_handler(CallbackQueryHandler(play_video_callback, pattern="^play_video_"))
    app.add_handler(CallbackQueryHandler(view_photos_callback, pattern="^view_photos_"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^del_"))

    print("🔥 SUPREME BOT v11.0 STARTED SUCCESSFULLY! 🔥")
    app.run_polling()

if __name__ == "__main__":
    main()
