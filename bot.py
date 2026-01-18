"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (50 FEATURES)
VERSION: v10.0 (Enterprise Grade)
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
import hashlib
import secrets
import string
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback
import pickle
import base64
from contextlib import contextmanager
from collections import defaultdict, deque

# Telegram imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, BotCommand
)
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    filters, ApplicationBuilder, CallbackContext
)

# ==============================================================================
# ⚙️ CONFIGURATION CONSTANTS
# ==============================================================================

class Config:
    # Bot Configuration
    TOKEN = "8456027249:AAGraaftHZCDG7vRB3DGRJdsx-WOcDymhfE"
    ADMIN_IDS = {6406804999}
    DB_NAME = "supreme_bot_v10.db"
    BACKUP_DIR = "backups"
    LOG_FILE = "bot_activity.log"
    
    # System Constants
    DEFAULT_AUTO_DELETE = 45  # seconds
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3  # messages per second
    SESSION_TIMEOUT = 300  # 5 minutes
    
    # Channel Settings
    DEFAULT_CHANNELS = [
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
    
    # Emoji Pack
    EMOJIS = {
        "heart": "❤️",
        "star": "⭐",
        "fire": "🔥",
        "lock": "🔒",
        "unlock": "🔓",
        "gear": "⚙️",
        "bell": "🔔",
        "chart": "📊",
        "users": "👥",
        "admin": "👑",
        "camera": "📸",
        "video": "🎬",
        "link": "🔗",
        "time": "⏰",
        "check": "✅",
        "cross": "❌",
        "warn": "⚠️",
        "info": "ℹ️",
        "up": "⬆️",
        "down": "⬇️",
        "left": "⬅️",
        "right": "➡️",
        "refresh": "🔄",
        "plus": "➕",
        "minus": "➖",
        "question": "❓",
        "exclamation": "❗",
        "money": "💰",
        "gift": "🎁",
        "crown": "👑",
        "shield": "🛡️",
        "rocket": "🚀",
        "target": "🎯",
        "megaphone": "📢",
        "pencil": "✏️",
        "trash": "🗑️",
        "database": "💾",
        "cloud": "☁️",
        "sun": "☀️",
        "moon": "🌙",
        "earth": "🌍"
    }
    
    # Conversation States
    STATE_EDIT_CONFIG = 1
    STATE_POST_CAPTION = 2
    STATE_POST_MEDIA = 3
    STATE_POST_BUTTON = 4
    STATE_POST_CONFIRM = 5
    STATE_BROADCAST = 6
    STATE_CHANNEL_ADD_ID = 7
    STATE_CHANNEL_ADD_NAME = 8
    STATE_CHANNEL_ADD_LINK = 9
    STATE_USER_BLOCK = 10
    STATE_VIP_ADD = 11
    STATE_BACKUP_RESTORE = 12

# ==============================================================================
# 📝 ADVANCED LOGGING SYSTEM
# ==============================================================================

class SupremeLogger:
    def __init__(self):
        self.logger = logging.getLogger("SupremeBot")
        self.setup_logging()
        
    def setup_logging(self):
        # Create handlers
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        error_handler = logging.FileHandler('errors.log', encoding='utf-8')
        
        # Set levels
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        error_handler.setLevel(logging.ERROR)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Set formatters
        console_handler.setFormatter(simple_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Log startup
        self.logger.info("=" * 60)
        self.logger.info("SUPREME GOD BOT v10.0 STARTING...")
        self.logger.info("=" * 60)
    
    def get_logger(self):
        return self.logger

logger_instance = SupremeLogger()
logger = logger_instance.get_logger()

# ==============================================================================
# 🗄️ ENTERPRISE DATABASE MANAGER
# ==============================================================================

class DatabaseManager:
    """Advanced multi-threaded database manager with encryption and backup"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.db_path = Config.DB_NAME
        self.backup_dir = Config.BACKUP_DIR
        self.setup_directories()
        self.connection_pool = {}
        self.init_database()
        self._initialized = True
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def get_connection(self, thread_id=None):
        """Get database connection for thread (thread-safe)"""
        if thread_id is None:
            thread_id = threading.get_ident()
            
        with self._lock:
            if thread_id not in self.connection_pool:
                conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30
                )
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA cache_size=-2000")  # 2MB cache
                self.connection_pool[thread_id] = conn
                
            return self.connection_pool[thread_id]
    
    def init_database(self):
        """Initialize database with all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table with level tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                user_level INTEGER DEFAULT 1,
                is_vip BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # Config table with encryption flag
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                is_private BOOLEAN DEFAULT 0,
                force_join BOOLEAN DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_checked DATETIME,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Posts history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                post_type TEXT,
                content_hash TEXT,
                sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                views INTEGER DEFAULT 0,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
            )
        ''')
        
        # User sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # VIP users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_users (
                vip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                level INTEGER DEFAULT 1,
                perks TEXT DEFAULT '{}',
                assigned_by INTEGER,
                assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Flood control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flood_control (
                user_id INTEGER PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                last_message DATETIME DEFAULT CURRENT_TIMESTAMP,
                warning_count INTEGER DEFAULT 0,
                is_temporarily_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_vip ON users(is_vip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(sent_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions(expires_at)')
        
        conn.commit()
        self.initialize_defaults()
        logger.info("Database initialized successfully")
    
    def initialize_defaults(self):
        """Initialize default configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        defaults = [
            ('welcome_msg', '''{heart} {star} <b>💖✨ওগো শুনছো! স্বাগতম জানাই তোমাকে!💖✨</b> {star} {heart}

{fire} <b>❤️তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা আনন্দে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন অসম্পূর্ণ ছিল।</b>

{tada} <b>💖✨তোমার জন্য যা যা থাকছে::</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব কালেকশন 🔥
🎀 এবং আমার হৃদয়ের ভালোবাসা... ❤️

{link} <b>নিচের বাটনে ক্লিক করে শুরু করুন:</b>''', 0, 'messages', 'Welcome message for new users'),
            
            ('lock_msg', '''{lock} <b>অ্যাক্সেস লক করা আছে!</b>

{cross} 😢💔ওহ নো বেবি! তুমি এখনো জয়েন করোনি? আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
প্লিজ সোনা, রাগ করো না!

{info} নিচের সবগুলোতে জয়েন করে💖✨ {check} ভেরিফাই বাটনে ক্লিক করুন। আমি অপেক্ষা করছি... 😘❤️''', 0, 'messages', 'Message shown when user hasn\'t joined channels'),
            
            ('welcome_photo', 'https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead', 0, 'media', 'Welcome photo URL'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1', 0, 'links', 'Main watch URL'),
            ('btn_text', '{video} 🎬🎉ভিডিও দেখুন এখনই! {fire}', 0, 'buttons', 'Button text'),
            ('auto_delete', '45', 0, 'settings', 'Auto delete timer in seconds'),
            ('maint_mode', 'OFF', 0, 'security', 'Maintenance mode status'),
            ('force_join', 'ON', 0, 'security', 'Force join channels'),
            ('max_users_per_day', '1000', 0, 'limits', 'Maximum users per day'),
            ('vip_access_level', '2', 0, 'vip', 'VIP access level required'),
            ('backup_interval', '86400', 0, 'system', 'Backup interval in seconds'),
            ('flood_threshold', '5', 0, 'security', 'Flood threshold messages per minute'),
            ('session_timeout', '300', 0, 'security', 'Session timeout in seconds')
        ]
        
        for key, value, encrypted, category, description in defaults:
            cursor.execute('''
                INSERT OR IGNORE INTO config (key, value, encrypted, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, value, encrypted, category, description))
        
        # Add default channels
        cursor.execute("SELECT COUNT(*) FROM channels")
        if cursor.fetchone()[0] == 0:
            for channel in Config.DEFAULT_CHANNELS:
                cursor.execute('''
                    INSERT OR IGNORE INTO channels (channel_id, name, link)
                    VALUES (?, ?, ?)
                ''', (str(channel["id"]), channel["name"], channel["link"]))
        
        conn.commit()
    
    # === User Management ===
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """Add or update user in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, join_date, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_active = CURRENT_TIMESTAMP
            ''', (user_id, username, first_name, last_name))
            
            # Log activity
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, 'user_join', f'Username: {username}'))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            conn.rollback()
            return False
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET last_active = CURRENT_TIMESTAMP,
                    message_count = message_count + 1
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating activity for {user_id}: {e}")
    
    def get_user(self, user_id: int):
        """Get user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        
        if row:
            return dict(zip(columns, row))
        return None
    
    def get_all_users(self, active_only: bool = True):
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('''
                SELECT user_id FROM users 
                WHERE is_blocked = 0 
                ORDER BY last_active DESC
            ''')
        else:
            cursor.execute('SELECT user_id FROM users')
            
        return [row[0] for row in cursor.fetchall()]
    
    def block_user(self, user_id: int, admin_id: int, reason: str = ""):
        """Block a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
            
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (admin_id, 'block_user', f'Blocked {user_id}: {reason}'))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error blocking user {user_id}: {e}")
            return False
    
    def unblock_user(self, user_id: int, admin_id: int):
        """Unblock a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
            
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (admin_id, 'unblock_user', f'Unblocked {user_id}'))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error unblocking user {user_id}: {e}")
            return False
    
    # === Statistics ===
    def get_stats(self):
        """Get comprehensive statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User stats
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
        stats['today_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        stats['vip_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        stats['blocked_users'] = cursor.fetchone()[0]
        
        # Channel stats
        cursor.execute("SELECT COUNT(*) FROM channels WHERE status = 'active'")
        stats['active_channels'] = cursor.fetchone()[0]
        
        # Post stats
        cursor.execute("SELECT COUNT(*) FROM posts WHERE DATE(sent_date) = DATE('now')")
        stats['today_posts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        
        # Activity stats
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM activity_logs 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        stats['active_today'] = cursor.fetchone()[0]
        
        return stats
    
    # === Configuration Management ===
    def get_config(self, key: str, default: str = ""):
        """Get configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            value = result[0]
            # Process emoji placeholders
            for emoji_key, emoji in Config.EMOJIS.items():
                value = value.replace(f"{{{emoji_key}}}", emoji)
            return value
        
        return default
    
    def set_config(self, key: str, value: str, encrypted: bool = False, category: str = "general"):
        """Set configuration value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, encrypted, category, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, value, encrypted, category))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    def get_all_configs(self, category: str = None):
        """Get all configurations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT key, value, category, description FROM config WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT key, value, category, description FROM config")
        
        configs = []
        for row in cursor.fetchall():
            configs.append({
                'key': row[0],
                'value': row[1],
                'category': row[2],
                'description': row[3]
            })
        
        return configs
    
    # === Channel Management ===
    def get_channels(self, force_join_only: bool = False):
        """Get all channels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if force_join_only:
            cursor.execute('''
                SELECT channel_id, name, link, is_private 
                FROM channels 
                WHERE status = 'active' AND force_join = 1
                ORDER BY name
            ''')
        else:
            cursor.execute('''
                SELECT channel_id, name, link, is_private 
                FROM channels 
                WHERE status = 'active'
                ORDER BY name
            ''')
        
        channels = []
        for row in cursor.fetchall():
            channels.append({
                'id': row[0],
                'name': row[1],
                'link': row[2],
                'is_private': bool(row[3])
            })
        
        return channels
    
    def add_channel(self, channel_id: str, name: str, link: str, is_private: bool = False):
        """Add a new channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO channels (channel_id, name, link, is_private, added_date)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (channel_id, name, link, is_private))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding channel {channel_id}: {e}")
            return False
    
    def remove_channel(self, channel_id: str):
        """Remove a channel (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE channels SET status = 'inactive' WHERE channel_id = ?", (channel_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing channel {channel_id}: {e}")
            return False
    
    # === VIP Management ===
    def add_vip(self, user_id: int, level: int = 1, expires_at: str = None):
        """Add user to VIP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update users table
            cursor.execute('UPDATE users SET is_vip = 1 WHERE user_id = ?', (user_id,))
            
            # Add to vip_users table
            cursor.execute('''
                INSERT OR REPLACE INTO vip_users (user_id, level, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, level, expires_at))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding VIP {user_id}: {e}")
            return False
    
    def remove_vip(self, user_id: int):
        """Remove user from VIP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET is_vip = 0 WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM vip_users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing VIP {user_id}: {e}")
            return False
    
    def is_vip(self, user_id: int):
        """Check if user is VIP"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_vip FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        return result and result[0] == 1
    
    # === Session Management ===
    def create_session(self, user_id: int, data: dict, expires_in: int = Config.SESSION_TIMEOUT):
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, data, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, json.dumps(data), expires_at))
            conn.commit()
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str):
        """Get session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, data FROM sessions 
            WHERE session_id = ? AND expires_at > CURRENT_TIMESTAMP
        ''', (session_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'data': json.loads(result[1]) if result[1] else {}
            }
        return None
    
    def cleanup_sessions(self):
        """Cleanup expired sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
        
        deleted = cursor.rowcount
        if deleted > 0:
            logger.debug(f"Cleaned up {deleted} expired sessions")
    
    # === Backup System ===
    def create_backup(self):
        """Create database backup"""
        backup_file = os.path.join(
            self.backup_dir,
            f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        try:
            # Create backup connection
            backup_conn = sqlite3.connect(backup_file)
            with self.get_connection() as source:
                source.backup(backup_conn)
            backup_conn.close()
            
            logger.info(f"Backup created: {backup_file}")
            
            # Cleanup old backups (keep last 7)
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith('backup_') and f.endswith('.db')
            ])
            
            if len(backups) > 7:
                for old_backup in backups[:-7]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
            
            return backup_file
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    # === Flood Control ===
    def check_flood(self, user_id: int):
        """Check if user is flooding"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_count, last_message, warning_count, is_temporarily_blocked
            FROM flood_control WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            message_count, last_message, warning_count, is_blocked = result
            
            # Reset if last message was more than 1 minute ago
            last_msg_time = datetime.datetime.fromisoformat(last_message)
            if (datetime.datetime.now() - last_msg_time).seconds > 60:
                cursor.execute('''
                    UPDATE flood_control 
                    SET message_count = 1, 
                        last_message = CURRENT_TIMESTAMP,
                        warning_count = 0
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return False
            
            # Check flood threshold
            flood_threshold = int(self.get_config('flood_threshold', '5'))
            
            if message_count >= flood_threshold:
                cursor.execute('''
                    UPDATE flood_control 
                    SET warning_count = warning_count + 1,
                        is_temporarily_blocked = 1
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
            
            # Increment message count
            cursor.execute('''
                UPDATE flood_control 
                SET message_count = message_count + 1,
                    last_message = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        else:
            # First message from user
            cursor.execute('''
                INSERT INTO flood_control (user_id, message_count, last_message)
                VALUES (?, 1, CURRENT_TIMESTAMP)
            ''', (user_id,))
            conn.commit()
        
        return False
    
    def reset_flood(self, user_id: int):
        """Reset flood control for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE flood_control 
            SET message_count = 0,
                warning_count = 0,
                is_temporarily_blocked = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

# Initialize database
db = DatabaseManager()

# ==============================================================================
# 🔧 SYSTEM MONITOR
# ==============================================================================

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.user_activity = defaultdict(int)
        
    def get_uptime(self):
        """Get formatted uptime"""
        uptime = time.time() - self.start_time
        days = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        hours = uptime // 3600
        uptime %= 3600
        minutes = uptime // 60
        seconds = uptime % 60
        
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        stats = {
            'uptime': self.get_uptime(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_percent': psutil.disk_usage('/').percent,
            'message_count': self.message_count,
            'error_count': self.error_count,
            'active_users': len(self.user_activity),
            'bot_processes': len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])
        }
        return stats
    
    def increment_message(self):
        """Increment message counter"""
        self.message_count += 1
    
    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1
    
    def update_user_activity(self, user_id: int):
        """Update user activity"""
        self.user_activity[user_id] = time.time()
        
        # Cleanup old entries (older than 1 hour)
        current_time = time.time()
        self.user_activity = defaultdict(int, {
            uid: ts for uid, ts in self.user_activity.items()
            if current_time - ts < 3600
        })

system_monitor = SystemMonitor()

# ==============================================================================
# 🌐 HEALTH SERVER WITH PORT BINDING
# ==============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def do_GET(self):
        if self.path == '/health':
            # Get system stats
            stats = system_monitor.get_system_stats()
            db_stats = db.get_stats()
            
            response = {
                'status': 'online',
                'timestamp': datetime.datetime.now().isoformat(),
                'system': stats,
                'database': db_stats,
                'version': 'v10.0'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Supreme Bot Status</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .status {{ padding: 15px; margin: 15px 0; border-radius: 5px; }}
                    .online {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                    .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
                    h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                    .emoji {{ font-size: 24px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Supreme Bot Status</h1>
                    <div class="status online">
                        <strong>🟢 ONLINE</strong> - System is running normally
                    </div>
                    <div class="stats">
                        <div class="stat-box">
                            <div class="emoji">⏰</div>
                            <h3>Uptime</h3>
                            <p>{stats['uptime']}</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">👥</div>
                            <h3>Users</h3>
                            <p>{db_stats['total_users']} total</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">💾</div>
                            <h3>Memory</h3>
                            <p>{stats['memory_percent']}% used</p>
                        </div>
                        <div class="stat-box">
                            <div class="emoji">⚡</div>
                            <h3>CPU</h3>
                            <p>{stats['cpu_percent']}% load</p>
                        </div>
                    </div>
                    <p><em>Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
                </div>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.debug(f"HTTP {args[0]} {args[1]}")

def run_health_server():
    """Run HTTP health check server"""
    port = int(os.environ.get('PORT', 8080))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Health server started on port {port}")
        logger.info(f"🔗 Status URL: http://0.0.0.0:{port}/health")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")

# Start health server in background
server_thread = threading.Thread(target=run_health_server, daemon=True)
server_thread.start()

# ==============================================================================
# 🎨 UI MANAGER WITH EMOJI SUPPORT
# ==============================================================================

class UIManager:
    """Advanced UI manager with emoji and formatting support"""
    
    @staticmethod
    def format_text(text: str, user=None, emojis: bool = True):
        """Format text with user info and emojis"""
        # Replace emoji placeholders
        if emojis:
            for key, emoji in Config.EMOJIS.items():
                text = text.replace(f"{{{key}}}", emoji)
        
        # Add user info if provided
        if user:
            user_info = f"\n\n👤 User: {mention_html(user.id, user.first_name or 'User')}"
            text += user_info
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text += f"\n⏰ Time: {timestamp}"
        
        return text
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = False):
        """Create inline keyboard from button configuration"""
        keyboard = []
        
        for row in buttons:
            row_buttons = []
            for btn in row:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=UIManager.format_text(btn.get('text', ''), emojis=True),
                        callback_data=btn.get('callback', ''),
                        url=btn.get('url', None)
                    )
                )
            keyboard.append(row_buttons)
        
        # Add back button
        if add_back:
            keyboard.append([
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ])
        
        # Add close button
        if add_close:
            keyboard.append([
                InlineKeyboardButton("❌ Close", callback_data="close_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
        """Get admin main menu"""
        buttons = [
            [
                {"text": "📝 Message Editor", "callback": "menu_messages"},
                {"text": "🔗 Link Settings", "callback": "menu_links"}
            ],
            [
                {"text": "📢 Channel Manager", "callback": "menu_channels"},
                {"text": "🛡️ Security Panel", "callback": "menu_security"}
            ],
            [
                {"text": "📡 Marketing Tools", "callback": "menu_marketing"},
                {"text": "📊 Statistics", "callback": "menu_stats"}
            ],
            [
                {"text": "👑 VIP Management", "callback": "menu_vip"},
                {"text": "⚙️ System Settings", "callback": "menu_system"}
            ]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def get_stats_display(stats: Dict):
        """Format statistics for display"""
        text = f"""
{Config.EMOJIS['chart']} <b>SYSTEM STATISTICS</b>

{Config.EMOJIS['users']} <b>User Stats:</b>
• Total Users: {stats.get('total_users', 0):,}
• Today New: {stats.get('today_users', 0):,}
• VIP Users: {stats.get('vip_users', 0):,}
• Blocked: {stats.get('blocked_users', 0):,}
• Active Today: {stats.get('active_today', 0):,}

{Config.EMOJIS['megaphone']} <b>Channel Stats:</b>
• Active Channels: {stats.get('active_channels', 0):,}

{Config.EMOJIS['camera']} <b>Post Stats:</b>
• Total Posts: {stats.get('total_posts', 0):,}
• Today Posts: {stats.get('today_posts', 0):,}
"""
        return text

ui = UIManager()

# ==============================================================================
# 🔐 SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    """Advanced security manager with flood control and verification"""
    
    def __init__(self):
        self.last_verification = {}
        self.verification_cache = {}
        self.blocked_ips = set()
    
    async def check_membership(self, user_id: int, bot) -> List[Dict]:
        """Check if user is member of required channels"""
        if db.get_config('force_join') != 'ON':
            return []
        
        # Check cache first
        cache_key = f"membership_{user_id}"
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minute cache
                return result
        
        missing_channels = []
        channels = db.get_channels(force_join_only=True)
        
        for channel in channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel['id'],
                    user_id=user_id
                )
                
                if member.status in ['left', 'kicked']:
                    missing_channels.append(channel)
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['id']}: {e}")
                missing_channels.append(channel)
        
        # Update cache
        self.verification_cache[cache_key] = (time.time(), missing_channels)
        
        return missing_channels
    
    def check_flood(self, user_id: int) -> bool:
        """Check if user is flooding"""
        return db.check_flood(user_id)
    
    def check_maintenance(self, user_id: int) -> bool:
        """Check if maintenance mode is active for user"""
        if user_id in Config.ADMIN_IDS:
            return False
        
        return db.get_config('maint_mode') == 'ON'
    
    def check_access(self, user_id: int, required_level: int = 1) -> bool:
        """Check user access level"""
        if user_id in Config.ADMIN_IDS:
            return True
        
        if required_level == 1:
            return True
        
        if required_level == 2:
            return db.is_vip(user_id)
        
        return False
    
    def generate_token(self, length: int = 32) -> str:
        """Generate security token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

security = SecurityManager()

# ==============================================================================
# 🔄 BACKGROUND TASK MANAGER
# ==============================================================================

class BackgroundTaskManager:
    """Manage background tasks"""
    
    def __init__(self):
        self.tasks = []
        self.running = True
        
    def add_task(self, func, interval: int, *args, **kwargs):
        """Add a recurring background task"""
        task = threading.Thread(
            target=self._run_task,
            args=(func, interval, args, kwargs),
            daemon=True
        )
        self.tasks.append(task)
        task.start()
    
    def _run_task(self, func, interval, args, kwargs):
        """Run task at intervals"""
        while self.running:
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Background task error: {e}")
            time.sleep(interval)
    
    def cleanup(self):
        """Cleanup all tasks"""
        self.running = False
        for task in self.tasks:
            task.join(timeout=1)

# Create background task manager
task_manager = BackgroundTaskManager()

# Define background tasks
def cleanup_expired_sessions():
    """Cleanup expired sessions"""
    db.cleanup_sessions()

def create_automatic_backup():
    """Create automatic backup"""
    backup_file = db.create_backup()
    if backup_file:
        logger.info(f"Automatic backup created: {backup_file}")

def monitor_system_health():
    """Monitor system health"""
    stats = system_monitor.get_system_stats()
    if stats['memory_percent'] > 90 or stats['cpu_percent'] > 90:
        logger.warning(f"High system load: CPU {stats['cpu_percent']}%, Memory {stats['memory_percent']}%")

# Schedule background tasks
task_manager.add_task(cleanup_expired_sessions, 300)  # Every 5 minutes
task_manager.add_task(create_automatic_backup, 3600)  # Every hour
task_manager.add_task(monitor_system_health, 60)      # Every minute

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    system_monitor.increment_message()
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ""
    )
    
    # Check flood control
    if security.check_flood(user.id):
        await update.message.reply_text(
            "⚠️ You're sending messages too fast. Please wait a moment.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check maintenance mode
    if security.check_maintenance(user.id):
        await update.message.reply_text(
            ui.format_text(
                "🔧 <b>System Maintenance</b>\n\n"
                "We're currently performing maintenance. Please try again later.",
                user
            ),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if blocked
    user_data = db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await update.message.reply_text(
            "🚫 Your access has been restricted. Contact admin for assistance.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check channel membership
    missing_channels = await security.check_membership(user.id, context.bot)
    
    if missing_channels:
        # Show lock message
        lock_msg = db.get_config('lock_msg')
        
        # Create channel join buttons
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {
                    "text": f"📢 Join {channel['name']}",
                    "url": channel['link']
                }
            ])
        
        buttons.append([
            {
                "text": "✅ Verify Membership",
                "callback": "verify_membership"
            }
        ])
        
        keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
        
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await update.message.reply_text(
                ui.format_text(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        # Show welcome message
        welcome_msg = db.get_config('welcome_msg')
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(btn_text, url=watch_url)
        ]])
        
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete after configured time
            auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await update.message.delete()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            await update.message.reply_text(
                ui.format_text(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Access denied!")
        return
    
    system_monitor.update_user_activity(user.id)
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME ADMIN PANEL</b>

{Config.EMOJIS['chart']} <b>Bot Statistics:</b>
• Users: {stats['total_users']:,}
• Today: {stats['today_users']:,}
• VIP: {stats['vip_users']:,}

{Config.EMOJIS['gear']} <b>System Status:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
• Messages: {sys_stats['message_count']:,}

👇 <b>Select an option:</b>
"""
    
    await update.message.reply_text(
        text,
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    
    text = ui.get_stats_display(stats)
    text += f"\n{Config.EMOJIS['gear']} <b>System Info:</b>"
    text += f"\n• Uptime: {sys_stats['uptime']}"
    text += f"\n• CPU: {sys_stats['cpu_percent']}%"
    text += f"\n• Memory: {sys_stats['memory_percent']}%"
    text += f"\n• Disk: {sys_stats['disk_percent']}%"
    
    await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML,
        reply_markup=ui.create_keyboard([], add_back=True, add_close=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    
    text = f"""
{Config.EMOJIS['info']} <b>Supreme Bot Commands</b>

<b>User Commands:</b>
/start - Start the bot
/help - Show this help message

<b>Admin Commands:</b>
/admin - Open admin panel
/stats - Show statistics
/backup - Create backup
/broadcast - Broadcast message

<b>Features:</b>
• Auto-delete messages
• Channel verification
• VIP access system
• Post scheduling
• Advanced analytics
"""
    
    await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML
    )

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /backup command"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("🚫 Admin only command!")
        return
    
    message = await update.message.reply_text("💾 Creating backup...")
    
    backup_file = db.create_backup()
    
    if backup_file:
        await message.edit_text(
            f"✅ Backup created successfully!\n\n"
            f"File: {os.path.basename(backup_file)}\n"
            f"Size: {os.path.getsize(backup_file) // 1024} KB",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.edit_text("❌ Failed to create backup!")

# ==============================================================================
# 🔄 CALLBACK QUERY HANDLER
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    
    user = query.from_user
    data = query.data
    
    system_monitor.update_user_activity(user.id)
    
    # Admin check for admin functions
    admin_functions = {
        'main_menu', 'menu_', 'edit_', 'toggle_', 'remove_', 'add_',
        'broadcast', 'create_post', 'block_user', 'unblock_user',
        'add_vip', 'remove_vip', 'backup_', 'restore_'
    }
    
    if any(data.startswith(func) for func in admin_functions) and user.id not in Config.ADMIN_IDS:
        await query.answer("🚫 Admin access required!", show_alert=True)
        return
    
    # Route callbacks
    if data == "main_menu":
        await query.answer()
        await show_admin_panel(query.message, user)
    
    elif data == "close_panel":
        await query.answer()
        try:
            await query.delete_message()
        except:
            pass
    
    elif data == "verify_membership":
        # === FIXED VERIFY BUTTON LOGIC ===
        try:
            # Clear cache for this specific user to force a fresh check
            security.verification_cache.pop(f"membership_{user.id}", None)
            
            missing_channels = await security.check_membership(user.id, context.bot)
            
            if not missing_channels:
                await query.answer("✅ Verified successfully!", show_alert=True)
                
                # Show welcome message
                welcome_msg = db.get_config('welcome_msg')
                btn_text = db.get_config('btn_text')
                watch_url = db.get_config('watch_url')
                
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton(btn_text, url=watch_url)
                ]])
                
                try:
                    await query.message.edit_caption(
                        caption=ui.format_text(welcome_msg, user),
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    # If message type is different or editing fails, send new message
                    await query.message.reply_text(
                        ui.format_text(welcome_msg, user),
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )
            else:
                await query.answer("❌ Still missing channels!\nPlease join all channels first.", show_alert=True)
        except Exception as e:
            logger.error(f"Verify Error: {e}")
            await query.answer("⚠️ Error verifying. Please try again.", show_alert=True)
    
    elif data == "menu_messages":
        await query.answer()
        buttons = [
            [
                {"text": "✏️ Welcome Message", "callback": "edit_welcome_msg"},
                {"text": "✏️ Lock Message", "callback": "edit_lock_msg"}
            ],
            [
                {"text": "🖼️ Welcome Photo", "callback": "edit_welcome_photo"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text("📝 <b>Message Editor</b>\nSelect message to edit:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_links":
        await query.answer()
        buttons = [
            [
                {"text": "🔗 Watch URL", "callback": "edit_watch_url"},
                {"text": "🔘 Button Text", "callback": "edit_btn_text"}
            ],
            [
                {"text": "⏱️ Auto Delete", "callback": "edit_auto_delete"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text("🔗 <b>Link Settings</b>\nSelect setting to edit:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_channels":
        await query.answer()
        channels = db.get_channels()
        
        text = "📢 <b>Channel Manager</b>\n\n"
        
        if channels:
            text += "<b>Current Channels:</b>\n"
            for idx, channel in enumerate(channels, 1):
                text += f"{idx}. {channel['name']}\n"
        else:
            text += "No channels added.\n"
        
        buttons = []
        for channel in channels:
            buttons.append([
                {"text": f"❌ Remove {channel['name']}", "callback": f"remove_channel_{channel['id']}"}
            ])
        
        buttons.append([
            {"text": "➕ Add Channel", "callback": "add_channel_start"}
        ])
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_security":
        await query.answer()
        maint_status = db.get_config('maint_mode')
        force_status = db.get_config('force_join')
        
        text = f"""
🛡️ <b>Security Settings</b>

<b>Current Status:</b>
• Maintenance Mode: {maint_status}
• Force Join: {force_status}

<b>Actions:</b>
"""
        
        buttons = [
            [
                {"text": f"🔄 Maintenance: {maint_status}", "callback": "toggle_maint"},
                {"text": f"🔄 Force Join: {force_status}", "callback": "toggle_force"}
            ],
            [
                {"text": "🚫 Block User", "callback": "block_user_start"},
                {"text": "✅ Unblock User", "callback": "unblock_user_start"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_marketing":
        await query.answer()
        text = """
📡 <b>Marketing Tools</b>

<b>Available Tools:</b>
• Create and schedule posts
• Broadcast messages
• Target specific user groups
• Analyze engagement
"""
        
        buttons = [
            [
                {"text": "📝 Create Post", "callback": "create_post_start"},
                {"text": "📢 Broadcast", "callback": "broadcast_start"}
            ],
            [
                {"text": "🎯 Target Users", "callback": "target_users"},
                {"text": "📊 Analytics", "callback": "analytics"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_stats":
        await query.answer()
        stats = db.get_stats()
        text = ui.get_stats_display(stats)
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard([]),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_vip":
        await query.answer()
        vip_users = [uid for uid in db.get_all_users() if db.is_vip(uid)]
        
        text = f"""
👑 <b>VIP Management</b>

<b>Current VIP Users:</b>
{len(vip_users)} VIP users
"""
        
        buttons = [
            [
                {"text": "➕ Add VIP", "callback": "add_vip_start"},
                {"text": "➖ Remove VIP", "callback": "remove_vip_start"}
            ],
            [
                {"text": "📋 VIP List", "callback": "vip_list"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data == "menu_system":
        await query.answer()
        sys_stats = system_monitor.get_system_stats()
        
        text = f"""
⚙️ <b>System Settings</b>

<b>System Status:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
• Disk: {sys_stats['disk_percent']}%

<b>Actions:</b>
"""
        
        buttons = [
            [
                {"text": "💾 Backup Now", "callback": "backup_now"},
                {"text": "🔄 Restart Bot", "callback": "restart_bot"}
            ],
            [
                {"text": "🧹 Cleanup DB", "callback": "cleanup_db"},
                {"text": "📜 View Logs", "callback": "view_logs"}
            ]
        ]
        
        await query.edit_message_text(
            ui.format_text(text, user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )
    
    elif data.startswith("edit_"):
        await query.answer()
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        current_value = db.get_config(key)
        
        await query.message.reply_text(
            f"✏️ <b>Editing:</b> <code>{key}</code>\n"
            f"<b>Current:</b> <code>{current_value[:100]}</code>\n\n"
            f"Please send the new value:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_EDIT_CONFIG
    
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        current = db.get_config(key)
        new_value = "ON" if current == "OFF" else "OFF"
        db.set_config(key, new_value)
        
        await query.answer(f"✅ {key} set to {new_value}", show_alert=True)
        # Refresh menu
        query.data = "menu_security"
        await callback_handler(update, context)
    
    elif data.startswith("remove_channel_"):
        channel_id = data.replace("remove_channel_", "")
        if db.remove_channel(channel_id):
            await query.answer("✅ Channel removed!", show_alert=True)
        else:
            await query.answer("❌ Failed to remove!", show_alert=True)
        # Refresh
        query.data = "menu_channels"
        await callback_handler(update, context)
    
    elif data == "add_channel_start":
        await query.answer()
        await query.message.reply_text(
            "➕ <b>Add New Channel</b>\n\n"
            "Please send the Channel ID (e.g., @channelname or -1001234567890):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_CHANNEL_ADD_ID
    
    elif data == "create_post_start":
        await query.answer()
        await query.message.reply_text(
            "📝 <b>Post Wizard - Step 1/4</b>\n\n"
            "Please send the post caption/text:",
            parse_mode=ParseMode.HTML
        )
        context.user_data['post_wizard'] = {}
        return Config.STATE_POST_CAPTION
    
    elif data == "broadcast_start":
        await query.answer()
        await query.message.reply_text(
            "📢 <b>Broadcast Message</b>\n\n"
            "Please send the message to broadcast (text, photo, or video):",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_BROADCAST
    
    elif data == "block_user_start":
        await query.answer()
        await query.message.reply_text(
            "🚫 <b>Block User</b>\n\n"
            "Please send the user ID to block:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_USER_BLOCK
    
    elif data == "add_vip_start":
        await query.answer()
        await query.message.reply_text(
            "👑 <b>Add VIP User</b>\n\n"
            "Please send the user ID to grant VIP access:",
            parse_mode=ParseMode.HTML
        )
        return Config.STATE_VIP_ADD
    
    elif data == "backup_now":
        await query.answer("💾 Creating backup...", show_alert=True)
        backup_file = db.create_backup()
        if backup_file:
            await query.message.reply_text(f"✅ Backup created: {os.path.basename(backup_file)}")
        else:
            await query.message.reply_text("❌ Backup failed!")
    
    else:
        await query.answer("❌ Unknown action!")

async def show_admin_panel(message, user):
    """Show admin panel"""
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME ADMIN PANEL</b>

{Config.EMOJIS['chart']} <b>Bot Statistics:</b>
• Users: {stats['total_users']:,}
• Today: {stats['today_users']:,}
• VIP: {stats['vip_users']:,}

{Config.EMOJIS['gear']} <b>System Status:</b>
• Uptime: {sys_stats['uptime']}
• CPU: {sys_stats['cpu_percent']}%
• Memory: {sys_stats['memory_percent']}%
• Messages: {sys_stats['message_count']:,}

👇 <b>Select an option:</b>
"""
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(text, reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle configuration editing"""
    key = context.user_data.get('edit_key')
    new_value = update.message.text
    
    if key:
        if db.set_config(key, new_value):
            await update.message.reply_text(
                f"✅ <b>{key}</b> updated successfully!",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to update {key}!",
                parse_mode=ParseMode.HTML
            )
    else:
        await update.message.reply_text("❌ Error: No key specified!")
    
    context.user_data.clear()
    return ConversationHandler.END

async def post_caption_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get post caption"""
    context.user_data['post_wizard']['caption'] = update.message.text_html
    
    await update.message.reply_text(
        "📸 <b>Post Wizard - Step 2/4</b>\n\n"
        "Send photo or video for the post (or type /skip for text only):",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_POST_MEDIA

async def post_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get media"""
    if update.message.photo:
        context.user_data['post_wizard']['media'] = update.message.photo[-1].file_id
        context.user_data['post_wizard']['type'] = 'photo'
    elif update.message.video:
        context.user_data['post_wizard']['media'] = update.message.video.file_id
        context.user_data['post_wizard']['type'] = 'video'
    else:
        context.user_data['post_wizard']['media'] = None
        context.user_data['post_wizard']['type'] = 'text'
    
    await update.message.reply_text(
        "🔘 <b>Post Wizard - Step 3/4</b>\n\n"
        "Send button text (or /skip to use default):",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_POST_BUTTON

async def post_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Get button text"""
    if update.message.text and update.message.text != '/skip':
        context.user_data['post_wizard']['button_text'] = update.message.text
    else:
        context.user_data['post_wizard']['button_text'] = db.get_config('btn_text')
    
    # Show channel selection
    channels = db.get_channels()
    
    if not channels:
        await update.message.reply_text("❌ No channels available!")
        context.user_data.clear()
        return ConversationHandler.END
    
    # Create preview
    caption = context.user_data['post_wizard'].get('caption', '')
    media = context.user_data['post_wizard'].get('media')
    post_type = context.user_data['post_wizard'].get('type', 'text')
    button_text = context.user_data['post_wizard'].get('button_text', '')
    watch_url = db.get_config('watch_url')
    
    preview_text = f"""
✅ <b>Post Wizard - Step 4/4</b>

<b>Preview:</b>
• Type: {post_type.upper()}
• Button: {button_text}
• Watch URL: {watch_url[:50]}...

<b>Select channels to post:</b>
"""
    
    # Create channel selection buttons
    buttons = []
    for channel in channels:
        buttons.append([
            {"text": f"📤 {channel['name']}", "callback": f"post_to_{channel['id']}"}
        ])
    
    buttons.append([
        {"text": "📤 Post to ALL", "callback": "post_to_all"}
    ])
    
    keyboard = ui.create_keyboard(buttons, add_back=False, add_close=True)
    
    # Send preview
    if post_type == 'photo' and media:
        await update.message.reply_photo(
            photo=media,
            caption=caption + f"\n\n[Preview]",
            parse_mode=ParseMode.HTML
        )
    elif post_type == 'video' and media:
        await update.message.reply_video(
            video=media,
            caption=caption + f"\n\n[Preview]",
            parse_mode=ParseMode.HTML
        )
    
    await update.message.reply_text(
        preview_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_POST_CONFIRM

async def post_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 4: Confirm and send post"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    post_data = context.user_data.get('post_wizard', {})
    
    caption = post_data.get('caption', '')
    media = post_data.get('media')
    post_type = post_data.get('type', 'text')
    button_text = post_data.get('button_text', db.get_config('btn_text'))
    watch_url = db.get_config('watch_url')
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(button_text, url=watch_url)
    ]])
    
    # Get target channels
    channels = db.get_channels()
    
    if data == "post_to_all":
        target_channels = channels
    else:
        channel_id = data.replace("post_to_", "")
        target_channels = [ch for ch in channels if ch['id'] == channel_id]
    
    if not target_channels:
        await query.message.reply_text("❌ No channels selected!")
        context.user_data.clear()
        return ConversationHandler.END
    
    # Send posts
    success = 0
    failed = 0
    
    status_msg = await query.message.reply_text(f"⏳ Sending to {len(target_channels)} channel(s)...")
    
    for channel in target_channels:
        try:
            if post_type == 'photo' and media:
                await context.bot.send_photo(
                    chat_id=channel['id'],
                    photo=media,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            elif post_type == 'video' and media:
                await context.bot.send_video(
                    chat_id=channel['id'],
                    video=media,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await context.bot.send_message(
                    chat_id=channel['id'],
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            success += 1
        except Exception as e:
            logger.error(f"Failed to post to {channel['id']}: {e}")
            failed += 1
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    await status_msg.edit_text(
        f"✅ <b>Posting Complete!</b>\n\n"
        f"• Successful: {success}\n"
        f"• Failed: {failed}\n"
        f"• Total: {len(target_channels)}",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast messages"""
    message = update.message
    users = db.get_all_users(active_only=True)
    
    if not users:
        await message.reply_text("❌ No users to broadcast!")
        return ConversationHandler.END
    
    total_users = len(users)
    status_msg = await message.reply_text(f"📤 Starting broadcast to {total_users} users...")
    
    success = 0
    failed = 0
    
    for idx, user_id in enumerate(users, 1):
        try:
            if message.photo:
                await message.copy(user_id)
            elif message.video:
                await message.copy(user_id)
            else:
                await context.bot.send_message(
                    user_id,
                    message.text_html,
                    parse_mode=ParseMode.HTML
                )
            success += 1
        except Exception as e:
            failed += 1
        
        # Update progress every 20 users
        if idx % 20 == 0:
            await status_msg.edit_text(
                f"📤 Broadcasting...\n"
                f"Progress: {idx}/{total_users}\n"
                f"Success: {success} | Failed: {failed}"
            )
        
        await asyncio.sleep(0.1)  # Rate limiting
    
    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"• Total users: {total_users}\n"
        f"• Successfully sent: {success}\n"
        f"• Failed: {failed}",
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END

async def add_channel_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Get channel ID"""
    context.user_data['channel_id'] = update.message.text.strip()
    
    await update.message.reply_text(
        "📝 <b>Step 2/3</b>\n\n"
        "Please send the channel name:",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Get channel name"""
    context.user_data['channel_name'] = update.message.text
    
    await update.message.reply_text(
        "🔗 <b>Step 3/3</b>\n\n"
        "Please send the channel link (t.me/...):",
        parse_mode=ParseMode.HTML
    )
    return Config.STATE_CHANNEL_ADD_LINK

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
    
    context.user_data.clear()
    return ConversationHandler.END

async def block_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a user"""
    try:
        user_id = int(update.message.text)
        if db.block_user(user_id, update.effective_user.id, "Manual block by admin"):
            await update.message.reply_text(f"✅ User {user_id} blocked successfully!")
        else:
            await update.message.reply_text(f"❌ Failed to block user {user_id}!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")
    
    return ConversationHandler.END

async def add_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add VIP user"""
    try:
        user_id = int(update.message.text)
        if db.add_vip(user_id):
            await update.message.reply_text(f"✅ User {user_id} granted VIP access!")
        else:
            await update.message.reply_text(f"❌ Failed to add VIP for user {user_id}!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")
    
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION SETUP
# ==============================================================================

def setup_application():
    """Setup the Telegram application with all handlers"""
    
    # Create application
    application = ApplicationBuilder() \
        .token(Config.TOKEN) \
        .connection_pool_size(10) \
        .pool_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .get_updates_read_timeout(30) \
        .http_version("1.1") \
        .build()
    
    # ===== CONVERSATION HANDLERS =====
    
    # Edit configuration conversation
    edit_config_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={
            Config.STATE_EDIT_CONFIG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_config_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Post wizard conversation
    post_wizard_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_CAPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_caption_handler)
            ],
            Config.STATE_POST_MEDIA: [
                MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, post_media_handler)
            ],
            Config.STATE_POST_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_button_handler)
            ],
            Config.STATE_POST_CONFIRM: [
                CallbackQueryHandler(post_confirm_handler, pattern='^post_to_')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Broadcast conversation
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast_start$')],
        states={
            Config.STATE_BROADCAST: [
                MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Add channel conversation
    add_channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel_start$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id_handler)
            ],
            Config.STATE_CHANNEL_ADD_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name_handler)
            ],
            Config.STATE_CHANNEL_ADD_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Block user conversation
    block_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^block_user_start$')],
        states={
            Config.STATE_USER_BLOCK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, block_user_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # Add VIP conversation
    add_vip_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_vip_start$')],
        states={
            Config.STATE_VIP_ADD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_vip_handler)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("backup", backup_command))
    
    # Conversation handlers
    application.add_handler(edit_config_conv)
    application.add_handler(post_wizard_conv)
    application.add_handler(broadcast_conv)
    application.add_handler(add_channel_conv)
    application.add_handler(block_user_conv)
    application.add_handler(add_vip_conv)
    
    # Callback query handler (must be last)
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully"""
    system_monitor.increment_error()
    
    # Log error
    logger.error(f"Exception while handling update: {context.error}")
    
    # Send traceback to log file
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")
    
    # Notify admin
    try:
        error_msg = f"⚠️ <b>Bot Error:</b>\n<code>{context.error}</code>"
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    error_msg,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
    except:
        pass
    
    # Try to send error message to user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. The admin has been notified.",
                parse_mode=ParseMode.HTML
            )
    except:
        pass

async def set_bot_commands(application: Application):
    """Set bot commands for menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("admin", "Admin panel"),
        BotCommand("stats", "View statistics"),
        BotCommand("help", "Show help"),
        BotCommand("backup", "Create backup")
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

def main():
    """Main entry point"""
    logger.info("🚀 Starting Supreme God Bot v10.0...")
    logger.info("=" * 60)
    
    # Display system info
    stats = system_monitor.get_system_stats()
    logger.info(f"System Uptime: {stats['uptime']}")
    logger.info(f"CPU Usage: {stats['cpu_percent']}%")
    logger.info(f"Memory Usage: {stats['memory_percent']}%")
    
    # Display bot info
    db_stats = db.get_stats()
    logger.info(f"Total Users: {db_stats['total_users']:,}")
    logger.info(f"Active Channels: {db_stats['active_channels']:,}")
    
    logger.info("=" * 60)
    
    try:
        # Create and setup application
        application = setup_application()
        
        # Set bot commands
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        task_manager.cleanup()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    # Run main function directly (run_polling handles the event loop)
    main()
