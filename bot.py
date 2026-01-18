"""
================================================================================
সুপ্রিম গড মোড বট - আলটিমেট এডিশন (বাংলাদেশ স্পেশাল)
ভার্সন: v১১.০ (ভাইরাল এডিশন)
অথর: এআই অ্যাসিস্ট্যান্ট
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
# ⚙️ কনফিগারেশন কনস্ট্যান্টস
# ==============================================================================

class Config:
    # বট কনফিগারেশন
    TOKEN = "8173181203:AAEDcda58agIZZic4uC8tSQVzKbrk6pYnU4"
    ADMIN_IDS = {6406804999}
    DB_NAME = "supreme_bot_v10.db"
    BACKUP_DIR = "backups"
    LOG_FILE = "bot_activity.log"
    
    # সিস্টেম কনস্ট্যান্টস
    DEFAULT_AUTO_DELETE = 45  # সেকেন্ড
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3  # প্রতি সেকেন্ডে মেসেজ
    SESSION_TIMEOUT = 300  # 5 মিনিট
    
    # চ্যানেল সেটিংস
    DEFAULT_CHANNELS = [
        {"id": "@virallink259", "name": "ভাইরাল লিংক ২০২৬ 🔥", "link": "https://t.me/virallink259"},
        {"id": -1002279183424, "name": "প্রিমিয়াম অ্যাপস 💎", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
        {"id": "@virallink246", "name": "বিডি বিউটি 🍑", "link": "https://t.me/virallink246"},
        {"id": "@viralexpress1", "name": "এফবি ইন্সটা লিংকস 🔗", "link": "https://t.me/viralexpress1"},
        {"id": "@movietime467", "name": "মুভি টাইম 🎬", "link": "https://t.me/movietime467"},
        {"id": "@viralfacebook9", "name": "বিডি এমএমএস ভিডিও 🔞", "link": "https://t.me/viralfacebook9"},
        {"id": "@viralfb24", "name": "দেশি ভাবি 🔥", "link": "https://t.me/viralfb24"},
        {"id": "@fbviral24", "name": "কোচি মেয়ে 🎀", "link": "https://t.me/fbviral24"},
        {"id": -1001550993047, "name": "রিকোয়েস্ট জোন 📥", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
        {"id": -1002011739504, "name": "ভাইরাল বিডি 🌍", "link": "https://t.me/+la630-IFwHAwYWVl"},
        {"id": -1002444538806, "name": "এআই স্টুডিও 🎨", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
    ]
    
    # প্রিমিয়াম ইমোজি প্যাক (ইমোজিগুলো লেখার সাথে মিক্সড থাকবে)
    EMOJIS = {
        "sparkle": "✨", "heart": "❤️", "fire": "🔥", "star": "⭐", "diamond": "💎",
        "crown": "👑", "gem": "🔮", "gift": "🎁", "ribbon": "🎀", "butterfly": "🦋",
        "fairy": "🧚‍♀️", "candy": "🍬", "cherry": "🍒", "flower": "🌸", "lollipop": "🍭",
        "rabbit": "🐇", "peach": "🍑", "chocolate": "🍫", "icecream": "🍦", "cake": "🍰",
        "donut": "🍩", "waffle": "🧇", "pancake": "🥞", "bacon": "🥓", "egg": "🍳",
        "sun": "☀️", "rainbow": "🌈", "cloud": "☁️", "lightning": "⚡", "rocket": "🚀",
        "target": "🎯", "lock": "🔒", "key": "🔑", "money": "💰", "magic": "🪄",
        "eye": "👁️", "eyes": "👀", "kiss": "💋", "lips": "🫦", "heart_hands": "🫶",
        "clock": "🕰️", "hourglass": "⏳", "bangladesh": "🇧🇩", "movie": "🎬", "camera": "🎥",
        "hot": "🌶️", "new": "🆕", "infinity": "∞", "fast_forward": "⏩", "trophy": "🥇",
        "peacock": "🦚", "evil_eye": "🧿", "drama": "🎭", "carousel": "🎠", "unicorn": "🦄",
        "sparkles": "🎇", "fireworks": "🎆", "party": "🎉", "confetti": "🎊", "pinata": "🪅",
        "circus": "🎪", "bubble": "🫧", "mango": "🥭", "rose": "🌹", "honey": "🍯",
        "blueberry": "🫐", "tulip": "🌷", "strawberry": "🍓", "blossom": "🌼", "cookie": "🍪",
        "heart_box": "💟", "watermelon": "🍉", "sunflower": "🌻", "lemon": "🍋", "avocado": "🥑",
        "pineapple": "🍍", "broccoli": "🥦", "corn": "🌽", "potato": "🥔", "carrot": "🥕",
        "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️", "megaphone": "📢",
        "users": "👥", "admin": "👑", "shield": "🛡️", "gear": "⚙️", "database": "💾",
        "chart": "📊", "bell": "🔔", "link": "🔗", "time": "⏰", "calendar": "📅",
        "up": "⬆️", "down": "⬇️", "left": "⬅️", "right": "➡️", "refresh": "🔄",
        "plus": "➕", "minus": "➖", "question": "❓", "exclamation": "❗", "trash": "🗑️",
        "cloud_storage": "☁️", "moon": "🌙", "earth": "🌍", "love_face": "🥰",
        "prince": "🤴", "princess": "👸", "smile": "😊", "wink": "😉", "heart_eyes": "😍",
        "cool": "😎", "kissing_heart": "😘", "flushed": "😳", "pleading": "🥺",
        "partying": "🥳", "disguise": "🥸", "salute": "🫡", "melting": "🫠", "hearts": "💕",
        "heart_grow": "💗", "heart_beat": "💓", "heart_sparkle": "💖", "heart_arrow": "💘",
        "heart_ribbon": "💝", "broken_heart": "💔", "mending_heart": "❤️🩹", "orange_heart": "🧡",
        "yellow_heart": "💛", "green_heart": "💚", "blue_heart": "💙", "purple_heart": "💜",
        "brown_heart": "🤎", "black_heart": "🖤", "grey_heart": "🩶", "white_heart": "🤍",
        "fire_heart": "❤️🔥", "pink_heart": "🩷", "light_blue_heart": "🩵",
        "ok_hand": "👌", "clap": "👏", "muscle": "💪", "brain": "🧠", "lungs": "🫁",
        "heart_lungs": "💘🫁", "sparkle_heart": "💖✨", "fire_eyes": "🔥👀"
    }
    
    # কনভারসেশন স্টেটস
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
# 📝 অ্যাডভান্সড লগিং সিস্টেম
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
        self.logger.info("সুপ্রিম গড বট v১১.০ (বিডি এডিশন) শুরু হচ্ছে...")
        self.logger.info("=" * 60)
    
    def get_logger(self):
        return self.logger

logger_instance = SupremeLogger()
logger = logger_instance.get_logger()

# ==============================================================================
# 🗄️ এন্টারপ্রাইজ ডাটাবেস ম্যানেজার
# ==============================================================================

class DatabaseManager:
    """অ্যাডভান্সড মাল্টি-থ্রেডেড ডাটাবেস ম্যানেজার"""
    
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
        logger.info("ডাটাবেস ইনিশিয়ালাইজড")
    
    def initialize_defaults(self):
        """ডিফল্ট কনফিগারেশন ইনিশিয়ালাইজেশন"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # প্রিমিয়াম ইমোজি মিক্সড ওয়েলকাম মেসেজ
        welcome_msg_text = '''✨🎀🦋🧚‍♀️💘👤হেই ডিয়ার ইউজারঃ {user_mention}🌟🍬🌸

🫦🥰❤️‍🔥ওহ্ মাই গড! আমার লাভ! তুমি এসেছো!❤️‍🔥🥰🫦

👸🤴😘আমার সুইটহার্ট!😘🤴👸তুমি কি জানো আমি তোমার জন্য🕰️⏳কতটা উতলা হয়ে অপেক্ষা করছিলাম? আমার🎁🎀এক্সক্লুসিভ প্রিমিয়াম ভাইরাল ওয়ার্ল্ড🎀🎁এ তোমাকে হার্টফেল স্বাগতম!💝💖

💎🔮এখানে আছে এমন সব🥵হট🥵ও🔮রেয়ার🔮কনটেন্ট যা তোমার🌈কল্পনার🌈ও বাইরে!🍭🍫

🔥👑ভিআইপি এক্সেস সুবিধা শুধু তোমার জন্য👑🔥
•🌶️👀স্পাইসি ভাইরাল ভিডিও👀🌶️: দেখলে চোখ জুড়িয়ে যাবে!✨👁️✨
•🔐🍖প্রিমিয়াম আনকাট ম্যাটেরিয়াল🍖🔐: একদম🆕ফ্রেশ🆕ও🥩র'🥩!
•🚀⚡রিয়েল-টাইম আপডেট⚡🚀:🥇সবার🥇আগেই পাবে!⚡⚡
•💸🪄গোপন ইনকাম ট্রিক্স🪄💸: টাকা কমানোর🎩ম্যাজিক🎩!💰💎

💋🫶আমার জান, তুমি কি🌌রেডি🌌অ্যাডভেঞ্চার শুরু করতে?⏩দেরি করো না⏩শোনা, নিচের🎯বাটনে🎯ক্লিক করো আর ঢুকো🌠এক্সাইটমেন্ট🌠এর দুনিয়ায়!🚀🌠

🫶👇এখনই জয়েন করো আর এঞ্জয়∞আনলিমিটেড ফান∞!👇🫶

🕐🇧🇩বাংলাদেশ সময়🇧🇩🕐: {bd_time}📅⏰'''
        
        # প্রিমিয়াম ইমোজি মিক্সড লক মেসেজ
        lock_msg_text = '''🔒⚠️🚫ওপিএস বেবি! অ্যাক্সেস ডিনাইড!🚫⚠️🔒

❌😥একি শোনা? তুমি এখনো আমাদের সব চ্যানেলে জয়েন করো নি?❌😥

👀💔আমি তোমায় এতো ভালোবাসি আর তুমি আমায় সাপোর্ট করবে না?👀💔আমার সব🥵হট ভিডিও🥵ও💎প্রিমিয়াম কনটেন্ট💎দেখার জন্য তোমাকে অবশ্যই নিচের সব গুলো চ্যানেলে জয়েন করতে হবে!🔥

❤️😘প্লিজ জান, আমার কথা রাখো!❤️😘নিচের দেওয়া প্রত্যেকটা চ্যানেলে এক্টি এক্টি করে ক্লিক করো আর জয়েন করো। তারপর"✅ভেরিফাই"বাটনে ক্লিক করো, আমি তোমায় সরাসরি ভিতরে নিয়ে যাব!💋

👇🔗নিচের বাটন গুলোতে ক্লিক করে জয়েন করো এখনই!🔗👇'''
        
        defaults = [
            ('welcome_msg', welcome_msg_text, 0, 'messages', 'নতুন ইউজারের জন্য ওয়েলকাম মেসেজ'),
            ('lock_msg', lock_msg_text, 0, 'messages', 'চ্যানেল জয়েন না করলে লক মেসেজ'),
            ('welcome_photo', 'https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead', 0, 'media', 'ওয়েলকাম ফটো URL'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1', 0, 'links', 'প্রধান ওয়াচ URL'),
            ('btn_text', '🎬🎥🔥ফুল ভিডিও দেখুন এখানে🔥🎥🎬', 0, 'buttons', 'বাটন টেক্সট'),
            ('auto_delete', '45', 0, 'settings', 'অটো ডিলিট টাইমার সেকেন্ডে'),
            ('maint_mode', 'OFF', 0, 'security', 'মেইনটেনেন্স মোড স্ট্যাটাস'),
            ('force_join', 'ON', 0, 'security', 'ফোর্স জয়েন চ্যানেল'),
            ('max_users_per_day', '1000', 0, 'limits', 'প্রতিদিন সর্বোচ্চ ইউজার'),
            ('vip_access_level', '2', 0, 'vip', 'ভিআইপি অ্যাক্সেস লেভেল'),
            ('backup_interval', '86400', 0, 'system', 'ব্যাকআপ ইন্টারভাল সেকেন্ডে'),
            ('flood_threshold', '5', 0, 'security', 'ফ্লাড থ্রেশহোল্ড প্রতি মিনিটে'),
            ('session_timeout', '300', 0, 'security', 'সেশন টাইমআউট সেকেন্ডে')
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
    
    # === ইউজার ম্যানেজমেন্ট ===
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
            logger.error(f"ইউজার অ্যাড করার ত্রুটি {user_id}: {e}")
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
            logger.error(f"ইউজার অ্যাক্টিভিটি আপডেট ত্রুটি {user_id}: {e}")
    
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
            ''', (admin_id, 'block_user', f'ব্লক করা হয়েছে {user_id}: {reason}'))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"ইউজার ব্লক করার ত্রুটি {user_id}: {e}")
            return False
    
    def unblock_user(self, user_id: int, admin_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (admin_id, 'unblock_user', f'আনব্লক করা হয়েছে {user_id}'))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"ইউজার আনব্লক করার ত্রুটি {user_id}: {e}")
            return False
    
    # === স্ট্যাটিস্টিক্স ===
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
    
    # === কনফিগারেশন ম্যানেজমেন্ট ===
    def get_config(self, key: str, default: str = ""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            return result[0]
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
            logger.error(f"কনফিগ সেট করার ত্রুটি {key}: {e}")
            return False
    
    # === চ্যানেল ম্যানেজমেন্ট ===
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
            logger.error(f"চ্যানেল অ্যাড করার ত্রুটি {channel_id}: {e}")
            return False
    
    def remove_channel(self, channel_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE channels SET status = 'inactive' WHERE channel_id = ?", (channel_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"চ্যানেল রিমুভ করার ত্রুটি {channel_id}: {e}")
            return False
    
    # === ভিআইপি ও সেশন ম্যানেজমেন্ট ===
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
            logger.error(f"ভিআইপি অ্যাড করার ত্রুটি {user_id}: {e}")
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
            logger.error(f"ভিআইপি রিমুভ করার ত্রুটি {user_id}: {e}")
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
            logger.error(f"সেশন ক্রিয়েট করার ত্রুটি: {e}")
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
            logger.info(f"ব্যাকআপ তৈরি হয়েছে: {backup_file}")
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith('backup_') and f.endswith('.db')
            ])
            if len(backups) > 7:
                for old_backup in backups[:-7]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
            return backup_file
        except Exception as e:
            logger.error(f"ব্যাকআপ তৈরি করার ত্রুটি: {e}")
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
# 🔧 সিস্টেম মনিটর
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
        return f"{int(days)}দিন {int(hours)}ঘণ্টা {int(minutes)}মিনিট {int(seconds)}সেকেন্ড"
    
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
# 🌐 হেলথ সার্ভার
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
                'version': 'v১১.০'
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>সুপ্রিম বট চলছে (বাংলাদেশ টাইমজোন)</h1>")
    
    def log_message(self, format, *args):
        logger.debug(f"HTTP {args[0]} {args[1]}")

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"হেলথ সার্ভার শুরু করতে ব্যর্থ: {e}")

server_thread = threading.Thread(target=run_health_server, daemon=True)
server_thread.start()

# ==============================================================================
# 🎨 ইউআই ম্যানেজার (বাংলাদেশ টাইম ও ইউজার মেনশন সহ)
# ==============================================================================

class UIManager:
    @staticmethod
    def format_text(text: str, user=None):
        """ইউজার ইনফো, ইমোজি ও বাংলাদেশ টাইম সহ টেক্সট ফরম্যাট"""
        # বাংলাদেশ টাইম (UTC+6)
        bd_time = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        bd_time_str = bd_time.strftime("%d %b %Y, %I:%M %p (BD)")
        
        # টেক্সটে বাংলাদেশ টাইম যুক্ত করুন
        text = text.replace("{bd_time}", bd_time_str)
        
        # ইউজার মেনশন যুক্ত করুন
        if user:
            user_mention = mention_html(user.id, user.first_name or 'আমার লাভ')
            text = text.replace("{user_mention}", user_mention)
        else:
            text = text.replace("{user_mention}", "")
        
        return text
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = False):
        keyboard = []
        for row in buttons:
            row_buttons = []
            for btn in row:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=btn.get('text', ''),
                        callback_data=btn.get('callback', ''),
                        url=btn.get('url', None)
                    )
                )
            keyboard.append(row_buttons)
        
        if add_back:
            keyboard.append([
                InlineKeyboardButton("🔙 মেইন মেনুতে ফিরুন", callback_data="main_menu")
            ])
        if add_close:
            keyboard.append([
                InlineKeyboardButton("❌ প্যানেল বন্ধ করুন", callback_data="close_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_menu():
        buttons = [
            [
                {"text": "📝 মেসেজ এডিটর", "callback": "menu_messages"},
                {"text": "🔗 লিংক সেটিংস", "callback": "menu_links"}
            ],
            [
                {"text": "📢 চ্যানেল ম্যানেজার", "callback": "menu_channels"},
                {"text": "🛡️ সিকিউরিটি প্যানেল", "callback": "menu_security"}
            ],
            [
                {"text": "📡 মার্কেটিং টুলস", "callback": "menu_marketing"},
                {"text": "📊 স্ট্যাটিস্টিক্স", "callback": "menu_stats"}
            ],
            [
                {"text": "👑 ভিআইপি ম্যানেজমেন্ট", "callback": "menu_vip"},
                {"text": "⚙️ সিস্টেম সেটিংস", "callback": "menu_system"}
            ]
        ]
        return UIManager.create_keyboard(buttons, add_back=False, add_close=True)
    
    @staticmethod
    def get_stats_display(stats: Dict):
        text = f"""
{Config.EMOJIS['chart']} <b>সিস্টেম স্ট্যাটিস্টিক্স (লাইভ)</b>

{Config.EMOJIS['users']} <b>ইউজার স্ট্যাটস:</b>
• মোট ইউজার: {stats.get('total_users', 0):,}
• আজ নতুন: {stats.get('today_users', 0):,}
• ভিআইপি ইউজার: {stats.get('vip_users', 0):,}
• ব্লকড: {stats.get('blocked_users', 0):,}
• আজ অ্যাক্টিভ: {stats.get('active_today', 0):,}

{Config.EMOJIS['megaphone']} <b>চ্যানেল স্ট্যাটস:</b>
• অ্যাক্টিভ চ্যানেল: {stats.get('active_channels', 0):,}

{Config.EMOJIS['camera']} <b>পোস্ট স্ট্যাটস:</b>
• মোট পোস্ট: {stats.get('total_posts', 0):,}
• আজকের পোস্ট: {stats.get('today_posts', 0):,}
"""
        return text

ui = UIManager()

# ==============================================================================
# 🔐 সিকিউরিটি ম্যানেজার (পপআপ ভেরিফিকেশন সহ)
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
                logger.warning(f"চ্যানেল চেক করতে ব্যর্থ {channel['id']}: {e}")
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
# 🔄 ব্যাকগ্রাউন্ড টাস্কস
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
                logger.error(f"ব্যাকগ্রাউন্ড টাস্ক ত্রুটি: {e}")
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
# 🎮 কমান্ড হ্যান্ডলারস (ইমোজি মিক্সড হট মেসেজ সহ)
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইমোজি মিক্সড হট মেসেজ লজিক সহ /start কমান্ড হ্যান্ডল"""
    user = update.effective_user
    system_monitor.update_user_activity(user.id)
    system_monitor.increment_message()
    
    db.add_user(user.id, user.username, user.first_name, user.last_name or "")
    
    if security.check_flood(user.id):
        await update.message.reply_text("⚠️ <b>ধীরে বেবি! খুব দ্রুত!</b>", parse_mode=ParseMode.HTML)
        return
    
    if security.check_maintenance(user.id):
        await update.message.reply_text(
            ui.format_text("🔧 <b>সিস্টেম মেইনটেনেন্স মোড চালু!</b>\nআমরা আরো হট ফিচারের জন্য সিস্টেম আপগ্রেড করছি।", user),
            parse_mode=ParseMode.HTML
        )
        return
    
    user_data = db.get_user(user.id)
    if user_data and user_data.get('is_blocked'):
        await update.message.reply_text("🚫 <b>আপনি ব্লকড!</b> অ্যাডমিনের সাথে যোগাযোগ করুন।", parse_mode=ParseMode.HTML)
        return
    
    missing_channels = await security.check_membership(user.id, context.bot)
    
    if missing_channels:
        # লক মেসেজ প্রিমিয়াম ইমোজি মিক্সড
        lock_msg = db.get_config('lock_msg')
        buttons = []
        for channel in missing_channels:
            buttons.append([
                {"text": f"📢 {channel['name']} এ জয়েন করুন", "url": channel['link']}
            ])
        buttons.append([
            {"text": "✅ ভেরিফাই মেম্বারশিপ", "callback": "verify_membership"}
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
        # ওয়েলকাম মেসেজ প্রিমিয়াম ইমোজি মিক্সড
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
    """এডমিন কমান্ড হ্যান্ডল"""
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS:
        return
    
    text = f"""
{Config.EMOJIS['admin']} <b>সুপ্রিম গড এডমিন প্যানেল</b>

{Config.EMOJIS['fire']} <b>স্বাগতম বস! এখানে আপনার সাম্রাজ্যের স্ট্যাটাস:</b>

{Config.EMOJIS['chart']} <b>বট স্ট্যাটিস্টিক্স:</b>
• মোট ইউজার: {db.get_stats()['total_users']:,}
• আজ অ্যাক্টিভ: {db.get_stats()['active_today']:,}

👇 <b>নিচের মেনু থেকে একটি অপশন সিলেক্ট করুন:</b>
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
    text += f"\n{Config.EMOJIS['gear']} <b>সার্ভার লোড:</b> CPU {sys_stats['cpu_percent']}% | RAM {sys_stats['memory_percent']}%"
    
    await update.message.reply_text(
        ui.format_text(text, user),
        parse_mode=ParseMode.HTML,
        reply_markup=ui.create_keyboard([], add_back=True, add_close=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
{Config.EMOJIS['info']} <b>হেল্প অ্যান্ড সাপোর্ট সেন্টার</b>

<b>প্রিয় ইউজার,</b>
যদি আপনি সমস্যার সম্মুখীন হন, /start ব্যবহার করে বট রিস্টার্ট করার চেষ্টা করুন।
নিশ্চিত করুন আপনি আমাদের সব চ্যানেলে জয়েন করেছেন!

<b>এডমিন কমান্ডস:</b>
/admin - কন্ট্রোল প্যানেল খুলুন
/stats - লাইভ স্ট্যাটস
/backup - ফোর্স ব্যাকআপ
"""
    await update.message.reply_text(ui.format_text(text, user), parse_mode=ParseMode.HTML)

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS: return
    
    msg = await update.message.reply_text("💾 <b>ডাটাবেস ব্যাকআপ হচ্ছে...</b>", parse_mode=ParseMode.HTML)
    backup_file = db.create_backup()
    if backup_file:
        await msg.edit_text(f"✅ <b>ব্যাকআপ সফল!</b>\nফাইলনাম: {os.path.basename(backup_file)}", parse_mode=ParseMode.HTML)
    else:
        await msg.edit_text("❌ <b>ব্যাকআপ ব্যর্থ!</b> লগ চেক করুন।", parse_mode=ParseMode.HTML)

# ==============================================================================
# 🔄 কলব্যাক কুয়েরি হ্যান্ডলার (অটো-ডিলিট ও পপআপ ভেরিফিকেশন)
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    system_monitor.update_user_activity(user.id)
    
    # -----------------------------------------------------------
    # ভেরিফাই বাটনের জন্য বিশেষ পপআপ লজিক
    # -----------------------------------------------------------
    if data == "verify_membership":
        missing_channels = await security.check_membership(user.id, context.bot)
        if not missing_channels:
            # ✅ সফল ভেরিফিকেশন পপআপ
            await query.answer(
                "🎉🎊✅ ওয়াও! ভেরিফিকেশন সফল হয়েছে বেবি! ❤️\n\n"
                "🌟✨ তোমাকে স্বাগতম আমাদের প্রিমিয়াম কমিউনিটিতে! 🎀💎\n"
                "এখন তুমি আনলিমিটেড এক্সেস পেয়েছো সব হট কনটেন্টে! 🔥🥵\n\n"
                "💋🫶 এঞ্জয় করো সারা জীবন মনে থাকবে এমন এক্সপেরিয়েন্স! 🚀🌠",
                show_alert=True
            )
            
            # ওয়েলকাম মেসেজ দিয়ে লক মেসেজ রিপ্লেস করুন
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
                # যদি অরিজিনাল টেক্সট হয়
                await query.message.edit_text(
                    ui.format_text(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
        else:
            # ❌ ফেইল ভেরিফিকেশন পপআপ
            await query.answer(
                "❌😥 ওপিএস! ভেরিফিকেশন ব্যর্থ! 🥺\n\n"
                "⚠️🚫 তুমি এখনো সব চ্যানেলে জয়েন করো নি! \n"
                "দয়া করে নিচের সবগুলো চ্যানেলে জয়েন করে তারপর আবার ভেরিফাই চেষ্টা করো! 🔗👇\n\n"
                "💋❤️ আমার কথা রাখো বেবি, আমি তোমার জন্য অপেক্ষা করছি! ⏳🕰️",
                show_alert=True
            )
        return

    # নরমাল কলব্যাক হ্যান্ডলিং
    await query.answer()

    # এডমিন চেক
    admin_functions = {'main_menu', 'menu_', 'edit_', 'toggle_', 'remove_', 'add_', 'broadcast', 'create_post', 'block_', 'unblock_', 'add_vip', 'backup_'}
    if any(data.startswith(func) for func in admin_functions) and user.id not in Config.ADMIN_IDS:
        await query.answer("🚫 শুধুমাত্র এডমিন অ্যাক্সেস!", show_alert=True)
        return

    # নেভিগেশন লজিক
    if data == "main_menu":
        await show_admin_panel(query.message, user)
    
    elif data == "close_panel":
        try:
            await query.message.delete()
        except:
            pass
    
    elif data == "menu_messages":
        buttons = [[
            {"text": "✏️ ওয়েলকাম মেসেজ", "callback": "edit_welcome_msg"},
            {"text": "✏️ লক মেসেজ", "callback": "edit_lock_msg"}
        ], [{"text": "🖼️ ওয়েলকাম ফটো", "callback": "edit_welcome_photo"}]]
        await query.edit_message_text(
            ui.format_text("📝 <b>মেসেজ এডিটর</b>\nকাস্টমাইজ করার জন্য একটি মেসেজ চয়েজ করুন:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_links":
        buttons = [[
            {"text": "🔗 ওয়াচ URL", "callback": "edit_watch_url"},
            {"text": "🔘 বাটন টেক্সট", "callback": "edit_btn_text"}
        ], [{"text": "⏱️ অটো ডিলিট", "callback": "edit_auto_delete"}]]
        await query.edit_message_text(
            ui.format_text("🔗 <b>লিংক সেটিংস</b>\nআপনার লিংক কাস্টমাইজ করুন:", user),
            reply_markup=ui.create_keyboard(buttons),
            parse_mode=ParseMode.HTML
        )

    elif data == "menu_channels":
        channels = db.get_channels()
        text = "📢 <b>চ্যানেল ম্যানেজার</b>\n\n" + ("\n".join([f"{i+1}. {c['name']}" for i, c in enumerate(channels)]) if channels else "কোন চ্যানেল অ্যাড করা হয়নি।")
        buttons = [[{"text": f"❌ {c['name']} রিমুভ করুন", "callback": f"remove_channel_{c['id']}"}] for c in channels]
        buttons.append([{"text": "➕ নতুন চ্যানেল অ্যাড করুন", "callback": "add_channel_start"}])
        await query.edit_message_text(ui.format_text(text, user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_security":
        m = db.get_config('maint_mode')
        f = db.get_config('force_join')
        buttons = [
            [{"text": f"🔄 মেইনটেনেন্স: {m}", "callback": "toggle_maint"}, {"text": f"🔄 ফোর্স জয়েন: {f}", "callback": "toggle_force"}],
            [{"text": "🚫 ইউজার ব্লক করুন", "callback": "block_user_start"}, {"text": "✅ আনব্লক করুন", "callback": "unblock_user_start"}]
        ]
        await query.edit_message_text(ui.format_text(f"🛡️ <b>সিকিউরিটি কন্ট্রোল</b>\nমেইনটেনেন্স: {m} | ফোর্স জয়েন: {f}", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_marketing":
        buttons = [{"text": "📝 পোস্ট তৈরি করুন", "callback": "create_post_start"}, {"text": "📢 ব্রডকাস্ট", "callback": "broadcast_start"}]
        await query.edit_message_text(ui.format_text("📡 <b>মার্কেটিং টুলস</b>\nআপনার কনটেন্ট প্রমোট করুন:", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_stats":
        await query.edit_message_text(ui.format_text(ui.get_stats_display(db.get_stats()), user), reply_markup=ui.create_keyboard([]), parse_mode=ParseMode.HTML)

    elif data == "menu_vip":
        buttons = [{"text": "➕ ভিআইপি অ্যাড করুন", "callback": "add_vip_start"}, {"text": "➖ ভিআইপি রিমুভ করুন", "callback": "remove_vip_start"}]
        await query.edit_message_text(ui.format_text("👑 <b>ভিআইপি ম্যানেজমেন্ট</b>\nপ্রিমিয়াম ইউজার কন্ট্রোল:", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    elif data == "menu_system":
        buttons = [{"text": "💾 এখনই ব্যাকআপ করুন", "callback": "backup_now"}]
        await query.edit_message_text(ui.format_text("⚙️ <b>সিস্টেম টুলস</b>", user), reply_markup=ui.create_keyboard(buttons), parse_mode=ParseMode.HTML)

    # অ্যাকশনস
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        context.user_data['edit_key'] = key
        await query.message.reply_text(f"✏️ <b>নতুন ভ্যালু পাঠান:</b> <code>{key}</code>", parse_mode=ParseMode.HTML)
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
        await query.message.reply_text("➕ <b>চ্যানেল ID/ইউজারনেম পাঠান:</b>\nউদাহরণ: @mychannel বা -100123...", parse_mode=ParseMode.HTML)
        return Config.STATE_CHANNEL_ADD_ID

    elif data == "create_post_start":
        await query.message.reply_text("📝 <b>পোস্ট ক্যাপশন পাঠান:</b>", parse_mode=ParseMode.HTML)
        context.user_data['post_wizard'] = {}
        return Config.STATE_POST_CAPTION

    elif data == "broadcast_start":
        await query.message.reply_text("📢 <b>ব্রডকাস্ট করার মেসেজ পাঠান:</b>\n(টেক্সট, ফটো বা ভিডিও)", parse_mode=ParseMode.HTML)
        return Config.STATE_BROADCAST

    elif data == "backup_now":
        f = db.create_backup()
        await query.answer("✅ ব্যাকআপ তৈরি হয়েছে!" if f else "❌ ব্যর্থ!", show_alert=True)

async def show_admin_panel(message, user):
    text = f"""
{Config.EMOJIS['admin']} <b>সুপ্রিম গড এডমিন প্যানেল</b>
{Config.EMOJIS['fire']} <b>স্বাগতম বস!</b>
"""
    await message.edit_text(ui.format_text(text, user), reply_markup=ui.get_admin_menu(), parse_mode=ParseMode.HTML)

# ==============================================================================
# ✏️ কনভারসেশন হ্যান্ডলারস
# ==============================================================================

async def edit_config_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    if key and db.set_config(key, update.message.text):
        await update.message.reply_text(f"✅ <b>{key}</b> আপডেট হয়েছে!", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def post_caption_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_wizard']['caption'] = update.message.text_html
    await update.message.reply_text("📸 <b>ফটো/ভিডিও পাঠান (বা /skip):</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_POST_MEDIA

async def post_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['post_wizard'].update({'media': update.message.photo[-1].file_id, 'type': 'photo'})
    elif update.message.video:
        context.user_data['post_wizard'].update({'media': update.message.video.file_id, 'type': 'video'})
    else:
        context.user_data['post_wizard'].update({'media': None, 'type': 'text'})
    await update.message.reply_text("🔘 <b>বাটন টেক্সট পাঠান (বা /skip):</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_POST_BUTTON

async def post_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text if update.message.text != '/skip' else db.get_config('btn_text')
    context.user_data['post_wizard']['button_text'] = txt
    
    channels = db.get_channels()
    buttons = [[{"text": f"📤 {c['name']}", "callback": f"post_to_{c['id']}"}] for c in channels]
    buttons.append([{"text": "📤 সব চ্যানেলে পোস্ট করুন", "callback": "post_to_all"}])
    
    await update.message.reply_text("✅ <b>টার্গেট চ্যানেল সিলেক্ট করুন:</b>", reply_markup=ui.create_keyboard(buttons, add_back=False), parse_mode=ParseMode.HTML)
    return Config.STATE_POST_CONFIRM

async def post_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = context.user_data.get('post_wizard', {})
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(data.get('button_text', 'ক্লিক করুন'), url=db.get_config('watch_url'))]])
    
    targets = db.get_channels() if query.data == "post_to_all" else [c for c in db.get_channels() if str(c['id']) == query.data.replace("post_to_", "")]
    
    await query.message.edit_text(f"⏳ {len(targets)} টি চ্যানেলে পাঠানো হচ্ছে...")
    
    for ch in targets:
        try:
            if data['type'] == 'photo': 
                await context.bot.send_photo(ch['id'], data['media'], caption=data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
            elif data['type'] == 'video': 
                await context.bot.send_video(ch['id'], data['media'], caption=data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
            else: 
                await context.bot.send_message(ch['id'], data['caption'], reply_markup=btn, parse_mode=ParseMode.HTML)
        except: 
            pass
        
    await query.message.reply_text("✅ <b>পোস্টিং সম্পূর্ণ!</b>", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = await update.message.reply_text(f"⏳ {len(users)} জন ইউজারকে ব্রডকাস্ট করা হচ্ছে...")
    count = 0
    for uid in users:
        try:
            await update.message.copy(uid)
            count += 1
            await asyncio.sleep(0.05)
        except: 
            pass
    await msg.edit_text(f"✅ <b>ব্রডকাস্ট {count} জন ইউজারকে পাঠানো হয়েছে!</b>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def add_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cid'] = update.message.text
    await update.message.reply_text("📝 <b>চ্যানেলের নাম:</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_CHANNEL_ADD_NAME

async def add_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cname'] = update.message.text
    await update.message.reply_text("🔗 <b>চ্যানেল লিংক:</b>", parse_mode=ParseMode.HTML)
    return Config.STATE_CHANNEL_ADD_LINK

async def add_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if db.add_channel(context.user_data['cid'], context.user_data['cname'], update.message.text):
        await update.message.reply_text("✅ চ্যানেল অ্যাড করা হয়েছে!", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ ব্যর্থ!", parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ বাতিল করা হয়েছে।")
    context.user_data.clear()
    return ConversationHandler.END

# ==============================================================================
# 🚀 মেইন অ্যাপ্লিকেশন
# ==============================================================================

def main():
    application = ApplicationBuilder().token(Config.TOKEN).build()
    
    # হ্যান্ডলারস
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("backup", backup_command))
    
    # কনভারসেশন: কনফিগ এডিট
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^edit_')],
        states={Config.STATE_EDIT_CONFIG: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_config_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # কনভারসেশন: পোস্ট
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
    
    # কনভারসেশন: চ্যানেল অ্যাড
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^add_channel_start$')],
        states={
            Config.STATE_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_id)],
            Config.STATE_CHANNEL_ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_name)],
            Config.STATE_CHANNEL_ADD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel_link)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))

    # কনভারসেশন: ব্রডকাস্ট
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^broadcast_start$')],
        states={Config.STATE_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    ))
    
    # গ্লোবাল কলব্যাক
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🤖 বট সফলভাবে শুরু হয়েছে...")
    application.run_polling()

if __name__ == "__main__":
    main()
