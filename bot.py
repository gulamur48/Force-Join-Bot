import os
import sys
import time
import sqlite3
import asyncio
import logging
import threading
import psutil
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import mention_html
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, 
    filters, ApplicationBuilder
)

# ================= 💖 CONFIGURATION =================
# আপনার বট টোকেন এবং অ্যাডমিন আইডি
TOKEN = "8510787985:AAEw4UNXdCZLK_r25EKJnuIwrlkE8cyk7VE"
ADMIN_IDS = {6406804999} 

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
START_TIME = time.time()

# Conversation States
INPUT_TEXT = 1
POST_CAP, POST_MEDIA, POST_FJ, POST_TG, POST_CONFIRM = range(2, 7)
BROADCAST_MSG = 8

# ================= 🗄️ SUPREME DATABASE (AUTO SETUP) =================
class SupremeDB:
    def __init__(self):
        self.conn = sqlite3.connect("supreme_love_final.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # টেবিল তৈরি
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, join_date TEXT, status TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        
        # 💖 রোমান্টিক এবং ফিচার সেটিংস (৫০টি ফিচার কনফিগ)
        defaults = {
            "watch_url": "https://mmshotbd.blogspot.com/?m=1",
            "welcome_photo": "https://cdn.pixabay.com/photo/2016/02/13/12/26/aurora-1197753_1280.jpg",
            "auto_delete": "45",
            "maint_mode": "OFF",
            "force_join": "ON",
            "anti_spam": "ON",
            
            # বিশাল রোমান্টিক ওয়েলকাম মেসেজ
            "welcome_msg": """💖✨ <b>ওগো শুনছো! স্বাগতম জানাই তোমাকে!</b> ✨💖

🌹 <b>প্রিয়তম/প্রিয়তমা,</b>
তুমি অবশেষে আমাদের মাঝে এসেছো, আমার হৃদয়টা খুশিতে নেচে উঠলো! 😍💃
তোমাকে ছাড়া আমাদের এই আয়োজন একদমই অসম্পূর্ণ ছিল। 💏

✨ <b>তোমার জন্য স্পেশাল যা যা থাকছে:</b>
🎀 এক্সক্লুসিভ ভাইরাল ভিডিও 🔞
🎀 নতুন সব হট কালেকশন 🔥
🎀 এবং আমার হৃদয়ের গভীর ভালোবাসা... ❤️

👇 <b>দেরি না করে নিচের বাটনে আলতো করে ক্লিক করো সোনা:</b> 👇""",
            
            # বিশাল রোমান্টিক লক মেসেজ (কান্নার ইমোজি সহ)
            "lock_msg": """💔 <b>ওহ নো বেবি! তুমি এখনো জয়েন করোনি?</b> 😢💔

আমার লক্ষ্মীটা, তুমি যদি নিচের চ্যানেলগুলোতে জয়েন না করো, তাহলে আমি তোমাকে ভিডিওটা দেখাতে পারবো না! 🥺🥀
আমার খুব কষ্ট লাগবে যদি তুমি চলে যাও... 😭

🌹 <b>প্লিজ সোনা, রাগ করো না!</b>
নিচের সবগুলোতে জয়েন করে <b>"Verify Me Love"</b> বাটনে ক্লিক করো। আমি তোমার অপেক্ষায় আছি... 😘💕""",
            
            "btn_text": "🎬 ভিডিও দেখুন (Watch Now) ✨😍"
        }
        for k, v in defaults.items():
            self.cursor.execute("INSERT OR IGNORE INTO config VALUES (?, ?)", (k, v))
        self.conn.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        res = self.cursor.fetchone()
        return res[0] if res else "Not Set"

    def set(self, key, val):
        self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (key, str(val)))
        self.conn.commit()

    def add_user(self, user):
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", 
                            (user.id, user.first_name, datetime.datetime.now().strftime("%Y-%m-%d"), "active"))
        self.conn.commit()

    def get_stats(self):
        try:
            total = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            today = self.cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (datetime.datetime.now().strftime("%Y-%m-%d"),)).fetchone()[0]
            return total, today
        except: return 0, 0

    def get_users(self):
        return [r[0] for r in self.cursor.execute("SELECT id FROM users").fetchall()]

db = SupremeDB()

# ================= 🔗 MASTER CHANNELS (Force Join List) =================
# নোট: বটকে অবশ্যই এই চ্যানেলগুলোতে অ্যাডমিন বানাতে হবে!
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

# ================= 🌐 RENDER HEALTH SERVER =================
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Supreme Love Bot Alive")

def run_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        HTTPServer(("0.0.0.0", port), HealthServer).serve_forever()
    except: pass

threading.Thread(target=run_server, daemon=True).start()

# ================= 🎨 DECORATION ENGINE =================
def decor(text, user):
    name = mention_html(user.id, user.first_name)
    header = "🌺🍃 <b>SUPREME LOVE ZONE</b> 🍃🌺\n━━━━━━━━━━━━━━━━━━━━━━\n"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━\n💖 <b>With Love:</b> {name}\n⏰ <b>Time:</b> {datetime.datetime.now().strftime('%I:%M %p')}"
    return header + text + footer

# ================= 🛡️ FORCE JOIN LOGIC (FIXED) =================
async def check_join_status(user_id, context):
    if db.get("force_join") == "OFF": return []
    missing = []
    
    for ch in MASTER_CHANNELS:
        try:
            # চেক করছে ইউজার মেম্বার কিনা
            m = await context.bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if m.status in ['left', 'kicked', 'restricted']:
                missing.append(ch)
        except Exception as e:
            # যদি বট অ্যাডমিন না হয়, তবুও আমরা ইউজারকে জয়েন করতে বলবো (সেফটি)
            # logger.error(f"Channel Check Error: {ch['id']} - {e}")
            missing.append(ch)
            
    return missing

# ================= 👤 USER HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user)
    
    # মেইনটেনেন্স মোড চেক
    if db.get("maint_mode") == "ON" and user.id not in ADMIN_IDS:
        await update.message.reply_html(decor("🚧 <b>দুঃখিত জানু!</b>\n\nএখন একটু সিস্টেম আপগ্রেডের কাজ চলছে, প্লিজ পরে আসো! 🥺", user))
        return

    missing = await check_join_status(user.id, context)
    photo_url = db.get("welcome_photo")
    
    if not missing:
        # সব জয়েন করা থাকলে
        txt = db.get("welcome_msg")
        kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
    else:
        # জয়েন করা বাকি থাকলে
        txt = db.get("lock_msg")
        kb = [[InlineKeyboardButton(f"💞 জয়েন: {c['name']}", url=c['link'])] for c in missing]
        kb.append([InlineKeyboardButton("✨ Verify Me Love ✨", callback_data="check_join")])

    # 🔥 Crash Proof Sender (ছবি নষ্ট থাকলেও টেক্সট যাবে)
    try:
        await update.message.reply_photo(photo=photo_url, caption=decor(txt, user), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Photo Error: {e}")
        await update.message.reply_html(decor(txt, user), reply_markup=InlineKeyboardMarkup(kb))

# ================= 👑 ULTIMATE ADMIN PANEL (NO COMMAND NEEDED) =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    
    total, today = db.get_stats()
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
    
    txt = (f"👑 <b>SUPREME GOD ADMIN PANEL</b> 👑\n\n"
           f"📊 <b>পরিসংখ্যান:</b>\n"
           f"🌹 টোটাল ইউজার: <code>{total}</code>\n"
           f"📅 আজকের নতুন: <code>{today}</code>\n"
           f"⚡ আপটাইম: {uptime}\n"
           f"💾 স্ট্যাটাস: Active ✅\n\n"
           f"👇 <b>কোন সেকশন কন্ট্রোল করতে চান?</b>")
    
    btns = [
        [InlineKeyboardButton("📝 লাভ মেসেজ এডিটর", callback_data="menu_msg"), InlineKeyboardButton("🔗 লিঙ্ক সেটিংস", callback_data="menu_links")],
        [InlineKeyboardButton("🛡️ সিকিউরিটি গার্ড", callback_data="menu_security"), InlineKeyboardButton("📢 পোস্ট & ব্রডকাস্ট", callback_data="menu_post")],
        [InlineKeyboardButton("❌ প্যানেল বন্ধ করুন", callback_data="close_admin")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_caption(caption=decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_html(decor(txt, update.effective_user), reply_markup=InlineKeyboardMarkup(btns))

# ================= ⚙️ SUB-MENUS & LOGIC =================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user

    # 1. Message Editor Menu
    if data == "menu_msg":
        btns = [
            [InlineKeyboardButton("✍️ ওয়েলকাম মেসেজ চেঞ্জ", callback_data="edit_welcome_msg")],
            [InlineKeyboardButton("✍️ লক মেসেজ (Join Request) চেঞ্জ", callback_data="edit_lock_msg")],
            [InlineKeyboardButton("🖼️ ওয়েলকাম ফটো চেঞ্জ", callback_data="edit_welcome_photo")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📝 <b>মেসেজ কাস্টমাইজেশন</b>\nএখানে সব টেক্সট এবং ফটো কন্ট্রোল করুন।", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    # 2. Link Settings Menu
    elif data == "menu_links":
        curr_url = db.get("watch_url")
        btns = [
            [InlineKeyboardButton("🔗 ওয়াচ ভিডিও লিঙ্ক চেঞ্জ", callback_data="edit_watch_url")],
            [InlineKeyboardButton("🔘 বাটন টেক্সট চেঞ্জ", callback_data="edit_btn_text")],
            [InlineKeyboardButton("⏱️ অটো ডিলিট টাইমার", callback_data="edit_auto_delete")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor(f"🔗 <b>লিঙ্ক ম্যানেজার</b>\nবর্তমান লিঙ্ক: {curr_url}", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    # 3. Security Menu
    elif data == "menu_security":
        maint = "✅ ON" if db.get("maint_mode") == "ON" else "❌ OFF"
        force = "✅ ON" if db.get("force_join") == "ON" else "❌ OFF"
        btns = [
            [InlineKeyboardButton(f"🚧 মেইনটেনেন্স মোড: {maint}", callback_data="tog_maint_mode")],
            [InlineKeyboardButton(f"🔐 ফোর্স জয়েন সিস্টেম: {force}", callback_data="tog_force_join")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("🛡️ <b>সিকিউরিটি কন্ট্রোল</b>\nএক ক্লিকে অন/অফ করুন।", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    # 4. Post & Broadcast Menu
    elif data == "menu_post":
        btns = [
            [InlineKeyboardButton("✨ নতুন পোস্ট তৈরি করুন (Wizard)", callback_data="wiz_start")],
            [InlineKeyboardButton("📡 গ্লোবাল ব্রডকাস্ট", callback_data="broadcast_init")],
            [InlineKeyboardButton("🔙 ব্যাক", callback_data="main_menu")]
        ]
        await query.edit_message_caption(decor("📢 <b>মার্কেটিং টুলস</b>\nপোস্ট বা ব্রডকাস্ট করুন।", user), reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

    # Toggle Logic
    elif data.startswith("tog_"):
        key = data.replace("tog_", "")
        new_val = "OFF" if db.get(key) == "ON" else "ON"
        db.set(key, new_val)
        # Refresh current menu
        query.data = "menu_security"
        await handle_callback(update, context)

    # Verification Logic
    elif data == "check_join":
        missing = await check_join_status(user.id, context)
        if not missing:
            await query.answer("💖 ভেরিফিকেশন সফল জানু!", show_alert=True)
            try: await query.message.delete()
            except: pass
            
            kb = [[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]]
            await query.message.reply_photo(
                photo=db.get("welcome_photo"),
                caption=decor(db.get("welcome_msg"), user),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.answer("💔 এখনো সবগুলোতে জয়েন করোনি!", show_alert=True)

    # Editors
    elif data.startswith("edit_"):
        context.user_data['edit_key'] = data.replace("edit_", "")
        await query.message.reply_html(decor("✍️ <b>নতুন ভ্যালু লিখে পাঠাও:</b>\n(যেকোন টেক্সট, ইমোজি বা লিঙ্ক দিতে পারো)", user))
        return INPUT_TEXT
    
    elif data == "main_menu":
        await admin_panel(update, context)
        
    elif data == "close_admin":
        await query.message.delete()

# ================= 📝 EDITOR HANDLER =================
async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('edit_key')
    val = update.message.text
    if key:
        db.set(key, val)
        await update.message.reply_html(decor(f"✅ <b>সেভ হয়েছে জানু!</b>\n\nKey: {key}\nValue: {val}", update.effective_user))
    return ConversationHandler.END

# ================= 📢 POST WIZARD =================
async def wiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_html(decor("📝 <b>স্টেপ ১: ক্যাপশন</b>\nপোস্টের ক্যাপশন লিখে পাঠাও।", update.effective_user))
    context.user_data['post'] = {'fj': [], 'tg': []}
    return POST_CAP

async def wiz_cap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['cap'] = update.message.text
    await update.message.reply_html(decor("📸 <b>স্টেপ ২: মিডিয়া</b>\nফটো/ভিডিও দাও (অথবা /skip লেখো)।", update.effective_user))
    return POST_MEDIA

async def wiz_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['med'] = update.message.photo[-1].file_id
    elif update.message.video: context.user_data['post']['med'] = update.message.video.file_id
    else: context.user_data['post']['med'] = None
    
    # Target Selection
    btns = [[InlineKeyboardButton(c['name'], callback_data=f"send_{c['id']}")] for c in MASTER_CHANNELS]
    await update.message.reply_html(decor("🚀 <b>কোথায় পাঠাবে?</b>\nচ্যানেল সিলেক্ট করো:", update.effective_user), reply_markup=InlineKeyboardMarkup(btns))
    return POST_CONFIRM

async def wiz_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("send_", "")
    p = context.user_data['post']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(db.get("btn_text"), url=db.get("watch_url"))]])
    
    try:
        if p['med']: await context.bot.send_photo(cid, p['med'], caption=p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        else: await context.bot.send_message(cid, p['cap'], reply_markup=kb, parse_mode=ParseMode.HTML)
        await update.callback_query.message.reply_text("✅ পোস্ট সফল হয়েছে!")
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ এরর: {e} (বট কি ওই চ্যানেলে অ্যাডমিন?)")
    return ConversationHandler.END

# ================= 📡 BROADCAST =================
async def broadcast_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_html(decor("📢 <b>ব্রডকাস্ট</b>\nমেসেজ ফরোয়ার্ড করুন বা লিখুন:", update.effective_user))
    return BROADCAST_MSG

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_users()
    msg = update.message
    status = await update.message.reply_text("⏳ ব্রডকাস্ট শুরু হচ্ছে...")
    s, f = 0, 0
    
    for uid in users:
        try:
            await msg.copy(uid)
            s += 1
        except: f += 1
        if s % 50 == 0: await status.edit_text(f"📤 পাঠাচ্ছে... {s}/{len(users)}")
        
    await status.edit_text(decor(f"✅ <b>ব্রডকাস্ট রিপোর্ট</b>\n\nসফল: {s}\nব্যর্থ: {f}", update.effective_user), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ অপারেশন বাতিল।")
    return ConversationHandler.END

# ================= 🚀 MAIN FUNCTION =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Conversation Handlers
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern="^edit_")],
        states={INPUT_TEXT: [MessageHandler(filters.TEXT, save_input)]},
        fallbacks=[CommandHandler("cancel", admin_panel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(wiz_start, pattern="^wiz_start$")],
        states={
            POST_CAP: [MessageHandler(filters.TEXT, wiz_cap)],
            POST_MEDIA: [MessageHandler(filters.ALL, wiz_media)],
            POST_CONFIRM: [CallbackQueryHandler(wiz_send, pattern="^send_")]
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="cancel")]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_init, pattern="^broadcast_init$")],
        states={BROADCAST_MSG: [MessageHandler(filters.ALL, broadcast_send)]},
        fallbacks=[CommandHandler("cancel", admin_panel)]
    ))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("💖 SUPREME LOVE BOT STARTED 💖")
    app.run_polling()

if __name__ == "__main__":
    main()
