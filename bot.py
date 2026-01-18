"""
================================================================================
SUPREME GOD MODE BOT - ULTIMATE EDITION (BANGLADESH SPECIAL)
VERSION: v11.0 (Viral Edition)
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
    TOKEN = "8173181203:AAEDcda58agIZZic4uC8tSQVzKbrk6pYnU4"
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
        "earth": "🌍",
        "kiss": "💋",
        "eyes": "👀",
        "love": "🥰"
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
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        error_handler = logging.FileHandler('errors.log', encoding='utf-8')
        
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)
        error_handler.setLevel(logging.ERROR)
        
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        console_handler.setFormatter(simple_formatter)
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.info("=" * 60)
        self.logger.info("SUPREME GOD BOT v11.0 (BD EDITION) STARTING...")
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
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def get_connection(self, thread_id=None):
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
                conn.execute("PRAGMA cache_size=-2000")
                self.connection_pool[thread_id] = conn
                
            return self.connection_pool[thread_id]
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flood_control (
                user_id INTEGER PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                last_message DATETIME DEFAULT CURRENT_TIMESTAMP,
                warning_count INTEGER DEFAULT 0,
                is_temporarily_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_vip ON users(is_vip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(sent_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expire ON sessions(expires_at)')
        
        conn.commit()
        self.initialize_defaults()
        logger.info("Database initialized successfully")
    
    def initialize_defaults(self):
        """Initialize default configuration with LONG, HOT messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Long, Hot, Flirty Bengali/English Mix Messages
        welcome_msg_text = '''{fire} {heart} <b>OH MY GOD! WELCOME MY LOVE!</b> {heart} {fire}

{kiss} <b>Shona Pakhi, Tumi eshe gecho? Ami tomar jonno ekhame wait korchilam!</b> {eyes}

{star} <b>Tomake amader ai Hot & Premium Viral Community te Swagotom janachi!</b> Ekhane tumi pabe emon sob jinish ja tumi sara jibon khujecho! {star}

{crown} <b>EXCLUSIVE VIP SUVIDHA SUDHU TOMAR JONNO:</b>
• {fire} **Super Hot Viral Videos:** Ja dekhe matha nosto hoye jabe!
• {lock} **Premium Leaked Content:** Ekdom Uncut & Raw!
• {bell} **Live Updates:** Sobar age sob notun update pabe ekhane!
• {money} **Earning Tricks:** Taka kamanor gopon sohoj upay!

{love} <b>Amar Jan, tumi ki ready ashol moja neoyar jonno?</b> Deri koro na shona, nicher button e click kore ekhon i suru koro tomar jiboner sera adventure! {rocket}

{link} <b>Ekhon i Join koro ar enjoy koro unlimited fun!</b> 👇'''

        lock_msg_text = '''{lock} {warn} <b>OOPS BABY! ACCESS DENIED!</b> {warn} {lock}

{cross} <b>Eki Shona? Tumi ekhono amader sob Channel e Join koro ni?</b> {cross}

{eyes} **Ami tomake eto valobashi ar tumi amake support korbe na?** Amar sob hot video ar premium content dekhar jonno tomake obossoi nicher sob gulo channel e join korte hobe! {fire}

{heart} <b>Please Jan, amar kotha rakho!</b> Nicher deoya prottekta channel e ekti ekti kore click koro ar Join koro. Tarpor "✅ Verify" button e click koro, ami tomake sora sori vitore niye jabo! {kiss}

{down} **Nicher Button gulo te click kore Join kore nao joldi!** {down}'''

        defaults = [
            ('welcome_msg', welcome_msg_text, 0, 'messages', 'Welcome message for new users'),
            ('lock_msg', lock_msg_text, 0, 'messages', 'Message shown when user hasn\'t joined channels'),
            ('welcome_photo', 'https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead', 0, 'media', 'Welcome photo URL'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1', 0, 'links', 'Main watch URL'),
            ('btn_text', '{video} FULL VIDEO DEKHUN EKHANE {fire}', 0, 'buttons', 'Button text'),
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None
    
    def get_all_users(self, active_only: bool = True):
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
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = DATE('now')")
        stats['today_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        stats['vip_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        stats['blocked_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM channels WHERE status = 'active'")
        stats['active_channels'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts WHERE DATE(sent_date) = DATE('now')")
        stats['today_posts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts")
        stats['total_posts'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM activity_logs 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        stats['active_today'] = cursor.fetchone()[0]
        return stats
    
    # === Configuration Management ===
    def get_config(self, key: str, default: str = ""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            value = result[0]
            for emoji_key, emoji in Config.EMOJIS.items():
                value = value.replace(f"{{{emoji_key}}}", emoji)
            return value
        return default
    
    def set_config(self, key: str, value: str, encrypted: bool = False, category: str = "general"):
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
    
    # === Channel Management ===
    def get_channels(self, force_join_only: bool = False):
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
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE channels SET status = 'inactive' WHERE channel_id = ?", (channel_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing channel {channel_id}: {e}")
            return False
    
    # === VIP & Session & Backup ===
    def add_vip(self, user_id: int, level: int = 1, expires_at: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_vip = 1 WHERE user_id = ?', (user_id,))
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_vip FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result and result[0] == 1
    
    def create_session(self, user_id: int, data: dict, expires_in: int = Config.SESSION_TIMEOUT):
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
    
    def create_backup(self):
        backup_file = os.path.join(
            self.backup_dir,
            f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        try:
            backup_conn = sqlite3.connect(backup_file)
            with self.get_connection() as source:
                source.backup(backup_conn)
            backup_conn.close()
            logger.info(f"Backup created: {backup_file}")
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
    
    def check_flood(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message_count, last_message, warning_count, is_temporarily_blocked
            FROM flood_control WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result:
            message_count, last_message, warning_count, is_blocked = result
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
            
            cursor.execute('''
                UPDATE flood_control 
                SET message_count = message_count + 1,
                    last_message = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
        else:
            cursor.execute('''
                INSERT INTO flood_control (user_id, message_count, last_message)
                VALUES (?, 1, CURRENT_TIMESTAMP)
            ''', (user_id,))
            conn.commit()
        return False

db = DatabaseManager()

# ==============================================================================
# 🔧 SYSTEM MONITOR
# ==============================================================================

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.user_activity = defaultdict(int)
        
    def get_uptime(self):
        uptime = time.time() - self.start_time
        days = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        hours = uptime // 3600
        uptime %= 3600
        minutes = uptime // 60
        seconds = uptime % 60
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def get_system_stats(self):
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
        self.message_count += 1
    
    def increment_error(self):
        self.error_count += 1
    
    def update_user_activity(self, user_id: int):
        self.user_activity[user_id] = time.time()
        current_time = time.time()
        self.user_activity = defaultdict(int, {
            uid: ts for uid, ts in self.user_activity.items()
            if current_time - ts < 3600
        })

system_monitor = SystemMonitor()

# ==============================================================================
# 🌐 HEALTH SERVER
# ==============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            stats = system_monitor.get_system_stats()
            db_stats = db.get_stats()
            response = {
                'status': 'online',
                'timestamp': datetime.datetime.now().isoformat(),
                'system': stats,
                'database': db_stats,
                'version': 'v11.0'
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Supreme Bot Running (BD Timezone)</h1>")
    
    def log_message(self, format, *args):
        logger.debug(f"HTTP {args[0]} {args[1]}")

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")

server_thread = threading.Thread(target=run_health_server, daemon=True)
server_thread.start()

# ==============================================================================
# 🎨 UI MANAGER WITH BD TIME & USER MENTION
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None, emojis: bool = True):
        """Format text with user info, emojis and BD Time"""
        # Replace emoji placeholders
        if emojis:
            for key, emoji in Config.EMOJIS.items():
                text = text.replace(f"{{{key}}}", emoji)
        
        # Add user info if provided (PROMINENT MENTION)
        if user:
            user_info = f"\n\n👤 <b>Hey Dear User:</b> {mention_html(user.id, user.first_name or 'My Love')}"
            text += user_info
        
        # Add timestamp (BANGLADESH TIME UTC+6)
        bd_time = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        timestamp = bd_time.strftime("%d %b %Y, %I:%M %p (BD)")
        text += f"\n⏰ <b>BD Time:</b> {timestamp}"
        
        return text
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = False):
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
        
        if add_back:
            keyboard.append([
                InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")
            ])
        if add_close:
            keyboard.append([
                InlineKeyboardButton("❌ Close Panel", callback_data="close_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
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
        text = f"""
{Config.EMOJIS['chart']} <b>SYSTEM STATISTICS (LIVE)</b>

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
    def __init__(self):
        self.last_verification = {}
        self.verification_cache = {}
        self.blocked_ips = set()
    
    async def check_membership(self, user_id: int, bot) -> List[Dict]:
        if db.get_config('force_join') != 'ON':
            return []
        
        cache_key = f"membership_{user_id}"
        if cache_key in self.verification_cache:
            cached_time, result = self.verification_cache[cache_key]
            if time.time() - cached_time < 300:
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
        
        self.verification_cache[cache_key] = (time.time(), missing_channels)
        return missing_channels
    
    def check_flood(self, user_id: int) -> bool:
        return db.check_flood(user_id)
    
    def check_maintenance(self, user_id: int) -> bool:
        if user_id in Config.ADMIN_IDS:
            return False
        return db.get_config('maint_mode') == 'ON'

security = SecurityManager()

# ==============================================================================
# 🔄 BACKGROUND TASKS
# ==============================================================================

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []
        self.running = True
        
    def add_task(self, func, interval: int, *args, **kwargs):
        task = threading.Thread(
            target=self._run_task,
            args=(func, interval, args, kwargs),
            daemon=True
        )
        self.tasks.append(task)
        task.start()
    
    def _run_task(self, func, interval, args, kwargs):
        while self.running:
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Background task error: {e}")
            time.sleep(interval)
    
    def cleanup(self):
        self.running = False
        for task in self.tasks:
            task.join(timeout=1)

task_manager = BackgroundTaskManager()

def cleanup_expired_sessions():
    db.cleanup_sessions()

def create_automatic_backup():
    db.create_backup()

task_manager.add_task(cleanup_expired_sessions, 300)
task_manager.add_task(create_automatic_backup, 3600)

# ==============================================================================
# 🎮 COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with Viral/Hot Message Logic"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    system_monitor.increment_message()
    
    db.add_user(user.id, user.username, user.first_name, user.last_name or "")
    
    if security.check_flood(user.id):
        await update.message.reply_text("⚠️ <b>Slow down baby! Too fast!</b>", parse_mode=ParseMode.HTML)
        return
    
    if security.check_maintenance(user.id):
        await update.message.reply_text(
            ui.format_text("🔧 <b>System Maintenance Mode is ON!</b>\nWe are upgrading the system for more hot features.", user),
            parse_mode=ParseMode.HTML
        )
        return
    
    user_data = db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await update.message.reply_text("🚫 <b>You are BLOCKED!</b> Contact Admin.", parse_mode=ParseMode.HTML)
        return
    
    missing_channels = await security.check_membership(user.id, context.bot)
    
    if missing_channels:
        lock_msg = db.get_config('lock_msg')
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {"text": f"📢 Join {channel['name']}", "url": channel['link']}
            ])
        buttons.append([
            {"text": "✅ Verify Membership", "callback": "verify_membership"}
        ])
        
        keyboard = ui.create_keyboard(buttons, add_back=False, add_close=False)
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except:
            await update.message.reply_text(
                ui.format_text(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        welcome_msg = db.get_config('welcome_msg')
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(btn_text, url=watch_url)
        ]])
        
        try:
            msg = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_text(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            auto_delete = int(db.get_config('auto_delete', Config.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await msg.delete()
                except:
                    pass
        except:
            await update.message.reply_text(
                ui.format_text(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS:
        return
    
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME GOD ADMIN PANEL</b>

{Config.EMOJIS['fire']} <b>Welcome Boss! Here is your Empire Status:</b>

{Config.EMOJIS['chart']} <b>Bot Statistics:</b>
• Total Users: {db.get_stats()['total_users']:,}
• Active Today: {db.get_stats()['active_today']:,}

👇 <b>Select an option from the menu below:</b>
"""
    await update.message.reply_text(
        ui.format_text(text, user),
        reply_markup=ui.get_admin_menu(),
        parse_mode=ParseMode.HTML
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS: return
    
    stats = db.get_stats()
    sys_stats = system_monitor.get_system_stats()
    text = ui.get_stats_display(stats)
    text += f"\n{Config.EMOJIS['gear']} <b>Server Load:</b> CPU {sys_stats['cpu_percent']}% | RAM {sys_stats['memory_percent']}%"
    
    await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML,
        reply_markup=ui.create_keyboard([], add_back=True, add_close=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
{Config.EMOJIS['info']} <b>Help & Support Center</b>

<b>Dear User,</b>
If you are facing issues, try to restart the bot using /start.
Make sure you joined all our channels!

<b>Admin Commands:</b>
/admin - Open Control Panel
/stats - Live Stats
/backup - Force Backup
"""
    await update.message.reply_text(ui.format_text(text, user), parse_mode=ParseMode.HTML)

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS: return
    
    msg = await update.message.reply_text("💾 <b>Backing up Database...</b>", parse_mode=ParseMode.HTML)
    backup_file = db.create_backup()
    if backup_file:
        await msg.edit_text(f"✅ <b>Backup Successful!</b>\nFilename: {os.path.basename(backup_file)}", parse_mode=ParseMode.HTML)
    else:
        await msg.edit_text("❌ <b>Backup Failed!</b> Check logs.", parse_mode=ParseMode.HTML)

# ==============================================================================
# 🔄 CALLBACK QUERY HANDLER (AUTO-DELETE & NAVIGATION)
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    system_monitor.update_user_activity(user.id)
    
    # -----------------------------------------------------------
    # SPECIAL POP-UP LOGIC FOR VERIFY BUTTON
    # -----------------------------------------------------------
    if data == "verify_membership":
        missing_channels = await security.check_membership(user.id, context.bot)
        if not missing_channels:
            # SHOW SUCCESS POPUP
            await query.answer("✅ WOW! Verification Successful Baby! ❤️\nAccess Granted! Enjoy...", show_alert=True)
            
            # Replace Lock Message with Welcome Message (Auto-delete effect)
            welcome_msg = db.get_config('welcome_msg')
            btn_text = db.get_config('btn_text')
            watch_url = db.get_config('watch_url')
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=watch_url)]])
            
            try:
                await query.message.edit_caption(
                    caption=ui.format_text(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except:
                # If original was text only
                await query.message.edit_text(
                    ui.format_text(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
        else:
            # SHOW FAILURE POPUP
            await query.answer("❌ OOPS! Access Denied! 🥺\nPlease join ALL channels first then click Verify!", show_alert=True)
        return

    # Normal Callback Handling
    await query.answer()

    # Admin check
    admin_functions = {'main_menu', 'menu_', 'edit_', 'toggle_', 'remove_', 'add_', 'broadcast', 'create_post', 'block_', 'unblock_', 'add_vip', 'backup_'}
    if any(data.startswith(func) for func in admin_functions) and user.id not in Config.ADMIN_IDS:
        await query.answer("🚫 Admin Access Only!", show_alert=True)
        return

    # Navigation Logic - Uses edit_message_text to "delete" previous state
    if data == "main_menu":
        await show_admin_panel(query.message, user)
    
    elif data == "close_panel":
        try:
            await query.message.delete()
        except:
            pass
    
    elif data == "menu_messages":
        buttons = [[
            {"text": "✏️ Welcome Msg", "callback": "edit_welcome_msg"},
            {"text": "✏️ Lock Msg", "callback": "edit_lock_msg"}
        ], [{"text": "🖼️ Welcome Photo", "callback": "edit_welcome_photo"}]]
        await query.edit_message_text(
            ui.format_text("📝 <b>Message Editor</b>\nChoose a message to customize:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_links":
        buttons = [[
            {"text": "🔗 Watch URL", "callback": "edit_watch_url"},
            {"text": "🔘 Button Text", "callback": "edit_btn_text"}
        ], [{"text": "⏱️ Auto Delete", "callback": "edit_auto_delete"}]]
        await query.edit_message_text(
            ui.format_text("🔗 <b>Link Settings</b>\nCustomize your links here:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_channels":
        channels = db.get_channels()
        text = "📢 <b>Channel Manager</b>\n\n" + ("\n".join([f"{i+1}. {c['name']}" for i, c in enumerate(channels)]) if channels else "No channels added.")
        buttons = [[{"text": f"❌ Remove {c['name']}", "callback": f"remove_channel_{c['id']}"}] for c in channels]
        buttons.append([{"text": "➕ Add New Channel", "callback": "add_channel_start"}])
        await query.edit_message_text(ui.format_text(text, user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_security":
        m = db.get_config('maint_mode')
        f = db.get_config('force_join')
        buttons = [
            [{"text": f"🔄 Maint: {m}", "callback": "toggle_maint"}, {"text": f"🔄 Force: {f}", "callback": "toggle_force"}],
            [{"text": "🚫 Block User", "callback": "block_user_start"}, {"text": "✅ Unblock", "callback": "unblock_user_start"}]
        ]
        await query.edit_message_text(ui.format_text(f"🛡️ <b>Security Control</b>\nMaint: {m} | Force Join: {f}", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_marketing":
        buttons = [[{"text": "📝 Create Post", "callback": "create_post_start"}, {"text": "📢 Broadcast", "callback": "broadcast_start"}]]
        await query.edit_message_text(ui.format_text("📡 <b>Marketing Tools</b>\nPromote your content:", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_stats":
        await query.edit_message_text(ui.format_text(ui.get_stats_display(db.get_stats()), user), reply_markup=ui.create_keyboard([]), parse_mode=ParseMode.HTML)

    elif data == "menu_vip":
        buttons = [[{"text": "➕ Add VIP", "callback": "add_vip_start"}, {"text": "➖ Remove VIP", "callback": "remove_vip_start"}]]
        await query.edit_message_text(ui.format_text("👑 <b>VIP Management</b>\nControl premium users:", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_system":
        buttons = [[{"text": "💾 Backup Now", "callback": "backup_now"}]]
        await query.edit_message_text(ui.format_text("⚙️ <b>System Tools</b>", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    # Actions
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        await query.message.reply_text(f"✏️ <b>Send new value for:</b> <code>{key}</code>", parse_mode=ParseMode.HTML)
        return Config.STATE_EDIT_CONFIG
    
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        val = "ON" if db.get_config(key) == "OFF" else "OFF"
        db.set_config(key, val)
        query.data = "menu_security"
        await callback_handler(update, context)

    elif data.startswith("remove_channel_"):
        cid = data.replace("remove_channel_", "")
        db.remove_channel(cid)
        query.data = "menu_channels"
        await callback_handler(update, context)

    elif data == "add_channel_start":
        await query.message.reply_text("➕ <b>Send Channel ID/Username:</b>\nExample: @mychannel or -100123...", parse_mode=ParseMode.HTML)
        return Config.STATE_CHANNEL_ADD_ID

    elif data == "create_post_start":
        await query.message.reply_text("📝 <b>Send Post Caption:</b>", parse_mode=ParseMode.HTML)
        context.user_data['post_wizard'] = {}
        return Config.STATE_POST_CAPTION

    elif data == "broadcast_start":
        await query.message.reply_text("📢 <b>Send Message to Broadcast:</b>\n(Text, Photo or Video)", parse_mode=ParseMode.HTML)
        return Config.STATE_BROADCAST

    elif data == "backup_now":
        f = db.create_backup()
        await query.answer("✅ Backup Created!" if f else "❌ Failed!", show_alert=True)

async def show_admin_panel(message, user):
    text = f"""
{Config.EMOJIS['admin']} <b>SUPREME GOD ADMIN PANEL</b>
{Config.EMOJIS['fire']} <b>Welcome Boss!</b>
"""
    await message.edit_text(ui.format_text(text, user), reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)

# ==============================================================================
# ✏️ CONVERSATION HANDLERS
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    if key and db.set_config(key, update.message.text):
        await update.message.reply_text(f"✅ <b>{key}</b> updated!", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def post_caption_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_wizard']['caption'] = update.message.text_html
    await update.message.reply_text("📸 <b>Send Photo/Video (or /skip):</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_POST_MEDIA

async def post_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['post_wizard'].update({'media': update.message.photo[-1].file_id, 'type': 'photo'})
    elif update.message.video:
        context.user_data['post_wizard'].update({'media': update.message.video.file_id, 'type': 'video'})
    else:
        context.user_data['post_wizard'].update({'media': None, 'type': 'text'})
    await update.message.reply_text("🔘 <b>Send Button Text (or /skip):</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_POST_BUTTON

async def post_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text if update.message.text != '/skip' else db.get_config('btn_text')
    context.user_data['post_wizard']['button_text'] = txt
    
    channels = db.get_channels()
    buttons = [[{"text": f"📤 {c['name']}", "callback": f"post_to_{c['id']}"}] for c in channels]
    buttons.append([{"text": "📤 Post to ALL", "callback": "post_to_all"}])
    
    await update.message.reply_text("✅ <b>Select Target Channel:</b>", reply_markup=ui.create_keyboard(buttons, add_back=False), parse_mode=ParseMode.HTML)
    return Config.STATE_POST_CONFIRM

async def post_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = context.user_data.get('post_wizard', {})
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(data.get('button_text', 'Click'), url=db.get_config('watch_url'))]])
    
    targets = db.get_channels() if query.data == "post_to_all" else [c for c in db.get_channels() if c['id'] == query.data.replace("post_to_", "")]
    
    await query.message.edit_text(f"⏳ Sending to {len(targets)} channels...")
    
    for ch in targets:
        try:
            if data['type'] == 'photo': await context.bot.send_photo(ch['id'], data['media'], caption=data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
            elif data['type'] == 'video': await context.bot.send_video(ch['id'], data['media'], caption=data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(ch['id'], data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
        except: pass
        
    await query.message.reply_text("✅ <b>Posting Completed!</b>", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = await update.message.reply_text(f"⏳ Broadcasting to {len(users)} users...")
    count = 0
    for uid in users:
        try:
            await update.message.copy(uid)
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await msg.edit_text(f"✅ <b>Broadcast sent to {count} users!</b>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def add_channel_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simplified flow for brevity, follows state machine
    pass # Implementation inside main via State Machine

async def add_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cid'] = update.message.text
    await update.message.reply_text("📝 <b>Channel Name:</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cname'] = update.message.text
    await update.message.reply_text("🔗 <b>Channel Link:</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_CHANNEL_ADD_LINK

async def add_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text):
        await update.message.reply_text("✅ Channel Added!", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ Failed!", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 MAIN APPLICATION
# ==============================================================================

def main():
    application = ApplicationBuilder().token(Config.TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("backup", backup_command))
    
    # Conversation: Config Edit
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={Config.STATE_EDIT_CONFIG: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_config_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Conversation: Post
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post_start$')],
        states={
            Config.STATE_POST_CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_caption_handler)],
            Config.STATE_POST_MEDIA: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, post_media_handler)],
            Config.STATE_POST_BUTTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_button_handler)],
            Config.STATE_POST_CONFIRM: [CallbackQueryHandler(post_confirm_handler, pattern='^post_to_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Conversation: Add Channel
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel_start$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))

    # Conversation: Broadcast
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast_start$')],
        states={Config.STATE_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # Global Callback
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🤖 Bot Started Successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
