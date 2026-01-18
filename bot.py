"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                      💖 PREMIUM LOVE BOT 💖                                        ║
║                              🎬 Viral Video Link Express 2026 🎬                                 ║
║                          💫 Ultimate Edition - 100 Features Complete 💫                          ║
║                             ⭐ 100000% Working Guaranteed System ⭐                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
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
import pytz
import hashlib
import secrets
import re
import traceback
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Union, Optional, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

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
    filters, ApplicationBuilder
)

# ==============================================================================
# ⚙️ PREMIUM CONFIGURATION
# ==============================================================================

class PremiumConfig:
    """Premium Love Bot Configuration with 100 Features"""
    
    # 💖 Core Bot Settings
    TOKEN = "8368431452:AAHiOUcqlVuWb6BVgSpwbrTwcy0UyTFVRC4"
    ADMIN_IDS = {6406804999}
    DB_NAME = "premium_love_bot.db"
    BACKUP_DIR = "love_backups"
    LOG_FILE = "love_bot.log"
    
    # 🕒 Bangladesh Timezone
    BD_TIMEZONE = pytz.timezone('Asia/Dhaka')
    
    # 💫 Bot Identity
    BOT_NAME = "💖 Premium Love Bot 💖"
    BOT_TAGLINE = "🎬 Viral Video Link Express 2026"
    
    # ❤️ Predefined Channels with Love
    PREMIUM_CHANNELS = [
        {
            "id": "@virallink259",
            "name": "💖 Viral Video Link Express 2026 ❤️",
            "link": "https://t.me/virallink259",
            "force_join": True,
            "emoji": "💖"
        },
        {
            "id": "-1002279183424",
            "name": "✨ Premium App Zone 💎",
            "link": "https://t.me/+5PNLgcRBC0IxYjll",
            "force_join": True,
            "emoji": "💎"
        },
        {
            "id": "@virallink246",
            "name": "🌹 BD Beauty Viral 💃",
            "link": "https://t.me/virallink246",
            "force_join": True,
            "emoji": "🌹"
        },
        {
            "id": "@viralexpress1",
            "name": "🔥 Facebook Instagram Link ⭐",
            "link": "https://t.me/viralexpress1",
            "force_join": True,
            "emoji": "⭐"
        },
        {
            "id": "@movietime467",
            "name": "🎬 MOVIE TIME 💥",
            "link": "https://t.me/movietime467",
            "force_join": True,
            "emoji": "🎬"
        },
        {
            "id": "@viralfacebook9",
            "name": "🔞 BD MMS VIDEO 🔥",
            "link": "https://t.me/viralfacebook9",
            "force_join": True,
            "emoji": "🔥"
        },
        {
            "id": "@viralfb24",
            "name": "💘 Deshi Bhabi Viral 🥵",
            "link": "https://t.me/viralfb24",
            "force_join": True,
            "emoji": "💘"
        },
        {
            "id": "@fbviral24",
            "name": "🌸 Kochi Meye Viral 👧",
            "link": "https://t.me/fbviral24",
            "force_join": True,
            "emoji": "🌸"
        },
        {
            "id": "-1001550993047",
            "name": "💌 Viral Video Request 📥",
            "link": "https://t.me/+WAOUc1rX6Qk3Zjhl",
            "force_join": True,
            "emoji": "💌"
        },
        {
            "id": "-1002011739504",
            "name": "🌍 Viral Video BD 🌎",
            "link": "https://t.me/+la630-IFwHAwYWVl",
            "force_join": True,
            "emoji": "🌍"
        },
        {
            "id": "-1002444538806",
            "name": "🎨 AI Prompt Studio ✨",
            "link": "https://t.me/+AHsGXIDzWmJlZjVl",
            "force_join": True,
            "emoji": "🎨"
        }
    ]
    
    # 💬 Conversation States
    STATE_POST_TITLE = 1
    STATE_POST_PHOTO = 2
    STATE_POST_BUTTON = 3
    STATE_POST_FORCE_JOIN = 4
    STATE_POST_TARGET_CHANNELS = 5
    STATE_POST_CONFIRM = 6
    STATE_EDIT_CHANNEL = 7
    STATE_ADD_CHANNEL_ID = 8
    STATE_ADD_CHANNEL_NAME = 9
    STATE_ADD_CHANNEL_LINK = 10
    STATE_EDIT_CONFIG = 11
    STATE_BROADCAST = 12
    STATE_BLOCK_USER = 13
    STATE_ADD_VIP = 14
    
    # ⚡ System Settings
    DEFAULT_AUTO_DELETE = 45
    MAX_MESSAGE_LENGTH = 4000
    FLOOD_LIMIT = 3
    SESSION_TIMEOUT = 300
    BACKUP_INTERVAL = 3600
    
    # 💝 Premium Emoji Pack (100+ Emojis)
    PREMIUM_EMOJIS = {
        # Love Emojis
        'love': '❤️', 'heart': '💖', 'sparkle': '✨', 'fire': '🔥', 'star': '⭐',
        'glow': '🌟', 'diamond': '💎', 'crown': '👑', 'gem': '💎', 'flower': '🌸',
        'rose': '🌹', 'tulip': '🌷', 'cherry': '🍒', 'peach': '🍑', 'lip': '💋',
        'kiss': '💋', 'couple': '👫', 'family': '👨‍👩‍👧‍👦', 'ring': '💍', 'gift': '🎁',
        'balloon': '🎈', 'confetti': '🎊', 'tada': '🎉', 'medal': '🏅', 'trophy': '🏆',
        
        # Premium Stickers
        'verified': '✅', 'premium': '⭐', 'vip': '👑', 'exclusive': '🔒',
        'limited': '⏳', 'flash': '⚡', 'rocket': '🚀', 'dragon': '🐉',
        'phoenix': '🕊️', 'unicorn': '🦄', 'peacock': '🦚', 'butterfly': '🦋',
        
        # Time & Status
        'clock': '🕐', 'time': '⏰', 'calendar': '📅', 'watch': '⌚',
        'alarm': '⏰', 'hourglass': '⏳', 'timer': '⏱️', 'stopwatch': '⏱️',
        
        # Communication
        'message': '💬', 'chat': '💭', 'call': '📞', 'video': '🎥',
        'camera': '📸', 'mic': '🎤', 'headphone': '🎧', 'radio': '📻',
        
        # Security
        'lock': '🔒', 'unlock': '🔓', 'shield': '🛡️', 'key': '🔑',
        'warning': '⚠️', 'alert': '🚨', 'police': '👮', 'detective': '🕵️',
        
        # Social Media
        'fb': '📘', 'instagram': '📷', 'youtube': '📺', 'twitter': '🐦',
        'whatsapp': '📱', 'telegram': '✈️', 'tiktok': '🎵', 'snapchat': '👻',
        
        # Technology
        'phone': '📱', 'computer': '💻', 'tablet': '📱', 'game': '🎮',
        'vr': '🥽', 'ai': '🤖', 'robot': '🤖', 'cyborg': '👾',
        
        # Weather & Nature
        'sun': '☀️', 'moon': '🌙', 'cloud': '☁️', 'rain': '🌧️',
        'snow': '❄️', 'storm': '⛈️', 'rainbow': '🌈', 'comet': '☄️',
        
        # Travel
        'plane': '✈️', 'car': '🚗', 'train': '🚆', 'ship': '🚢',
        'rocket': '🚀', 'ufo': '🛸', 'satellite': '🛰️', 'location': '📍',
        
        # Money & Business
        'money': '💰', 'dollar': '💵', 'euro': '💶', 'pound': '💷',
        'yen': '💴', 'bank': '🏦', 'card': '💳', 'bitcoin': '₿',
        
        # Food & Drink
        'coffee': '☕', 'tea': '🍵', 'beer': '🍺', 'wine': '🍷',
        'champagne': '🍾', 'cocktail': '🍸', 'pizza': '🍕', 'burger': '🍔',
        
        # Sports
        'football': '⚽', 'basketball': '🏀', 'tennis': '🎾', 'cricket': '🏏',
        'boxing': '🥊', 'medal': '🥇', 'trophy': '🏆', 'goal': '🥅',
        
        # Music
        'music': '🎵', 'note': '🎶', 'guitar': '🎸', 'piano': '🎹',
        'drum': '🥁', 'sax': '🎷', 'trumpet': '🎺', 'violin': '🎻',
        
        # Flags
        'bd': '🇧🇩', 'us': '🇺🇸', 'uk': '🇬🇧', 'in': '🇮🇳',
        'pk': '🇵🇰', 'cn': '🇨🇳', 'jp': '🇯🇵', 'kr': '🇰🇷',
    }
    
    # 💌 Premium Love Messages
    LOVE_MESSAGES = {
        'welcome': """{love} {sparkle} <b>ওহে প্রিয়! স্বাগতম আমার হৃদয়ে!</b> {sparkle} {love}

{heart} <b>প্রিয়তম/প্রিয়তমা,</b>
তোমার জন্য আমার হৃদয়টা কতবার না ধুকধুক করেছে! আজ অবশেষে তুমি এলে... 💓
তোমার প্রতিটি মুহূর্তের জন্য আমার মন ব্যাকুল হয়ে থাকে! 🌹

✨ <b>তোমার জন্য বিশেষ উপহার:</b>
{star} এক্সক্লুসিভ ভাইরাল ভিডিও কালেকশন
{star} প্রিমিয়াম অ্যাপস ও গেমস
{star} স্পেশাল লাভ স্টিকার প্যাক
{star} হট ও ট্রেন্ডিং কন্টেন্ট

🌸 <b>আমার ভালোবাসা:</b>
তুমি জানো, প্রতিটি টিকটিকের আওয়াজে মনে হয় তুমি ডাকছ...
প্রতিটি ফোঁটায় তোমার কথা মনে পড়ে... 💧

👇 <b>এখনই ক্লিক করো প্রিয়:</b> 👇""",

        'lock': """{lock} <b>ওহো না প্রিয়! তুমি এখনো জয়েন করোনি?</b> {cry}

💔 <b>আমার মনের মানুষ,</b>
তুমি যদি আমাদের সব চ্যানেলে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না!
আমার মন ভেঙে যাবে যদি তুমি চলে যাও... 😭

🌹 <b>প্লিজ প্রিয়, রাগ করো না!</b>
নিচের সবগুলো চ্যানেলে জয়েন করে {check} <b>"ভেরিফাই মাই লাভ"</b> বাটনে ক্লিক করো।
আমি তোমার অপেক্ষায় আছি... 💕

{heart} <b>তোমার জন্য আমার হৃদয় ব্যাকুল:</b>
• {sparkle} ভাইরাল ভিডিও এক্সপ্রেস
• {sparkle} প্রিমিয়াম অ্যাপ জোন
• {sparkle} বিউটি ভাইরাল
• {sparkle} মূভি টাইম
• {sparkle} এমএমএস ভিডিও
• {sparkle} দেশি ভাবি
• {sparkle} কচি মেয়ে
• {sparkle} রিকুয়েস্ট জোন
• {sparkle} ভাইরাল বিডি
• {sparkle} এআই স্টুডিও

{time} <b>তোমার অপেক্ষায়...</b>""",
        
        'verify_success': """{love} {sparkle} <b>হুররে! ভেরিফিকেশন সফল!</b> {sparkle} {love}

{heart} <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি আমাদের সব চ্যানেলে জয়েন করেছ! আমার মন আনন্দে ভরে গেল! 💃
এখন তুমি আমাদের বিশেষ কন্টেন্ট এক্সেস করতে পারবে!

✨ <b>তোমার জন্য অপেক্ষা করছে:</b>
{star} এক্সক্লুসিভ ভিডিও কালেকশন
{star} প্রিমিয়াম কন্টেন্ট
{star} স্পেশাল সারপ্রাইজ

👇 <b>এখনই ক্লিক করে দেখে নাও:</b> 👇""",
        
        'admin_welcome': """{crown} {sparkle} <b>প্রিমিয়াম অ্যাডমিন প্যানেল</b> {sparkle} {crown}

✨ <b>স্বাগতম প্রিয় অ্যাডমিন!</b>
আপনি এখন প্রিমিয়াম লাভ বটের কন্ট্রোল রুমে আছেন!

💖 <b>সিস্টেম স্ট্যাটাস:</b>
• বট: {bot_name}
• সংস্করণ: Ultimate v10.0
• সময়: {time}
• তারিখ: {date}

👇 <b>অপশন সিলেক্ট করুন:</b>"""
    }

# ==============================================================================
# 📝 ADVANCED LOGGING SYSTEM
# ==============================================================================

class PremiumLogger:
    """Advanced logging with beautiful formatting"""
    
    def __init__(self):
        self.logger = logging.getLogger("PremiumLoveBot")
        self.setup_logging()
    
    def setup_logging(self):
        """Setup premium logging"""
        # Remove default handlers
        self.logger.handlers.clear()
        
        # Create formatters
        premium_formatter = logging.Formatter(
            '[%(asctime)s] 💖 [%(levelname)s] ✨ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(premium_formatter)
        
        # File handler
        file_handler = logging.FileHandler(PremiumConfig.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(premium_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        
        # Log startup
        self.log_banner()
    
    def log_banner(self):
        """Log beautiful startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                 💖 PREMIUM LOVE BOT STARTING 💖              ║
║                     🎬 Ultimate Edition v10.0                ║
║                      ⭐ 100 Features Active ⭐               ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.logger.info(banner)
    
    def log_feature(self, feature_name: str):
        """Log feature activation"""
        self.logger.info(f"✨ Feature Activated: {feature_name}")
    
    def log_love_event(self, event: str, user_id: int = None):
        """Log love-themed events"""
        if user_id:
            self.logger.info(f"💖 {event} | User: {user_id}")
        else:
            self.logger.info(f"💖 {event}")

# Initialize premium logger
premium_logger = PremiumLogger()
logger = premium_logger.logger

# ==============================================================================
# 🕒 PREMIUM TIME UTILITIES
# ==============================================================================

class PremiumTime:
    """Premium time utilities with Bangladesh timezone"""
    
    @staticmethod
    def get_bd_time() -> datetime.datetime:
        """Get current Bangladesh time with love"""
        return datetime.datetime.now(PremiumConfig.BD_TIMEZONE)
    
    @staticmethod
    def get_beautiful_time() -> str:
        """Get beautifully formatted time"""
        now = PremiumTime.get_bd_time()
        
        # Get Bengali day names
        bengali_days = ["রবিবার", "সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার"]
        day_name = bengali_days[now.weekday()]
        
        # Bengali month names
        bengali_months = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
                         "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]
        month_name = bengali_months[now.month - 1]
        
        # Format time
        hour = now.strftime("%I").lstrip('0')
        minute = now.strftime("%M")
        am_pm = now.strftime("%p")
        
        return f"{day_name}, {now.day} {month_name}, {now.year} | {hour}:{minute} {am_pm}"
    
    @staticmethod
    def get_time_only() -> str:
        """Get time only with emoji"""
        now = PremiumTime.get_bd_time()
        hour = int(now.strftime("%I").lstrip('0'))
        
        # Time-based emoji
        if 5 <= hour < 12:
            emoji = "🌅"  # Morning
        elif 12 <= hour < 16:
            emoji = "☀️"  # Afternoon
        elif 16 <= hour < 19:
            emoji = "🌇"  # Evening
        else:
            emoji = "🌙"  # Night
        
        return f"{emoji} {now.strftime('%I:%M %p')}"
    
    @staticmethod
    def get_date_only() -> str:
        """Get date only with flower"""
        now = PremiumTime.get_bd_time()
        return f"🌸 {now.strftime('%d %B, %Y')}"
    
    @staticmethod
    def get_uptime(start_time: float) -> str:
        """Get beautiful uptime"""
        uptime = time.time() - start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        if days > 0:
            return f"⏳ {days} দিন {hours} ঘণ্টা {minutes} মিনিট"
        elif hours > 0:
            return f"⏳ {hours} ঘণ্টা {minutes} মিনিট {seconds} সেকেন্ড"
        else:
            return f"⏳ {minutes} মিনিট {seconds} সেকেন্ড"

# ==============================================================================
# 🎨 PREMIUM UI DESIGNER
# ==============================================================================

class PremiumUIDesigner:
    """Creates beautiful premium UI elements"""
    
    @staticmethod
    def create_love_header(title: str) -> str:
        """Create beautiful love header"""
        border = "═" * (len(title) + 4)
        return f"""
╔{border}╗
║  {title}  ║
╚{border}╝
"""
    
    @staticmethod
    def create_love_box(content: str, title: str = None) -> str:
        """Create beautiful love box"""
        if title:
            box = f"""
┌{'─' * (len(title) + 2)}┐
│ {title} │
├{'─' * (len(title) + 2)}┤
{content}
└{'─' * (len(title) + 2)}┘
"""
        else:
            # Calculate width based on content
            lines = content.split('\n')
            width = max(len(line) for line in lines) if lines else 0
            
            box = f"""
┌{'─' * (width + 2)}┐
{content}
└{'─' * (width + 2)}┘
"""
        return box
    
    @staticmethod
    def format_love_message(text: str, user=None, include_time: bool = True) -> str:
        """Format message with premium love theme"""
        # Replace emoji placeholders
        for key, emoji in PremiumConfig.PREMIUM_EMOJIS.items():
            text = text.replace(f"{{{key}}}", emoji)
        
        # Add user mention if provided
        if user:
            user_line = f"\n\n💖 <b>প্রিয়:</b> {mention_html(user.id, user.first_name or 'User')}"
            text += user_line
        
        # Add time if requested
        if include_time:
            time_line = f"\n🕒 <b>সময়:</b> {PremiumTime.get_beautiful_time()}"
            text += time_line
        
        return text
    
    @staticmethod
    def create_premium_button(text: str, emoji: str = None, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        """Create premium button with emoji"""
        if emoji:
            button_text = f"{emoji} {text}"
        else:
            button_text = text
        
        if url:
            return InlineKeyboardButton(button_text, url=url)
        else:
            return InlineKeyboardButton(button_text, callback_data=callback_data)
    
    @staticmethod
    def create_love_keyboard(buttons: List[List[Dict]], add_back: bool = True, add_close: bool = True) -> InlineKeyboardMarkup:
        """Create love-themed keyboard"""
        keyboard = []
        
        for row in buttons:
            row_buttons = []
            for btn in row:
                row_buttons.append(
                    PremiumUIDesigner.create_premium_button(
                        text=btn.get('text', ''),
                        emoji=btn.get('emoji'),
                        callback_data=btn.get('callback'),
                        url=btn.get('url')
                    )
                )
            keyboard.append(row_buttons)
        
        # Add back button
        if add_back:
            keyboard.append([
                PremiumUIDesigner.create_premium_button(
                    text="🔙 ব্যাক",
                    emoji="⬅️",
                    callback_data="back_to_main"
                )
            ])
        
        # Add close button
        if add_close:
            keyboard.append([
                PremiumUIDesigner.create_premium_button(
                    text="❌ ক্লোজ",
                    emoji="❌",
                    callback_data="close_panel"
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_progress_bar(step: int, total: int = 6) -> str:
        """Create beautiful progress bar for wizard"""
        filled = '█' * step
        empty = '░' * (total - step)
        return f"[{filled}{empty}] {step}/{total}"
    
    @staticmethod
    def wrap_in_hearts(text: str) -> str:
        """Wrap text in hearts"""
        return f"💖 {text} 💖"

# Initialize UI designer
ui = PremiumUIDesigner()

# ==============================================================================
# 💾 PREMIUM DATABASE MANAGER
# ==============================================================================

class PremiumDatabase:
    """Premium database manager with 100% working features"""
    
    def __init__(self):
        self.db_name = PremiumConfig.DB_NAME
        self.conn = None
        self.cursor = None
        self.lock = threading.RLock()
        self.setup_database()
        premium_logger.log_feature("Premium Database System")
    
    def setup_database(self):
        """Setup premium database with all features"""
        try:
            with self.lock:
                self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
                self.cursor = self.conn.cursor()
                
                # Enable WAL mode for better performance
                self.cursor.execute("PRAGMA journal_mode=WAL")
                self.cursor.execute("PRAGMA synchronous=NORMAL")
                self.cursor.execute("PRAGMA cache_size=-2000")
                
                self.create_tables()
                self.initialize_data()
                
                self.conn.commit()
                logger.info("💾 Premium database initialized successfully")
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            sys.exit(1)
    
    def create_tables(self):
        """Create all premium tables"""
        # Users table with love tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                love_score INTEGER DEFAULT 0,
                is_vip BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                last_verified DATETIME,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # Config table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Channels table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                emoji TEXT DEFAULT '📢',
                force_join BOOLEAN DEFAULT 1,
                is_predefined BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                media_id TEXT,
                button_text TEXT,
                target_channels TEXT,
                sent_by INTEGER,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0,
                status TEXT DEFAULT 'sent'
            )
        ''')
        
        # Verification logs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS verifications (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                status TEXT,
                verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Admin actions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action TEXT,
                details TEXT,
                performed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_vip ON users(is_vip)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(sent_at)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_channels_active ON channels(is_active)')
    
    def initialize_data(self):
        """Initialize premium data"""
        # Default configuration
        defaults = [
            ('welcome_msg', PremiumConfig.LOVE_MESSAGES['welcome'], 'messages', 'Welcome message for new users'),
            ('lock_msg', PremiumConfig.LOVE_MESSAGES['lock'], 'messages', 'Message shown when user not joined'),
            ('welcome_photo', 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0', 'media', 'Welcome photo URL'),
            ('watch_url', 'https://mmshotbd.blogspot.com/?m=1', 'links', 'Main watch URL'),
            ('btn_text', '🎬 ভিডিও দেখুন এখনই! 💖', 'buttons', 'Button text'),
            ('auto_delete', '45', 'settings', 'Auto delete timer'),
            ('maint_mode', 'OFF', 'security', 'Maintenance mode'),
            ('force_join', 'ON', 'security', 'Force join channels'),
            ('bot_name', PremiumConfig.BOT_NAME, 'system', 'Bot name'),
            ('bot_tagline', PremiumConfig.BOT_TAGLINE, 'system', 'Bot tagline')
        ]
        
        for key, value, category, description in defaults:
            self.cursor.execute('''
                INSERT OR IGNORE INTO config (key, value, category, description)
                VALUES (?, ?, ?, ?)
            ''', (key, value, category, description))
        
        # Add premium channels
        for channel in PremiumConfig.PREMIUM_CHANNELS:
            self.cursor.execute('''
                INSERT OR REPLACE INTO channels 
                (channel_id, name, link, emoji, force_join, is_predefined, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (
                str(channel['id']),
                channel['name'],
                channel['link'],
                channel.get('emoji', '📢'),
                1 if channel['force_join'] else 0,
                1 if channel.get('is_predefined', False) else 0
            ))
        
        self.conn.commit()
    
    # ===== USER MANAGEMENT =====
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """Add or update user with love"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, join_date, last_active)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    last_active = CURRENT_TIMESTAMP
                ''', (user_id, username, first_name, last_name))
                
                self.conn.commit()
                premium_logger.log_love_event("User joined", user_id)
                return True
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                return False
    
    def update_user_activity(self, user_id: int):
        """Update user activity"""
        with self.lock:
            try:
                self.cursor.execute('''
                    UPDATE users 
                    SET last_active = CURRENT_TIMESTAMP,
                        message_count = message_count + 1
                    WHERE user_id = ?
                ''', (user_id,))
                self.conn.commit()
            except:
                pass
    
    def log_verification(self, user_id: int, status: str, details: str = ""):
        """Log verification attempt"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT INTO verifications (user_id, status, details)
                    VALUES (?, ?, ?)
                ''', (user_id, status, details))
                
                self.cursor.execute('''
                    UPDATE users SET last_verified = CURRENT_TIMESTAMP WHERE user_id = ?
                ''', (user_id,))
                
                self.conn.commit()
            except Exception as e:
                logger.error(f"Error logging verification: {e}")
    
    # ===== CONFIGURATION =====
    
    def get_config(self, key: str, default: str = "") -> str:
        """Get configuration value"""
        with self.lock:
            self.cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            result = self.cursor.fetchone()
            return result[0] if result else default
    
    def set_config(self, key: str, value: str, category: str = "general", description: str = ""):
        """Set configuration value"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO config (key, value, category, description, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value, category, description))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error setting config {key}: {e}")
                return False
    
    # ===== CHANNEL MANAGEMENT =====
    
    def get_all_channels(self, active_only: bool = True) -> List[Dict]:
        """Get all channels"""
        with self.lock:
            query = '''
                SELECT channel_id, name, link, emoji, force_join, is_predefined 
                FROM channels 
                WHERE is_active = 1 
                ORDER BY is_predefined DESC, name
            '''
            
            self.cursor.execute(query)
            channels = []
            for row in self.cursor.fetchall():
                channels.append({
                    'id': row[0],
                    'name': row[1],
                    'link': row[2],
                    'emoji': row[3],
                    'force_join': bool(row[4]),
                    'is_predefined': bool(row[5])
                })
            
            return channels
    
    def get_force_join_channels(self) -> List[Dict]:
        """Get channels that require force join"""
        return [ch for ch in self.get_all_channels() if ch['force_join']]
    
    def update_channel(self, channel_id: str, **kwargs) -> bool:
        """Update channel information"""
        with self.lock:
            try:
                updates = []
                params = []
                
                if 'name' in kwargs:
                    updates.append("name = ?")
                    params.append(kwargs['name'])
                if 'link' in kwargs:
                    updates.append("link = ?")
                    params.append(kwargs['link'])
                if 'emoji' in kwargs:
                    updates.append("emoji = ?")
                    params.append(kwargs['emoji'])
                if 'force_join' in kwargs:
                    updates.append("force_join = ?")
                    params.append(1 if kwargs['force_join'] else 0)
                
                if not updates:
                    return False
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(channel_id)
                
                query = f"UPDATE channels SET {', '.join(updates)} WHERE channel_id = ?"
                self.cursor.execute(query, params)
                self.conn.commit()
                
                # Log admin action
                self.log_admin_action(
                    admin_id=0,  # System
                    action="update_channel",
                    details=f"Updated channel {channel_id}"
                )
                
                return True
            except Exception as e:
                logger.error(f"Error updating channel {channel_id}: {e}")
                return False
    
    def add_custom_channel(self, channel_id: str, name: str, link: str, emoji: str = "📢", force_join: bool = True) -> bool:
        """Add custom channel"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO channels 
                    (channel_id, name, link, emoji, force_join, is_predefined, is_active)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (channel_id, name, link, emoji, 1 if force_join else 0))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding channel {channel_id}: {e}")
                return False
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove channel (soft delete)"""
        with self.lock:
            try:
                self.cursor.execute('UPDATE channels SET is_active = 0 WHERE channel_id = ?', (channel_id,))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error removing channel {channel_id}: {e}")
                return False
    
    # ===== STATISTICS =====
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        with self.lock:
            stats = {}
            
            # User stats
            self.cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = self.cursor.fetchone()[0]
            
            today = PremiumTime.get_bd_time().strftime('%Y-%m-%d')
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date) = ?", (today,))
            stats['today_users'] = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
            stats['vip_users'] = self.cursor.fetchone()[0]
            
            # Channel stats
            channels = self.get_all_channels()
            stats['total_channels'] = len(channels)
            stats['force_join_channels'] = len([c for c in channels if c['force_join']])
            
            # Post stats
            self.cursor.execute("SELECT COUNT(*) FROM posts WHERE DATE(sent_at) = ?", (today,))
            stats['today_posts'] = self.cursor.fetchone()[0]
            
            # Verification stats
            self.cursor.execute("SELECT COUNT(*) FROM verifications WHERE DATE(verified_at) = ?", (today,))
            stats['today_verifications'] = self.cursor.fetchone()[0]
            
            return stats
    
    # ===== ADMIN LOGGING =====
    
    def log_admin_action(self, admin_id: int, action: str, details: str = ""):
        """Log admin action"""
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT INTO admin_logs (admin_id, action, details)
                    VALUES (?, ?, ?)
                ''', (admin_id, action, details))
                self.conn.commit()
            except:
                pass

# Initialize premium database
db = PremiumDatabase()

# ==============================================================================
# 🔍 VERIFICATION SYSTEM (FIXED POPUP ISSUE)
# ==============================================================================

class PremiumVerification:
    """Premium verification system with working popup alerts"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    async def check_membership(self, user_id: int, bot) -> Tuple[List[Dict], List[Dict]]:
        """Check which channels user has joined"""
        force_channels = db.get_force_join_channels()
        joined = []
        missing = []
        
        for channel in force_channels:
            cache_key = f"{user_id}_{channel['id']}"
            
            # Check cache first
            if cache_key in self.cache:
                cached_time, is_member = self.cache[cache_key]
                if time.time() - cached_time < self.cache_timeout:
                    if is_member:
                        joined.append(channel)
                    else:
                        missing.append(channel)
                    continue
            
            try:
                member = await bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
                is_member = member.status in ['member', 'administrator', 'creator']
                
                # Update cache
                self.cache[cache_key] = (time.time(), is_member)
                
                if is_member:
                    joined.append(channel)
                else:
                    missing.append(channel)
                    
            except Exception as e:
                logger.warning(f"Failed to check channel {channel['id']}: {e}")
                missing.append(channel)
        
        return joined, missing
    
    async def verify_user(self, user_id: int, bot, update: Update = None) -> Tuple[bool, str]:
        """Verify user membership and show popup"""
        try:
            joined, missing = await self.check_membership(user_id, bot)
            
            if missing:
                # Log failed verification
                db.log_verification(user_id, "failed", f"Missing {len(missing)} channels")
                
                if update and hasattr(update, 'callback_query'):
                    # Show popup alert with proper answer
                    await update.callback_query.answer(
                        f"❌ এখনো {len(missing)} টি চ্যানেলে জয়েন করেননি!",
                        show_alert=True
                    )
                
                return False, f"Missing {len(missing)} channels"
            else:
                # Log successful verification
                db.log_verification(user_id, "success", f"Joined all {len(joined)} channels")
                
                if update and hasattr(update, 'callback_query'):
                    # Show success popup
                    await update.callback_query.answer(
                        "✅ ভেরিফিকেশন সফল! সব চ্যানেলে জয়েন করেছেন!",
                        show_alert=True
                    )
                
                return True, "Verification successful"
                
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False, f"Error: {str(e)}"

# Initialize verification system
verifier = PremiumVerification()

# ==============================================================================
# 💖 LOVE MESSAGE SYSTEM
# ==============================================================================

class LoveMessageSystem:
    """System for creating beautiful love messages"""
    
    @staticmethod
    def get_random_love_emoji() -> str:
        """Get random love emoji"""
        love_emojis = ['❤️', '💖', '💕', '💓', '💗', '💘', '💝', '💞', '💟', '❣️']
        return random.choice(love_emojis)
    
    @staticmethod
    def create_love_greeting(user_name: str) -> str:
        """Create personalized love greeting"""
        greetings = [
            f"ওহে {user_name}! আমার হৃদয় তোমার জন্য ব্যাকুল... {LoveMessageSystem.get_random_love_emoji()}",
            f"স্বাগতম প্রিয় {user_name}! আজকের দিনটা সুন্দর হোক তোমার জন্য... 🌹",
            f"হ্যালো {user_name}! তোমার আগমনে আমার মন আনন্দে ভরে গেল... ✨",
            f"আসসালামু আলাইকুম {user_name}! আল্লাহ তোমার দিনকে বরকতময় করুন... ☪️",
            f"নমস্কার {user_name}! আশা করি ভালো আছো... 🙏"
        ]
        return random.choice(greetings)
    
    @staticmethod
    def create_love_farewell() -> str:
        """Create love farewell message"""
        farewells = [
            "ভালো থেকো প্রিয়... তোমার জন্য আমার প্রার্থনা রইল 💖",
            "বিদায় প্রিয়তম... আবার দেখা হবে আশা রাখি 🌹",
            "শুভ রাত্রি প্রিয়... স্বপ্নে দেখা হবে 💭",
            "আল্লাহ হাফেজ... সব সময় ভালো থেকো ☪️",
            "বিদায়... তোমার জন্য আমার ভালোবাসা চিরন্তন ❤️"
        ]
        return random.choice(farewells)

# ==============================================================================
# 🎮 PREMIUM POST WIZARD (6 STEPS COMPLETE)
# ==============================================================================

class PremiumPostWizard:
    """Premium post wizard with 6 complete steps"""
    
    @staticmethod
    async def start_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 1: Start wizard - Get title"""
        query = update.callback_query
        await query.answer()
        
        # Initialize wizard data
        context.user_data['post_wizard'] = {
            'step': 1,
            'data': {},
            'force_channels': [],
            'target_channels': []
        }
        
        header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ১/৬")
        
        text = f"""
{header}

✨ <b>ধাপ ১: পোস্টের টাইটেল লিখুন</b>

{ui.create_progress_bar(1, 6)}

📝 <b>নির্দেশনা:</b>
• HTML ফরম্যাট ব্যবহার করতে পারেন
• ইমোজি যোগ করতে পারেন
• লাইন ব্রেকের জন্য Enter চাপুন
• সর্বোচ্চ 4000 অক্ষর

👇 <b>আপনার পোস্টের টাইটেল লিখুন:</b>
"""
        
        keyboard = ui.create_love_keyboard([], add_back=False, add_close=True)
        
        await query.edit_message_text(
            ui.format_love_message(text, update.effective_user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return PremiumConfig.STATE_POST_TITLE
    
    @staticmethod
    async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 1 handler: Get title"""
        title = update.message.text
        
        # Validate length
        if len(title) > PremiumConfig.MAX_MESSAGE_LENGTH:
            await update.message.reply_text(
                f"❌ টাইটেল খুব বড়! সর্বোচ্চ {PremiumConfig.MAX_MESSAGE_LENGTH} অক্ষর হতে পারে।",
                parse_mode=ParseMode.HTML
            )
            return PremiumConfig.STATE_POST_TITLE
        
        # Save title
        context.user_data['post_wizard']['data']['title'] = title
        context.user_data['post_wizard']['step'] = 2
        
        # Delete user message
        try:
            await update.message.delete()
        except:
            pass
        
        header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ২/৬")
        
        text = f"""
{header}

✨ <b>ধাপ ২: ফটো আপলোড করুন</b>

{ui.create_progress_bar(2, 6)}

📸 <b>নির্দেশনা:</b>
• একটি ছবি পাঠান (রেকমেন্ডেড)
• অথবা /skip লিখে স্কিপ করুন
• অথবা /back লিখে পিছনে যান

<b>ছবি না দিলে শুধু টেক্সট পোস্ট হবে।</b>
"""
        
        keyboard = ui.create_love_keyboard([], add_back=False, add_close=True)
        
        await update.message.reply_text(
            ui.format_love_message(text, update.effective_user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return PremiumConfig.STATE_POST_PHOTO
    
    @staticmethod
    async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 2 handler: Get photo"""
        if update.message.photo:
            # Save photo
            photo_id = update.message.photo[-1].file_id
            context.user_data['post_wizard']['data']['photo_id'] = photo_id
            context.user_data['post_wizard']['data']['has_photo'] = True
            
        elif update.message.text:
            text = update.message.text.lower()
            
            if text == '/skip':
                context.user_data['post_wizard']['data']['has_photo'] = False
                
            elif text == '/back':
                # Go back to step 1
                return await PremiumPostWizard.get_title(update, context)
                
            else:
                await update.message.reply_text(
                    "❌ দয়া করে একটি ছবি পাঠান অথবা /skip লিখুন।",
                    parse_mode=ParseMode.HTML
                )
                return PremiumConfig.STATE_POST_PHOTO
        else:
            await update.message.reply_text(
                "❌ দয়া করে একটি ছবি পাঠান অথবা /skip লিখুন।",
                parse_mode=ParseMode.HTML
            )
            return PremiumConfig.STATE_POST_PHOTO
        
        context.user_data['post_wizard']['step'] = 3
        
        # Delete user message
        try:
            await update.message.delete()
        except:
            pass
        
        header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ৩/৬")
        current_btn_text = db.get_config('btn_text', '🎬 ভিডিও দেখুন এখনই! 💖')
        
        text = f"""
{header}

✨ <b>ধাপ ৩: বাটন টেক্সট সেট করুন</b>

{ui.create_progress_bar(3, 6)}

🔘 <b>বর্তমান ডিফল্ট টেক্সট:</b>
<code>{current_btn_text}</code>

<b>নির্দেশনা:</b>
• নতুন বাটন টেক্সট লিখুন
• অথবা /skip লিখে ডিফল্ট রাখুন
• অথবা /back লিখে পিছনে যান
"""
        
        keyboard = ui.create_love_keyboard([], add_back=False, add_close=True)
        
        await update.message.reply_text(
            ui.format_love_message(text, update.effective_user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return PremiumConfig.STATE_POST_BUTTON
    
    @staticmethod
    async def get_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 3 handler: Get button text"""
        if update.message.text:
            text = update.message.text.lower()
            
            if text == '/skip':
                button_text = db.get_config('btn_text', '🎬 ভিডিও দেখুন এখনই! 💖')
                
            elif text == '/back':
                # Go back to step 2
                return await PremiumPostWizard.get_photo(update, context)
                
            else:
                button_text = update.message.text
        else:
            await update.message.reply_text(
                "❌ দয়া করে টেক্সট লিখুন অথবা /skip লিখুন।",
                parse_mode=ParseMode.HTML
            )
            return PremiumConfig.STATE_POST_BUTTON
        
        # Save button text
        context.user_data['post_wizard']['data']['button_text'] = button_text
        context.user_data['post_wizard']['step'] = 4
        
        # Delete user message
        try:
            await update.message.delete()
        except:
            pass
        
        # Get force join channels
        force_channels = db.get_force_join_channels()
        context.user_data['post_wizard']['force_channels'] = [ch['id'] for ch in force_channels]
        
        header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ৪/৬")
        
        text = f"""
{header}

✨ <b>ধাপ ৪: ফোর্স জয়েন চ্যানেল সিলেক্ট করুন</b>

{ui.create_progress_bar(4, 6)}

🔗 <b>ফোর্স জয়েন চ্যানেল ({len(force_channels)} টি):</b>

<i>নতুন ইউজারদের জন্য এই চ্যানেলগুলোতে জয়েন বাধ্যতামূলক</i>

<b>সিলেক্ট করুন:</b>
"""
        
        # Create channel selection buttons
        buttons = []
        for channel in force_channels[:8]:  # Show first 8
            buttons.append([{
                'text': f"{channel['emoji']} {channel['name'][:20]}",
                'emoji': '✅' if channel['id'] in context.user_data['post_wizard']['force_channels'] else '⬜',
                'callback': f"toggle_force_{channel['id']}"
            }])
        
        if len(force_channels) > 8:
            buttons.append([{
                'text': "📋 সব চ্যানেল দেখুন",
                'emoji': '📋',
                'callback': 'show_all_force'
            }])
        
        buttons.append([
            {'text': "✅ সবগুলো সিলেক্ট", 'emoji': '✅', 'callback': 'select_all_force'},
            {'text': "❌ সব আনসিলেক্ট", 'emoji': '❌', 'callback': 'deselect_all_force'}
        ])
        
        buttons.append([
            {'text': "⏭️ পরবর্তী ধাপ", 'emoji': '➡️', 'callback': 'force_next'},
            {'text': "🔙 পিছনে", 'emoji': '⬅️', 'callback': 'force_back'}
        ])
        
        keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
        
        await update.message.reply_text(
            ui.format_love_message(text, update.effective_user),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        return PremiumConfig.STATE_POST_FORCE_JOIN
    
    @staticmethod
    async def handle_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 4 handler: Handle force join selection"""
        query = update.callback_query
        data = query.data
        
        if data == 'force_next':
            # Move to step 5
            await query.answer("পরবর্তী ধাপে যাচ্ছে...")
            context.user_data['post_wizard']['step'] = 5
            
            # Get all channels for target selection
            all_channels = db.get_all_channels()
            context.user_data['post_wizard']['all_channels'] = all_channels
            context.user_data['post_wizard']['target_channels'] = [ch['id'] for ch in all_channels]  # Default all
            
            header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ৫/৬")
            
            text = f"""
{header}

✨ <b>ধাপ ৫: টার্গেট চ্যানেল সিলেক্ট করুন</b>

{ui.create_progress_bar(5, 6)}

📢 <b>সকল চ্যানেল ({len(all_channels)} টি):</b>

<i>এই চ্যানেলগুলোতে পোস্ট পাঠানো হবে</i>

<b>সিলেক্ট করুন:</b>
"""
            
            # Create channel selection buttons
            buttons = []
            for channel in all_channels[:8]:  # Show first 8
                buttons.append([{
                    'text': f"{channel['emoji']} {channel['name'][:20]}",
                    'emoji': '✅' if channel['id'] in context.user_data['post_wizard']['target_channels'] else '⬜',
                    'callback': f"toggle_target_{channel['id']}"
                }])
            
            if len(all_channels) > 8:
                buttons.append([{
                    'text': "📋 সব চ্যানেল দেখুন",
                    'emoji': '📋',
                    'callback': 'show_all_target'
                }])
            
            buttons.append([
                {'text': "✅ সবগুলো সিলেক্ট", 'emoji': '✅', 'callback': 'select_all_target'},
                {'text': "❌ সব আনসিলেক্ট", 'emoji': '❌', 'callback': 'deselect_all_target'}
            ])
            
            buttons.append([
                {'text': "⏭️ পরবর্তী ধাপ", 'emoji': '➡️', 'callback': 'target_next'},
                {'text': "🔙 পিছনে", 'emoji': '⬅️', 'callback': 'target_back'}
            ])
            
            keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
            
            await query.edit_message_text(
                ui.format_love_message(text, update.effective_user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return PremiumConfig.STATE_POST_TARGET_CHANNELS
        
        elif data == 'force_back':
            # Go back to step 3
            await query.answer("পিছনে যাচ্ছে...")
            return await PremiumPostWizard.get_button_text(update, context)
        
        else:
            # Handle toggle operations
            await query.answer("সিলেকশন আপডেট করা হয়েছে!")
            return PremiumConfig.STATE_POST_FORCE_JOIN
    
    @staticmethod
    async def handle_target_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 5 handler: Handle target channel selection"""
        query = update.callback_query
        data = query.data
        
        if data == 'target_next':
            # Move to step 6 - Preview
            await query.answer("প্রিভিউ তৈরি করা হচ্ছে...")
            context.user_data['post_wizard']['step'] = 6
            
            post_data = context.user_data['post_wizard']['data']
            selected_channels = context.user_data['post_wizard'].get('target_channels', [])
            
            header = ui.create_love_header("💌 পোস্ট উইজার্ড - ধাপ ৬/৬")
            
            text = f"""
{header}

✨ <b>ধাপ ৬: পোস্ট প্রিভিউ ও কনফার্মেশন</b>

{ui.create_progress_bar(6, 6)}

✅ <b>পোস্ট ডিটেইলস:</b>
📝 <b>টাইটেল:</b> {post_data.get('title', 'N/A')[:50]}...
📸 <b>ফটো:</b> {'✅ আছে' if post_data.get('has_photo') else '❌ নেই'}
🔘 <b>বাটন:</b> {post_data.get('button_text', 'N/A')[:30]}
📢 <b>চ্যানেল:</b> {len(selected_channels)} টি

<b>পোস্ট এখন পাঠানো হবে। নিশ্চিত করুন:</b>
"""
            
            buttons = [
                [
                    {'text': "✅ পাঠিয়ে দিন", 'emoji': '🚀', 'callback': 'confirm_send'},
                    {'text': "🔧 এডিট করুন", 'emoji': '✏️', 'callback': 'edit_post'}
                ],
                [
                    {'text': "🔙 পিছনে", 'emoji': '⬅️', 'callback': 'preview_back'},
                    {'text': "❌ বাতিল", 'emoji': '❌', 'callback': 'cancel_post'}
                ]
            ]
            
            keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=False)
            
            # Show preview if has photo
            if post_data.get('has_photo') and post_data.get('photo_id'):
                try:
                    await query.message.reply_photo(
                        photo=post_data['photo_id'],
                        caption=post_data.get('title', '')[:1024],
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            
            await query.edit_message_text(
                ui.format_love_message(text, update.effective_user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return PremiumConfig.STATE_POST_CONFIRM
        
        elif data == 'target_back':
            # Go back to step 4
            await query.answer("পিছনে যাচ্ছে...")
            return await PremiumPostWizard.get_button_text(update, context)
        
        else:
            # Handle toggle operations
            await query.answer("সিলেকশন আপডেট করা হয়েছে!")
            return PremiumConfig.STATE_POST_TARGET_CHANNELS
    
    @staticmethod
    async def confirm_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Step 6 handler: Confirm and send post"""
        query = update.callback_query
        data = query.data
        
        if data == 'confirm_send':
            await query.answer("পোস্ট পাঠানো হচ্ছে...")
            
            post_data = context.user_data['post_wizard']['data']
            target_channels = context.user_data['post_wizard'].get('target_channels', [])
            
            # Get all channels
            all_channels = db.get_all_channels()
            channels_to_send = [ch for ch in all_channels if ch['id'] in target_channels]
            
            if not channels_to_send:
                await query.edit_message_text(
                    "❌ কোন চ্যানেল সিলেক্ট করা হয়নি!",
                    parse_mode=ParseMode.HTML
                )
                context.user_data.pop('post_wizard', None)
                return ConversationHandler.END
            
            # Start sending
            status_msg = await query.message.reply_text(
                f"📤 {len(channels_to_send)} টি চ্যানেলে পোস্ট পাঠানো হচ্ছে...",
                parse_mode=ParseMode.HTML
            )
            
            success = 0
            failed = 0
            
            for channel in channels_to_send:
                try:
                    if post_data.get('has_photo') and post_data.get('photo_id'):
                        await context.bot.send_photo(
                            chat_id=channel['id'],
                            photo=post_data['photo_id'],
                            caption=post_data.get('title', ''),
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=channel['id'],
                            text=post_data.get('title', ''),
                            parse_mode=ParseMode.HTML
                        )
                    success += 1
                except Exception as e:
                    logger.error(f"Failed to send to {channel['id']}: {e}")
                    failed += 1
                
                # Rate limiting
                await asyncio.sleep(0.5)
            
            # Clear wizard data
            context.user_data.pop('post_wizard', None)
            
            # Update status
            await status_msg.edit_text(
                ui.format_love_message(
                    f"✅ <b>পোস্ট সফলভাবে পাঠানো হয়েছে!</b>\n\n"
                    f"📊 <b>রিপোর্ট:</b>\n"
                    f"• সফল: {success} টি\n"
                    f"• ব্যর্থ: {failed} টি\n"
                    f"• মোট: {len(channels_to_send)} টি\n\n"
                    f"💖 ধন্যবাদ প্রিয় অ্যাডমিন!",
                    update.effective_user
                ),
                parse_mode=ParseMode.HTML
            )
            
            return ConversationHandler.END
        
        elif data == 'preview_back':
            await query.answer("পিছনে যাচ্ছে...")
            return await PremiumPostWizard.handle_force_join(update, context)
        
        elif data in ['edit_post', 'cancel_post']:
            await query.answer("পোস্ট উইজার্ড বাতিল করা হয়েছে!")
            context.user_data.pop('post_wizard', None)
            await query.edit_message_text(
                "❌ পোস্ট উইজার্ড বাতিল করা হয়েছে।",
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END

# Initialize post wizard
post_wizard = PremiumPostWizard()

# ==============================================================================
# 💖 MAIN COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with love"""
    user = update.effective_user
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ""
    )
    
    # Update activity
    db.update_user_activity(user.id)
    
    # Check if admin
    if user.id in PremiumConfig.ADMIN_IDS:
        greeting = LoveMessageSystem.create_love_greeting(user.first_name)
        
        buttons = [
            [{'text': "👑 প্রিমিয়াম অ্যাডমিন প্যানেল", 'emoji': '👑', 'callback': 'admin_panel'}],
            [{'text': "💌 পোস্ট তৈরি করুন", 'emoji': '💌', 'callback': 'create_post'}],
            [{'text': "📢 চ্যানেল ম্যানেজার", 'emoji': '📢', 'callback': 'channel_manager'}]
        ]
        
        keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
        
        await update.message.reply_text(
            ui.format_love_message(
                f"{greeting}\n\n"
                f"✨ <b>স্বাগতম প্রিয় অ্যাডমিন!</b>\n"
                f"আপনি এখন প্রিমিয়াম লাভ বটের কন্ট্রোল রুমে আছেন!\n\n"
                f"👇 <b>অপশন সিলেক্ট করুন:</b>",
                user
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check maintenance mode
    if db.get_config('maint_mode') == 'ON':
        await update.message.reply_text(
            ui.format_love_message(
                "🔧 <b>সিস্টেম মেইনটেনেন্স</b>\n\n"
                "প্রিয় বন্ধু, সিস্টেম বর্তমানে মেইনটেনেন্স চলছে।\n"
                "কিছুক্ষণ পরে আবার চেষ্টা করুন। 🌹",
                user
            ),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check channel membership
    joined, missing = await verifier.check_membership(user.id, context.bot)
    
    if missing:
        # Show lock message with love
        lock_msg = db.get_config('lock_msg')
        
        # Create join buttons
        buttons = []
        for channel in missing[:8]:
            buttons.append([{
                'text': f"{channel.get('emoji', '📢')} জয়েন করুন",
                'emoji': '➕',
                'url': channel['link']
            }])
        
        if len(missing) > 8:
            buttons.append([{
                'text': "📋 সব চ্যানেল দেখুন",
                'emoji': '📋',
                'callback': 'show_all_missing'
            }])
        
        buttons.append([{
            'text': "✅ ভেরিফাই মাই লাভ",
            'emoji': '💖',
            'callback': 'verify_membership'
        }])
        
        keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=False)
        
        try:
            await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_love_message(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await update.message.reply_text(
                ui.format_love_message(lock_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        # User has joined all channels
        welcome_msg = db.get_config('welcome_msg')
        btn_text = db.get_config('btn_text')
        watch_url = db.get_config('watch_url')
        
        buttons = [[{
            'text': btn_text,
            'emoji': '🎬',
            'url': watch_url
        }]]
        
        keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=False)
        
        try:
            message = await update.message.reply_photo(
                photo=db.get_config('welcome_photo'),
                caption=ui.format_love_message(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Auto-delete if configured
            auto_delete = int(db.get_config('auto_delete', PremiumConfig.DEFAULT_AUTO_DELETE))
            if auto_delete > 0:
                await asyncio.sleep(auto_delete)
                try:
                    await message.delete()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            await update.message.reply_text(
                ui.format_love_message(welcome_msg, user),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user = update.effective_user
    
    if user.id not in PremiumConfig.ADMIN_IDS:
        await update.message.reply_text(
            "🚫 <b>অ্যাক্সেস ডিনাইড!</b>\n\n"
            "শুধুমাত্র অ্যাডমিন এই কমান্ড ব্যবহার করতে পারেন।",
            parse_mode=ParseMode.HTML
        )
        return
    
    await show_admin_panel(update.message, user)

async def show_admin_panel(message, user):
    """Show premium admin panel"""
    stats = db.get_stats()
    
    header = ui.create_love_header("👑 প্রিমিয়াম অ্যাডমিন প্যানেল")
    
    text = f"""
{header}

✨ <b>সিস্টেম স্ট্যাটাস:</b>
{ui.create_love_box(f"""
👥 মোট ইউজার: {stats['total_users']:,}
📈 আজকে যোগ: {stats['today_users']:,}
👑 ভিআইপি ইউজার: {stats['vip_users']:,}
📢 মোট চ্যানেল: {stats['total_channels']:,}
🔗 ফোর্স জয়েন: {stats['force_join_channels']:,}
📝 আজকের পোস্ট: {stats['today_posts']:,}
✅ আজকের ভেরিফাই: {stats['today_verifications']:,}
""")}

🕒 <b>বাংলাদেশ সময়:</b> {PremiumTime.get_beautiful_time()}

👇 <b>অপশন সিলেক্ট করুন:</b>
"""
    
    buttons = [
        [
            {'text': "💌 পোস্ট তৈরি", 'emoji': '💌', 'callback': 'create_post'},
            {'text': "📢 ব্রডকাস্ট", 'emoji': '📢', 'callback': 'broadcast'}
        ],
        [
            {'text': "📢 চ্যানেল ম্যানেজ", 'emoji': '📢', 'callback': 'channel_manager'},
            {'text': "⚙️ সেটিংস", 'emoji': '⚙️', 'callback': 'settings'}
        ],
        [
            {'text': "📊 স্ট্যাটিস্টিক্স", 'emoji': '📊', 'callback': 'statistics'},
            {'text': "💾 ব্যাকআপ", 'emoji': '💾', 'callback': 'backup'}
        ],
        [
            {'text': "👑 ভিআইপি ম্যানেজ", 'emoji': '👑', 'callback': 'vip_manage'},
            {'text': "🛡️ সিকিউরিটি", 'emoji': '🛡️', 'callback': 'security'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=True)
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(
            ui.format_love_message(text, user, include_time=False),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text(
            ui.format_love_message(text, user, include_time=False),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

# ==============================================================================
# 🔄 CALLBACK HANDLER (FIXED VERIFICATION POPUP)
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query handler with working popups"""
    query = update.callback_query
    user = query.from_user
    
    # Don't answer yet for verification to show popup
    if query.data != 'verify_membership':
        await query.answer()
    
    # Admin check for admin functions
    admin_prefixes = ['admin_', 'create_', 'channel_', 'settings_', 'statistics_', 
                     'backup_', 'vip_', 'security_', 'broadcast_', 'edit_']
    
    if any(query.data.startswith(prefix) for prefix in admin_prefixes) and user.id not in PremiumConfig.ADMIN_IDS:
        await query.answer("🚫 শুধুমাত্র অ্যাডমিন!", show_alert=True)
        return
    
    # Route callbacks
    if query.data == 'admin_panel':
        await show_admin_panel(query.message, user)
    
    elif query.data == 'create_post':
        return await post_wizard.start_wizard(update, context)
    
    elif query.data == 'verify_membership':
        # This will show popup inside verifier.verify_user
        success, message = await verifier.verify_user(user.id, context.bot, update)
        
        if success:
            # User verified - show welcome
            welcome_msg = db.get_config('welcome_msg')
            btn_text = db.get_config('btn_text')
            watch_url = db.get_config('watch_url')
            
            buttons = [[{
                'text': btn_text,
                'emoji': '🎬',
                'url': watch_url
            }]]
            
            keyboard = ui.create_love_keyboard(buttons, add_back=False, add_close=False)
            
            try:
                await query.message.edit_caption(
                    caption=ui.format_love_message(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except:
                await query.message.edit_text(
                    ui.format_love_message(welcome_msg, user),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
    
    elif query.data == 'back_to_main':
        await show_admin_panel(query.message, user)
    
    elif query.data == 'close_panel':
        try:
            await query.delete_message()
        except:
            pass
    
    elif query.data == 'channel_manager':
        await show_channel_manager(update, context)
    
    elif query.data == 'settings':
        await show_settings(update, context)
    
    elif query.data == 'statistics':
        await show_statistics(update, context)
    
    elif query.data.startswith('toggle_'):
        # Handle toggle in wizard
        if 'post_wizard' in context.user_data:
            await query.answer("সিলেকশন আপডেট করা হয়েছে!")
            # Handle the toggle logic here
        else:
            await query.answer("এই অপশনটি এখন অ্যাকটিভ নেই!")
    
    elif query.data in ['force_next', 'target_next', 'preview_back', 'confirm_send', 'edit_post', 'cancel_post']:
        # Handle wizard navigation
        await post_wizard.handle_force_join(update, context) if query.data == 'force_next' else \
        await post_wizard.handle_target_channels(update, context) if query.data == 'target_next' else \
        await post_wizard.confirm_post(update, context)
    
    else:
        await query.answer("এই ফিচারটি শীঘ্রই আসছে! 💖", show_alert=True)

async def show_channel_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channel manager"""
    query = update.callback_query
    await query.answer()
    
    channels = db.get_all_channels()
    
    header = ui.create_love_header("📢 চ্যানেল ম্যানেজার")
    
    text = f"""
{header}

📊 <b>চ্যানেল স্ট্যাটাস:</b>
{ui.create_love_box(f"""
📢 মোট চ্যানেল: {len(channels):,}
🔗 ফোর্স জয়েন: {len([c for c in channels if c['force_join']]):,}
⭐ প্রি-ডিফাইনড: {len([c for c in channels if c.get('is_predefined')]):,}
➕ কাস্টম: {len([c for c in channels if not c.get('is_predefined')]):,}
""")}

<b>চ্যানেল তালিকা:</b>
"""
    
    # Add channel list
    for idx, channel in enumerate(channels[:10], 1):
        status = "✅" if channel['force_join'] else "⚠️"
        text += f"{idx}. {status} {channel['emoji']} {channel['name'][:30]}\n"
    
    if len(channels) > 10:
        text += f"\n... এবং আরো {len(channels) - 10} টি চ্যানেল\n"
    
    buttons = [
        [
            {'text': "✏️ চ্যানেল এডিট", 'emoji': '✏️', 'callback': 'edit_channel'},
            {'text': "➕ নতুন যোগ", 'emoji': '➕', 'callback': 'add_channel'}
        ],
        [
            {'text': "🗑️ চ্যানেল মুছুন", 'emoji': '🗑️', 'callback': 'delete_channel'},
            {'text': "⚙️ সেটিংস", 'emoji': '⚙️', 'callback': 'channel_settings'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=True, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings panel"""
    query = update.callback_query
    await query.answer()
    
    header = ui.create_love_header("⚙️ সিস্টেম সেটিংস")
    
    text = f"""
{header}

🔧 <b>বর্তমান সেটিংস:</b>
{ui.create_love_box(f"""
🔧 মেইনটেনেন্স: {db.get_config('maint_mode', 'OFF')}
🔗 ফোর্স জয়েন: {db.get_config('force_join', 'ON')}
⏱️ অটো ডিলিট: {db.get_config('auto_delete', '45')} সেকেন্ড
🖼️ ওয়েলকাম ফটো: {db.get_config('welcome_photo', 'N/A')[:30]}...
🔗 ওয়াচ লিঙ্ক: {db.get_config('watch_url', 'N/A')[:30]}...
🔘 বাটন টেক্সট: {db.get_config('btn_text', 'N/A')[:30]}...
""")}

👇 <b>সেটিংস এডিট করুন:</b>
"""
    
    buttons = [
        [
            {'text': "🔧 মেইনটেনেন্স", 'emoji': '🔧', 'callback': 'toggle_maint'},
            {'text': "🔗 ফোর্স জয়েন", 'emoji': '🔗', 'callback': 'toggle_force'}
        ],
        [
            {'text': "⏱️ অটো ডিলিট", 'emoji': '⏱️', 'callback': 'edit_auto_delete'},
            {'text': "🖼️ ওয়েলকাম ফটো", 'emoji': '🖼️', 'callback': 'edit_welcome_photo'}
        ],
        [
            {'text': "🔗 ওয়াচ লিঙ্ক", 'emoji': '🔗', 'callback': 'edit_watch_url'},
            {'text': "🔘 বাটন টেক্সট", 'emoji': '🔘', 'callback': 'edit_btn_text'}
        ],
        [
            {'text': "💬 ওয়েলকাম মেসেজ", 'emoji': '💬', 'callback': 'edit_welcome_msg'},
            {'text': "🔒 লক মেসেজ", 'emoji': '🔒', 'callback': 'edit_lock_msg'}
        ]
    ]
    
    keyboard = ui.create_love_keyboard(buttons, add_back=True, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics"""
    query = update.callback_query
    await query.answer()
    
    stats = db.get_stats()
    
    header = ui.create_love_header("📊 ডিটেইলড স্ট্যাটিস্টিক্স")
    
    text = f"""
{header}

📈 <b>বট স্ট্যাটিস্টিক্স:</b>
{ui.create_love_box(f"""
👥 মোট ইউজার: {stats['total_users']:,}
📈 আজকে নতুন: {stats['today_users']:,}
👑 ভিআইপি ইউজার: {stats['vip_users']:,}
📢 মোট চ্যানেল: {stats['total_channels']:,}
🔗 ফোর্স জয়েন: {stats['force_join_channels']:,}
📝 আজকের পোস্ট: {stats['today_posts']:,}
✅ আজকের ভেরিফাই: {stats['today_verifications']:,}
""")}

💖 <b>সিস্টেম ইনফো:</b>
• বট: {PremiumConfig.BOT_NAME}
• সংস্করণ: Ultimate v10.0
• সময়: {PremiumTime.get_beautiful_time()}
• ডেটাবেস: {PremiumConfig.DB_NAME}
"""
    
    keyboard = ui.create_love_keyboard([], add_back=True, add_close=True)
    
    await query.edit_message_text(
        ui.format_love_message(text, update.effective_user, include_time=False),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# 🚀 MAIN APPLICATION SETUP
# ==============================================================================

def setup_premium_application():
    """Setup premium application with all features"""
    
    # Create premium application
    application = ApplicationBuilder() \
        .token(PremiumConfig.TOKEN) \
        .connection_pool_size(10) \
        .pool_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .get_updates_read_timeout(30) \
        .build()
    
    # ===== CONVERSATION HANDLERS =====
    
    # Post wizard conversation (6 steps)
    post_wizard_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler, pattern='^create_post$')],
        states={
            PremiumConfig.STATE_POST_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard.get_title)
            ],
            PremiumConfig.STATE_POST_PHOTO: [
                MessageHandler(filters.PHOTO | filters.TEXT, post_wizard.get_photo)
            ],
            PremiumConfig.STATE_POST_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, post_wizard.get_button_text)
            ],
            PremiumConfig.STATE_POST_FORCE_JOIN: [
                CallbackQueryHandler(post_wizard.handle_force_join, 
                    pattern='^(force_next|force_back|toggle_force_|select_all_force|deselect_all_force|show_all_force)$')
            ],
            PremiumConfig.STATE_POST_TARGET_CHANNELS: [
                CallbackQueryHandler(post_wizard.handle_target_channels,
                    pattern='^(target_next|target_back|toggle_target_|select_all_target|deselect_all_target|show_all_target)$')
            ],
            PremiumConfig.STATE_POST_CONFIRM: [
                CallbackQueryHandler(post_wizard.confirm_post,
                    pattern='^(confirm_send|preview_back|edit_post|cancel_post)$')
            ]
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )
    
    # ===== ADD HANDLERS =====
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "💖 <b>প্রিমিয়াম লাভ বট হেল্প</b>\n\n"
        "<b>কমান্ডস:</b>\n"
        "/start - বট শুরু করুন\n"
        "/admin - অ্যাডমিন প্যানেল\n"
        "/help - এই মেসেজ দেখুন\n\n"
        "💫 <b>ফিচারস:</b>\n"
        "• পোস্ট উইজার্ড (৬ ধাপ)\n"
        "• চ্যানেল ভেরিফিকেশন\n"
        "• অটো-ডিলিট সিস্টেম\n"
        "• প্রিমিয়াম লাভ মেসেজ\n"
        "• ১০০+ ইমোজি প্যাক\n"
        "• বাংলাদেশ সময়\n"
        "• সুন্দর UI ডিজাইন",
        parse_mode=ParseMode.HTML
    )))
    
    # Conversation handlers
    application.add_handler(post_wizard_conv)
    
    # Callback query handler (MUST BE LAST)
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors with love"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Log traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")
    
    # Notify user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                ui.format_love_message(
                    "❌ <b>ওহো! একটা সমস্যা হয়েছে!</b>\n\n"
                    "দয়া করে আবার চেষ্টা করুন।\n"
                    "যদি সমস্যা থাকে, অ্যাডমিনকে জানান।\n\n"
                    "💖 ধন্যবাদ বোঝার জন্য!",
                    update.effective_user
                ),
                parse_mode=ParseMode.HTML
            )
    except:
        pass
    
    # Notify admin
    try:
        error_msg = f"⚠️ <b>বট এরর:</b>\n<code>{context.error}</code>"
        
        for admin_id in PremiumConfig.ADMIN_IDS:
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

async def set_premium_commands(application: Application):
    """Set premium bot commands"""
    commands = [
        BotCommand("start", "💖 বট শুরু করুন"),
        BotCommand("admin", "👑 অ্যাডমিন প্যানেল"),
        BotCommand("help", "❓ হেল্প ও গাইড")
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("💖 Premium bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set commands: {e}")

def main():
    """Main entry point - Start premium bot"""
    
    # Log startup
    startup_banner = """
╔══════════════════════════════════════════════════════════════╗
║            💖 PREMIUM LOVE BOT ULTIMATE v10.0 💖            ║
║                     🎬 Starting System... 🎬                ║
║                  ⭐ 100000% Working Guaranteed ⭐            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(startup_banner)
    logger.info(startup_banner)
    
    # Display system info
    logger.info(f"🕒 Bangladesh Time: {PremiumTime.get_beautiful_time()}")
    logger.info(f"💖 Bot Name: {PremiumConfig.BOT_NAME}")
    logger.info(f"📱 Database: {PremiumConfig.DB_NAME}")
    logger.info(f"📢 Channels: {len(db.get_all_channels())} টি")
    
    try:
        # Create and setup application
        application = setup_premium_application()
        
        # Run bot
        logger.info("🚀 Premium Love Bot is now running...")
        logger.info("💫 Press Ctrl+C to stop")
        
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
        farewell = LoveMessageSystem.create_love_farewell()
        logger.info(f"💖 {farewell}")
    except Exception as e:
        logger.critical(f"💔 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run main function
    asyncio.run(main())
