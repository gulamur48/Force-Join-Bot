#!/usr/bin/env python3
"""
🤖 MOTHER BOT - Termux Version
Complete bot in single file
"""

import os
import sys
import logging
import asyncio
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# Try to import Telegram libraries
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        filters,
        ContextTypes,
        ConversationHandler
    )
    from telegram.constants import ParseMode
    HAS_TELEGRAM = True
except ImportError:
    print("❌ python-telegram-bot not installed!")
    print("Run: pip install python-telegram-bot")
    HAS_TELEGRAM = False
    sys.exit(1)

# ==================== CONFIGURATION ====================
class Config:
    BOT_TOKEN = "8547594859:AAHX5Dy5sjRng4Wyiy-fT5hf04HV7iwQ8Gc"  # Change this!
    ADMIN_IDS = [8013042180]  # Change to your user ID
    DATABASE_PATH = "data/database.db"
    
    EMOJIS = {
        "welcome": "💖🌸✨",
        "video": "🎬📽️🎥",
        "photo": "🖼️📸🌅",
        "success": "✅",
        "error": "❌",
        "admin": "👑"
    }

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(Config.DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize all database tables"""
        tables = [
            # Users table
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked BOOLEAN DEFAULT 0
            )""",
            
            # Welcome messages
            """CREATE TABLE IF NOT EXISTS welcome_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text TEXT NOT NULL,
                photo_url TEXT,
                order_num INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )""",
            
            # Force channels
            """CREATE TABLE IF NOT EXISTS force_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                channel_username TEXT NOT NULL,
                channel_title TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                order_num INTEGER DEFAULT 0
            )""",
            
            # Videos
            """CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                thumbnail TEXT,
                category TEXT DEFAULT 'general',
                order_num INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                likes INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0
            )""",
            
            # Photo galleries
            """CREATE TABLE IF NOT EXISTS photo_galleries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                order_num INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )""",
            
            # Photos
            """CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gallery_id INTEGER NOT NULL,
                photo_url TEXT NOT NULL,
                caption TEXT,
                order_num INTEGER DEFAULT 0
            )"""
        ]
        
        for table_sql in tables:
            self.cursor.execute(table_sql)
        
        # Insert default data if empty
        self.insert_default_data()
        self.conn.commit()
    
    def insert_default_data(self):
        """Insert default sample data"""
        # Check if welcome messages exist
        self.cursor.execute("SELECT COUNT(*) FROM welcome_messages")
        if self.cursor.fetchone()[0] == 0:
            welcome_messages = [
                ("""💖🌸 হ্যালো {first_name}! 🌸💖
🔥 স্বাগতম আমাদের Exclusive Video & Photo Hub-এ! 🔥
✨ এখানে তুমি ভিডিও, ছবি এবং মজার কনটেন্ট দেখতে পারবে! ✨
⚠️ সব কনটেন্ট দেখতে Force Channels join করতে হবে! 💎💫""", None, 1),
                
                ("""✨🎉 স্বাগতম {first_name}! 🎉✨
❤️ তোমাকে পেয়ে আমরা খুব খুশি! ❤️
🎬 ভিডিও এবং 🖼️ ছবির রাজ্যে তোমাকে স্বাগতম!
📢 নিচের চ্যানেলগুলো জয়েন করে সবকিছু আনলক করো! 💝""", None, 2)
            ]
            
            self.cursor.executemany(
                "INSERT INTO welcome_messages (message_text, photo_url, order_num) VALUES (?, ?, ?)",
                welcome_messages
            )
        
        # Insert sample videos
        self.cursor.execute("SELECT COUNT(*) FROM videos")
        if self.cursor.fetchone()[0] == 0:
            videos = [
                ("প্রথম ভিডিও টিউটোরিয়াল 🎬", "এটি একটি ডেমো ভিডিও", 
                 "https://youtu.be/dQw4w9WgXcQ", None, "শিক্ষামূলক", 1, 25, 150),
                ("বিনোদনমূলক কনটেন্ট 😄", "মজাদার ভিডিও", 
                 "https://youtu.be/example", None, "বিনোদন", 2, 42, 230),
            ]
            
            self.cursor.executemany(
                """INSERT INTO videos (title, description, url, thumbnail, category, order_num, likes, views) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                videos
            )
        
        self.conn.commit()
    
    def add_user(self, user_id: int, first_name: str, username: str = None):
        """Add new user to database"""
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
                (user_id, first_name, username)
            )
            self.conn.commit()
            return True
        except:
            return False
    
    def get_welcome_messages(self):
        """Get all active welcome messages"""
        self.cursor.execute(
            "SELECT * FROM welcome_messages WHERE is_active = 1 ORDER BY order_num"
        )
        return self.cursor.fetchall()
    
    def get_videos(self):
        """Get all active videos"""
        self.cursor.execute(
            "SELECT * FROM videos WHERE is_active = 1 ORDER BY order_num"
        )
        return self.cursor.fetchall()
    
    def get_photo_galleries(self):
        """Get all active photo galleries"""
        self.cursor.execute(
            "SELECT * FROM photo_galleries WHERE is_active = 1 ORDER BY order_num"
        )
        return self.cursor.fetchall()
    
    def get_photos_by_gallery(self, gallery_id: int):
        """Get photos by gallery ID"""
        self.cursor.execute(
            "SELECT * FROM photos WHERE gallery_id = ? ORDER BY order_num",
            (gallery_id,)
        )
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# ==================== UTILITIES ====================
def create_keyboard(buttons: List[List[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """Create inline keyboard"""
    return InlineKeyboardMarkup(buttons)

def format_welcome_message(text: str, first_name: str) -> str:
    """Format welcome message with user name"""
    return text.replace("{first_name}", first_name)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in Config.ADMIN_IDS

# ==================== USER PANEL ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db = Database()
    
    # Add user to database
    db.add_user(user.id, user.first_name, user.username)
    
    # Get welcome messages
    messages = db.get_welcome_messages()
    
    if messages:
        # Use first welcome message
        msg = messages[0]
        message_text = format_welcome_message(msg[1], user.first_name)
        
        # Create buttons
        keyboard = [
            [InlineKeyboardButton("🎬 Video Section", callback_data="video_section"),
             InlineKeyboardButton("🖼️ Photo Section", callback_data="photo_section")],
            [InlineKeyboardButton("📢 Force Channels", callback_data="force_channels"),
             InlineKeyboardButton("🔄 Verify Joined", callback_data="verify_joined")],
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")]
        ]
        
        await update.message.reply_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            f"🌟 Hello {user.first_name}! Welcome to Mother Bot!",
            parse_mode=ParseMode.HTML
        )
    
    db.close()

async def show_video_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show video section"""
    query = update.callback_query
    await query.answer()
    
    db = Database()
    videos = db.get_videos()
    db.close()
    
    if not videos:
        await query.edit_message_text(
            "📭 No videos available yet!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Home", callback_data="home")
            ]])
        )
        return
    
    # Create video buttons (2 per row)
    buttons = []
    for i in range(0, len(videos), 2):
        row = []
        for j in range(2):
            if i + j < len(videos):
                video = videos[i + j]
                row.append(
                    InlineKeyboardButton(
                        f"🎥 {video[1][:15]}",
                        callback_data=f"video_{video[0]}"
                    )
                )
        if row:
            buttons.append(row)
    
    # Add navigation buttons
    buttons.append([
        InlineKeyboardButton("⏮️ Previous", callback_data="prev_page"),
        InlineKeyboardButton("⏭️ Next", callback_data="next_page")
    ])
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    
    await query.edit_message_text(
        f"🎬 **Video Section** ✨\n\n"
        f"Total Videos: {len(videos)}\n"
        f"Select a video to watch:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

async def show_photo_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show photo section"""
    query = update.callback_query
    await query.answer()
    
    db = Database()
    galleries = db.get_photo_galleries()
    db.close()
    
    if not galleries:
        await query.edit_message_text(
            "📭 No photo galleries available yet!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Home", callback_data="home")
            ]])
        )
        return
    
    # Create gallery buttons
    buttons = []
    for i in range(0, len(galleries), 2):
        row = []
        for j in range(2):
            if i + j < len(galleries):
                gallery = galleries[i + j]
                row.append(
                    InlineKeyboardButton(
                        f"🖼️ {gallery[1][:15]}",
                        callback_data=f"gallery_{gallery[0]}"
                    )
                )
        if row:
            buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    
    await query.edit_message_text(
        f"🖼️ **Photo Section** 🌸\n\n"
        f"Total Galleries: {len(galleries)}\n"
        f"Select a gallery to view:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

async def show_force_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show force channels"""
    query = update.callback_query
    await query.answer()
    
    db = Database()
    db.cursor.execute("SELECT * FROM force_channels WHERE is_active = 1 ORDER BY order_num")
    channels = db.cursor.fetchall()
    db.close()
    
    if not channels:
        message = "📢 **Force Channels**\n\nNo channels configured yet."
        keyboard = [[InlineKeyboardButton("🏠 Home", callback_data="home")]]
    else:
        message = "📢 **Force Channels**\n\nPlease join these channels:\n\n"
        keyboard = []
        
        for channel in channels:
            message += f"• {channel[3]}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"📢 Join {channel[3][:10]}",
                    url=f"https://t.me/{channel[2]}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Verify Joined", callback_data="verify_joined"),
            InlineKeyboardButton("🏠 Home", callback_data="home")
        ])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

# ==================== ADMIN PANEL ====================
async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Access denied! Admin only.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Welcome Messages", callback_data="admin_welcome"),
         InlineKeyboardButton("📢 Force Channels", callback_data="admin_channels")],
        [InlineKeyboardButton("🎬 Video Management", callback_data="admin_videos"),
         InlineKeyboardButton("🖼️ Photo Management", callback_data="admin_photos")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
         InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("🏠 Home", callback_data="home")]
    ]
    
    await update.message.reply_text(
        "👑 **Admin Panel** ⚙️\n\n"
        "Select a section to manage:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def admin_welcome_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message management"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    db = Database()
    messages = db.get_welcome_messages()
    db.close()
    
    keyboard = []
    for msg in messages:
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ Message {msg[0]}",
                callback_data=f"edit_welcome_{msg[0]}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("➕ Add New", callback_data="add_welcome"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="admin_main")
    ])
    
    await query.edit_message_text(
        "📝 **Welcome Message Management**\n\n"
        f"Total messages: {len(messages)}\n"
        "Click to edit:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    db = Database()
    
    # Get counts
    db.cursor.execute("SELECT COUNT(*) FROM users")
    total_users = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM videos")
    total_videos = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM photo_galleries")
    total_galleries = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM photos")
    total_photos = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM force_channels")
    total_channels = db.cursor.fetchone()[0]
    
    db.close()
    
    stats_text = f"""
📊 **Bot Statistics**

👥 Users: {total_users}
🎬 Videos: {total_videos}
🖼️ Galleries: {total_galleries}
📸 Photos: {total_photos}
📢 Channels: {total_channels}

🌟 Mother Bot v1.0
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats"),
         InlineKeyboardButton("📤 Export", callback_data="export_stats")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="admin_main")]
    ]
    
    await query.edit_message_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

# ==================== CALLBACK HANDLER ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "home":
        # Simulate start command
        user = query.from_user
        message = f"""💖🌸 হ্যালো {user.first_name}! 🌸💖
🔥 স্বাগতম Mother Bot-এ! 🔥
✨ এখানে তুমি ভিডিও, ছবি দেখতে পারবে! ✨"""
        
        keyboard = [
            [InlineKeyboardButton("🎬 Video Section", callback_data="video_section"),
             InlineKeyboardButton("🖼️ Photo Section", callback_data="photo_section")],
            [InlineKeyboardButton("📢 Force Channels", callback_data="force_channels"),
             InlineKeyboardButton("🔄 Verify Joined", callback_data="verify_joined")],
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "video_section":
        await show_video_section(update, context)
    
    elif data == "photo_section":
        await show_photo_section(update, context)
    
    elif data == "force_channels":
        await show_force_channels(update, context)
    
    elif data == "verify_joined":
        await query.answer("✅ All channels verified! (Demo)", show_alert=True)
    
    elif data == "admin_panel":
        # Create admin panel message
        keyboard = [
            [InlineKeyboardButton("📝 Welcome Messages", callback_data="admin_welcome"),
             InlineKeyboardButton("📢 Force Channels", callback_data="admin_channels")],
            [InlineKeyboardButton("🎬 Video Management", callback_data="admin_videos"),
             InlineKeyboardButton("🖼️ Photo Management", callback_data="admin_photos")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
             InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ]
        
        if is_admin(query.from_user.id):
            await query.edit_message_text(
                "👑 **Admin Panel** ⚙️\n\n"
                "Select a section to manage:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("❌ Admin only!", show_alert=True)
    
    elif data == "admin_welcome":
        await admin_welcome_management(update, context)
    
    elif data == "admin_stats":
        await admin_stats(update, context)
    
    elif data == "admin_main":
        keyboard = [
            [InlineKeyboardButton("📝 Welcome Messages", callback_data="admin_welcome"),
             InlineKeyboardButton("📢 Force Channels", callback_data="admin_channels")],
            [InlineKeyboardButton("🎬 Video Management", callback_data="admin_videos"),
             InlineKeyboardButton("🖼️ Photo Management", callback_data="admin_photos")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
             InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ]
        
        await query.edit_message_text(
            "👑 **Admin Panel** ⚙️\n\n"
            "Select a section to manage:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    
    elif data.startswith("video_"):
        video_id = int(data.split("_")[1])
        db = Database()
        db.cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        video = db.cursor.fetchone()
        db.close()
        
        if video:
            keyboard = [
                [InlineKeyboardButton("▶️ Watch Video", url=video[3]),
                 InlineKeyboardButton(f"💖 Like ({video[8]})", callback_data=f"like_video_{video[0]}")],
                [InlineKeyboardButton("⏮️ Previous", callback_data=f"prev_video_{video[0]}"),
                 InlineKeyboardButton("⏭️ Next", callback_data=f"next_video_{video[0]}")],
                [InlineKeyboardButton("📤 Share", callback_data=f"share_video_{video[0]}"),
                 InlineKeyboardButton("🏠 Home", callback_data="home")]
            ]
            
            await query.edit_message_text(
                f"🎬 **{video[1]}**\n\n"
                f"📝 {video[2]}\n\n"
                f"👁️ Views: {video[9]}\n"
                f"💖 Likes: {video[8]}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
    
    elif data.startswith("like_video_"):
        video_id = int(data.split("_")[2])
        db = Database()
        db.cursor.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (video_id,))
        db.conn.commit()
        db.close()
        await query.answer("👍 Liked!", show_alert=True)
    
    elif data.startswith("gallery_"):
        gallery_id = int(data.split("_")[1])
        db = Database()
        db.cursor.execute("SELECT * FROM photo_galleries WHERE id = ?", (gallery_id,))
        gallery = db.cursor.fetchone()
        
        db.cursor.execute("SELECT * FROM photos WHERE gallery_id = ? ORDER BY order_num", (gallery_id,))
        photos = db.cursor.fetchall()
        db.close()
        
        if photos:
            photo = photos[0]
            keyboard = [
                [InlineKeyboardButton("⏮️ Previous", callback_data=f"photo_prev_{gallery_id}_0"),
                 InlineKeyboardButton("⏭️ Next", callback_data=f"photo_next_{gallery_id}_0")],
                [InlineKeyboardButton("🔍 View Full", url=photo[2]),
                 InlineKeyboardButton("📤 Share", callback_data=f"share_photo_{photo[0]}")],
                [InlineKeyboardButton("🏠 Home", callback_data="home"),
                 InlineKeyboardButton("📂 Galleries", callback_data="photo_section")]
            ]
            
            caption = f"🖼️ {gallery[1]} - Photo 1/{len(photos)}"
            if photo[3]:
                caption += f"\n\n{photo[3]}"
            
            await query.edit_message_photo(
                photo=photo[2],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# ==================== MAIN FUNCTION ====================
async def main():
    """Main function to run the bot"""
    
    # Check bot token
    if Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "="*50)
        print("❌ ERROR: Please configure your bot token!")
        print("="*50)
        print("\nSteps to configure:")
        print("1. Open this file in editor")
        print("2. Find: BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'")
        print("3. Replace with your actual bot token from @BotFather")
        print("4. Change ADMIN_IDS to your Telegram user ID")
        print("5. Save and run again")
        print("\nGet your user ID from @userinfobot")
        print("="*50)
        return
    
    # Initialize database
    print("📊 Initializing database...")
    db = Database()
    db.close()
    
    # Create application
    print("🤖 Creating bot application...")
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    print("🔧 Setting up handlers...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_panel_command))
    application.add_handler(CommandHandler("help", lambda u,c: u.message.reply_text("Type /start to begin!")))
    
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start the bot
    print("\n" + "="*50)
    print("🌟 MOTHER BOT v1.0 - Termux Edition")
    print("="*50)
    print(f"🤖 Bot Token: {Config.BOT_TOKEN[:10]}...")
    print(f"👑 Admin IDs: {Config.ADMIN_IDS}")
    print(f"💾 Database: {Config.DATABASE_PATH}")
    print("="*50)
    print("\n🚀 Starting bot... Press Ctrl+C to stop")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep running
    await asyncio.Event().wait()

# ==================== RUN BOT ====================
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Check for Telegram library
    if not HAS_TELEGRAM:
        print("\nInstalling required packages...")
        os.system("pip install python-telegram-bot python-dotenv")
        print("\n✅ Packages installed. Please run the bot again.")
        sys.exit(0)
    
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your bot token is correct")
        print("2. Make sure you have internet connection")
        print("3. Check if bot is started with @BotFather")
        print("4. Try: pip install --upgrade python-telegram-bot")
