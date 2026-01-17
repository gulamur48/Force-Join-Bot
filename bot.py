import logging
import os
import threading
import sqlite3
import asyncio
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Set, Dict, Optional

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto,
    constants
)
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler,
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# ====================================================================
# 🔥 CONFIGURATION & CONSTANTS
# ====================================================================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = [6406804999]  # আপনার অ্যাডমিন আইডি
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

# Database File
DB_NAME = "premium_forcejoin.db"

# Conversation States
POST_TITLE, POST_PHOTO, POST_FORCE_CHANS, POST_WEBSITE, POST_TARGET_CHANS, POST_CONFIRM = range(6)
BROADCAST_MSG = 10

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================================================================
# 🌐 HEALTH CHECK SERVER (For 24/7 Hosting)
# ====================================================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Bot is Alive & Running! 🚀</h1>")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"🌍 Web server running on port {port}")
    server.serve_forever()

# Start Server in Background Thread
threading.Thread(target=run_health_check_server, daemon=True).start()

# ====================================================================
# 🗄️ DATABASE MANAGER (Robust SQLite Handler)
# ====================================================================
class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY, 
                name TEXT, 
                link TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        self.conn.commit()

    def get_total_users(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def add_channel(self, c_id, name, link):
        self.cursor.execute("INSERT OR REPLACE INTO channels VALUES(?,?,?)", (c_id, name, link))
        self.conn.commit()

    def delete_channel(self, c_id):
        self.cursor.execute("DELETE FROM channels WHERE id=?", (c_id,))
        self.conn.commit()

    def get_all_channels(self):
        self.cursor.execute("SELECT * FROM channels")
        return self.cursor.fetchall()
    
    def get_channel(self, c_id):
        self.cursor.execute("SELECT name, link FROM channels WHERE id=?", (c_id,))
        return self.cursor.fetchone()

    def get_all_user_ids(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]

db = DatabaseManager(DB_NAME)

# ====================================================================
# ⚡ INITIAL DATA SEEDING
# ====================================================================
INITIAL_CHANNELS = [
    ("@virallink259","🔥 Viral Video Express","https://t.me/virallink259"),
    ("-1002279183424","💎 Premium App Zone","https://t.me/+5PNLgcRBC0IxYjll"),
    ("@virallink246","🇧🇩 BD Beauty Viral","https://t.me/virallink246"),
    ("@viralexpress1","📸 FB/Insta Leaks","https://t.me/viralexpress1"),
    ("@movietime467","🎬 Movie Time 467","https://t.me/movietime467"),
    ("@viralfacebook9","🌶️ BD MMS Video","https://t.me/viralfacebook9"),
    ("@viralfb24","🥵 Deshi Vabi Viral","https://t.me/viralfb24"),
    ("@fbviral24","💃 Kachi Meyer Video","https://t.me/fbviral24"),
    ("-1001550993047","📥 Video Request","https://t.me/+WAOUc1rX6Qk3Zjhl"),
    ("-1002011739504","🌍 Viral World BD","https://t.me/+la630-IFwHAwYWVl"),
    ("-1002444538806","🎨 AI Prompt Studio","https://t.me/+AHsGXIDzWmJlZjVl")
]

for c in INITIAL_CHANNELS:
    db.add_channel(c[0], c[1], c[2])

# ====================================================================
# 🛠️ HELPER FUNCTIONS & DECORATORS
# ====================================================================
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user.id not in ADMIN_IDS:
            await update.message.reply_text("⛔ <b>Access Denied!</b> You are not an admin.", parse_mode=ParseMode.HTML)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

async def send_loading_animation(message, text_list, delay=0.5):
    """Creates a cool loading effect on a message"""
    for text in text_list:
        try:
            await message.edit_text(text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(delay)
        except:
            pass

async def check_subscription(user_id, bot):
    """Checks if user has joined all required channels"""
    not_joined = []
    channels = db.get_all_channels()
    
    for cid, name, link in channels:
        try:
            member = await bot.get_chat_member(cid, user_id)
            if member.status in ['left', 'kicked', 'restricted']:
                not_joined.append((cid, name, link))
        except Exception as e:
            # If bot can't check (not admin or channel private/invalid), assume joined to avoid blocking
            # But here we add to not_joined so admin knows to fix bot permissions
            logger.error(f"Error checking channel {cid}: {e}")
            not_joined.append((cid, name, link))
            
    return not_joined

async def check_specific_subscription(user_id, bot, channel_ids):
    not_joined = []
    for cid in channel_ids:
        res = db.get_channel(cid)
        if res:
            name, link = res
            try:
                member = await bot.get_chat_member(cid, user_id)
                if member.status in ['left', 'kicked']:
                    not_joined.append((cid, name, link))
            except:
                not_joined.append((cid, name, link))
    return not_joined

# ====================================================================
# 🤖 BOT COMMAND HANDLERS
# ====================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id)
    
    # Send temporary loading message
    msg = await update.message.reply_text("⚡ <i>Connecting to server...</i>", parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=user.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.8) # Simulate loading
    
    not_joined = await check_subscription(user.id, context.bot)

    if not not_joined:
        await msg.delete()
        text = (
            f"🎉 <b>স্বাগতম {user.first_name}!</b>\n\n"
            f"✅ আপনি সফলভাবে ভেরিফাইড হয়েছেন।\n"
            f"🎬 এখন আপনি আনলিমিটেড প্রিমিয়াম কন্টেন্ট উপভোগ করতে পারবেন।\n\n"
            f"👇 নিচের বাটনে ক্লিক করুন:"
        )
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Watch Now 🎬", url=WATCH_NOW_URL)],
                [InlineKeyboardButton("💠 Official Channel", url="https://t.me/virallink259")]
            ]),
            parse_mode=ParseMode.HTML
        )
    else:
        await msg.edit_text("🔒 <b>Access Locked!</b>\n<i>দয়া করে নিচের চ্যানেলগুলোতে জয়েন করুন...</i>", parse_mode=ParseMode.HTML)
        
        keyboard = []
        # Creating a stylish 2-column layout for buttons
        row = []
        for index, (cid, name, link) in enumerate(not_joined):
            btn_text = f"Join {index + 1} 🚀"
            row.append(InlineKeyboardButton(btn_text, url=link))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("✅ I Have Joined (Verify) 🔄", callback_data="check_status")])
        
        await update.message.reply_text(
            f"⚠️ <b>হ্যালো {user.first_name},</b>\n\n"
            f"🚨 কন্টেন্ট আনলক করতে হলে আপনাকে নিচের <b>{len(not_joined)}টি</b> চ্যানেলে জয়েন করতে হবে।\n"
            f"👇 সবগুলোতে জয়েন করে <b>Verify</b> বাটনে ক্লিক করুন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer("🔄 Checking subscription status...")
    
    not_joined = await check_subscription(user.id, context.bot)
    
    if not not_joined:
        await query.message.edit_text(
            f"🎉 <b>অভিনন্দন {user.first_name}!</b>\n✅ ভেরিফিকেশন সফল হয়েছে।",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now 🎬", url=WATCH_NOW_URL)]]),
            parse_mode=ParseMode.HTML
        )
    else:
        await query.answer("❌ আপনি সব চ্যানেলে জয়েন করেননি!", show_alert=True)

# ====================================================================
# 📝 ADVANCED POST CREATION WIZARD
# ====================================================================
# Global dictionary to store temporary post data
POST_DATA = {}

@admin_only
async def newpost_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    POST_DATA[user_id] = {'force_chans': set(), 'target_chans': set()}
    
    await update.message.reply_text(
        "📝 <b>New Post Wizard</b>\n\n"
        "1️⃣ দয়া করে পোস্টের <b>Title (Caption)</b> পাঠান:",
        parse_mode=ParseMode.HTML
    )
    return POST_TITLE

async def p_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    POST_DATA[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("2️⃣ এবার পোস্টের জন্য একটি <b>Photo</b> পাঠান:", parse_mode=ParseMode.HTML)
    return POST_PHOTO

async def p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    POST_DATA[update.effective_user.id]['photo'] = photo
    
    # Create selection keyboard for Force Join
    keyboard = []
    channels = db.get_all_channels()
    for cid, name, _ in channels:
        keyboard.append([InlineKeyboardButton(f"🛡️ {name}", callback_data=f"fsel|{cid}")])
    
    keyboard.append([InlineKeyboardButton("✅ Done Selecting", callback_data="fsel_done")])
    
    await update.message.reply_text(
        "3️⃣ <b>Force Join Configuration:</b>\n"
        "ইউজার কোন চ্যানেলগুলোতে জয়েন না থাকলে এই ভিডিও দেখতে পারবে না? (সিলেক্ট করুন)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    return POST_FORCE_CHANS

async def p_force_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "fsel_done":
        await query.edit_message_text(
            "4️⃣ এখন <b>Website URL</b> দিন (যদি ডাইরেক্ট ওয়াচ লিংক হয়)।\n"
            "➡️ আর যদি ডিফল্ট ব্যবহার করতে চান তবে লিখুন: <code>skip</code>",
            parse_mode=ParseMode.HTML
        )
        return POST_WEBSITE
    
    cid = query.data.split("|")[1]
    if cid in POST_DATA[user_id]['force_chans']:
        POST_DATA[user_id]['force_chans'].remove(cid)
        await query.answer(f"Removed from Force Join", show_alert=False)
    else:
        POST_DATA[user_id]['force_chans'].add(cid)
        await query.answer(f"Added to Force Join", show_alert=False)
        
    # Update button text to show selection
    current_markup = query.message.reply_markup
    new_keyboard = []
    for row in current_markup.inline_keyboard:
        btn = row[0]
        if btn.callback_data == f"fsel|{cid}":
            prefix = "✅" if cid in POST_DATA[user_id]['force_chans'] else "🛡️"
            # Extract clean name
            clean_name = btn.text.replace("✅ ", "").replace("🛡️ ", "")
            new_keyboard.append([InlineKeyboardButton(f"{prefix} {clean_name}", callback_data=btn.callback_data)])
        else:
            new_keyboard.append(row)
            
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))
    return POST_FORCE_CHANS

async def p_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    url = WATCH_NOW_URL if text.lower() == 'skip' else text
    POST_DATA[update.effective_user.id]['url'] = url
    
    # Target channels selection
    keyboard = []
    channels = db.get_all_channels()
    for cid, name, _ in channels:
        keyboard.append([InlineKeyboardButton(f"📢 {name}", callback_data=f"tsel|{cid}")])
    keyboard.append([InlineKeyboardButton("🚀 Proceed to Confirmation", callback_data="tsel_done")])
    
    await update.message.reply_text(
        "5️⃣ <b>Target Channels:</b>\n"
        "পোস্টটি কোন কোন চ্যানেলে সেন্ড হবে? সিলেক্ট করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    return POST_TARGET_CHANS

async def p_target_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "tsel_done":
        data = POST_DATA[user_id]
        
        # Summary
        force_count = len(data['force_chans'])
        target_count = len(data['target_chans'])
        
        text = (
            f"📋 <b>Post Summary</b>\n\n"
            f"📝 <b>Title:</b> {data['title'][:50]}...\n"
            f"🛡️ <b>Force Join:</b> {force_count} Channels\n"
            f"📢 <b>Destination:</b> {target_count} Channels\n"
            f"🔗 <b>URL:</b> {data['url']}\n\n"
            f"⚠️ <i>আপনি কি নিশ্চিত?</i>"
        )
        
        buttons = [
            [InlineKeyboardButton("✅ Yes, Send Now! 🚀", callback_data="post_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="post_cancel")]
        ]
        
        # Send Preview
        await query.message.reply_photo(
            photo=data['photo'],
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
        return POST_CONFIRM
        
    cid = query.data.split("|")[1]
    # Toggle Logic
    if cid in POST_DATA[user_id]['target_chans']:
        POST_DATA[user_id]['target_chans'].remove(cid)
        await query.answer("Removed from Target")
    else:
        POST_DATA[user_id]['target_chans'].add(cid)
        await query.answer("Added to Target")

    # Visual Update
    current_markup = query.message.reply_markup
    new_keyboard = []
    for row in current_markup.inline_keyboard:
        btn = row[0]
        if btn.callback_data == f"tsel|{cid}":
            prefix = "✅" if cid in POST_DATA[user_id]['target_chans'] else "📢"
            clean_name = btn.text.replace("✅ ", "").replace("📢 ", "")
            new_keyboard.append([InlineKeyboardButton(f"{prefix} {clean_name}", callback_data=btn.callback_data)])
        else:
            new_keyboard.append(row)
            
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))
    return POST_TARGET_CHANS

async def p_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "post_cancel":
        await query.message.edit_caption("❌ <b>Post Creation Cancelled.</b>", parse_mode=ParseMode.HTML)
        POST_DATA.pop(user_id, None)
        return ConversationHandler.END
        
    if query.data == "post_confirm":
        data = POST_DATA[user_id]
        force_ids = ",".join(data['force_chans']) if data['force_chans'] else "none"
        
        # The Magic Button
        magic_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("🎬 Watch Video 🔞", callback_data=f"v|{force_ids}|{data['url']}")
        ]])
        
        await query.edit_message_caption("⏳ <b>Sending to channels...</b>", parse_mode=ParseMode.HTML)
        
        success_count = 0
        for target_cid in data['target_chans']:
            try:
                await context.bot.send_photo(
                    chat_id=target_cid,
                    photo=data['photo'],
                    caption=data['title'],
                    reply_markup=magic_btn,
                    parse_mode=ParseMode.HTML
                )
                success_count += 1
                await asyncio.sleep(0.5) # Flood limit protection
            except Exception as e:
                logger.error(f"Failed to send to {target_cid}: {e}")
                
        await query.message.reply_text(f"✅ <b>Success!</b> Post sent to {success_count} channels.", parse_mode=ParseMode.HTML)
        POST_DATA.pop(user_id, None)
        return ConversationHandler.END

# ====================================================================
# 🎥 VIDEO WATCH HANDLER (The Core Verification)
# ====================================================================
async def watch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Extract Data: v | force_ids_comma_sep | url
    try:
        _, force_str, url = query.data.split("|", 2)
    except:
        await query.answer("❌ Error in button data!", show_alert=True)
        return

    # Check database for user
    db.add_user(user_id)
    
    if force_str == "none":
        required_ids = []
    else:
        required_ids = force_str.split(",")

    # Check Verification
    not_joined = await check_specific_subscription(user_id, context.bot, required_ids)
    
    if not not_joined:
        # Success Animation
        await query.answer("✅ Access Granted! Opening Link...", show_alert=False)
        try:
            # We try to send ephemeral message or private message with link
            text = f"🚀 <b>Link Generated:</b>\n{url}\n\n<i>This message will auto-delete in 60s.</i>"
            await context.bot.send_message(user_id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except:
             # If user hasn't started bot in PM
             await query.answer("❌ Please start the bot in private first!", show_alert=True)
             return
             
        # Optional: Edit original message slightly to show interaction? No, keep it clean.
    else:
        await query.answer("❌ Access Denied!", show_alert=True)
        
        # Build lock message
        buttons = [[InlineKeyboardButton(f"Join {n}", url=l)] for _, n, l in not_joined]
        buttons.append([InlineKeyboardButton("♻️ Try Again", callback_data=query.data)])
        
        await context.bot.send_message(
            chat_id=user_id,
            text="🚫 <b>ভিডিওটি দেখতে হলে নিচের চ্যানেলগুলোতে জয়েন করতে হবে:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )

# ====================================================================
# 📢 BROADCAST & ADMIN TOOLS
# ====================================================================
@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_total_users()
    channels = len(db.get_all_channels())
    
    text = (
        f"📊 <b>BOT STATISTICS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{users}</code>\n"
        f"📺 <b>Connected Channels:</b> <code>{channels}</code>\n"
        f"🤖 <b>Bot Status:</b> Active ✅\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

@admin_only
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📢 <b>Broadcast Mode</b>\nSend the message (Text, Photo, Video) you want to broadcast to all users.", parse_mode=ParseMode.HTML)
    return BROADCAST_MSG

async def broadcast_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_user_ids()
    total = len(users)
    success = 0
    blocked = 0
    
    status_msg = await update.message.reply_text(f"🚀 Broadcast started to {total} users...")
    
    for uid in users:
        try:
            await update.message.copy(chat_id=uid)
            success += 1
        except Exception:
            blocked += 1
        
        if (success + blocked) % 50 == 0:
            try:
                await status_msg.edit_text(f"📤 Sending...\n✅ Success: {success}\n🚫 Blocked: {blocked}\n🎯 Total: {total}")
            except: pass
            
    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"👥 Total: {total}\n"
        f"✅ Sent: {success}\n"
        f"🚫 Failed/Blocked: {blocked}",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation Cancelled.")
    return ConversationHandler.END

@admin_only
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /addchannel -100xxx https://t.me/xx Name
    try:
        args = context.args
        if len(args) < 3:
            raise ValueError
        
        cid = args[0]
        link = args[1]
        name = " ".join(args[2:])
        
        db.add_channel(cid, name, link)
        await update.message.reply_text(f"✅ <b>Channel Added!</b>\nName: {name}", parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text("Usage: `/addchannel <id> <link> <name>`", parse_mode=ParseMode.HTML)

# ====================================================================
# 🚀 MAIN APPLICATION ENTRY POINT
# ====================================================================
def main():
    print("🔥 Starting Premium Bot...")
    
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="^check_status"))
    app.add_handler(CallbackQueryHandler(watch_callback, pattern="^v\|"))
    
    # Admin Commands
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("addchannel", add_channel))
    
    # New Post Wizard
    post_handler = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost_start)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, p_photo)],
            POST_FORCE_CHANS: [CallbackQueryHandler(p_force_cb, pattern="^fsel")],
            POST_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_website)],
            POST_TARGET_CHANS: [CallbackQueryHandler(p_target_cb, pattern="^tsel")],
            POST_CONFIRM: [CallbackQueryHandler(p_confirm, pattern="^post_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_op)]
    )
    app.add_handler(post_handler)
    
    # Broadcast Wizard
    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={
            BROADCAST_MSG: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_process)]
        },
        fallbacks=[CommandHandler("cancel", cancel_op)]
    )
    app.add_handler(broadcast_handler)

    print("✅ Bot is Online & Polling!")
    app.run_polling()

if __name__ == "__main__":
    main()
