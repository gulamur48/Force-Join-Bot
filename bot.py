import logging
import os
import threading
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)

# ================= HEALTH CHECK =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================= CONFIG =================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
ADMIN_IDS = {6406804999}
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= DATABASE =================
DB = sqlite3.connect("bot.db", check_same_thread=False)
CURSOR = DB.cursor()

CURSOR.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)""")
CURSOR.execute("""CREATE TABLE IF NOT EXISTS channels (username TEXT PRIMARY KEY, button TEXT, link TEXT)""")
CURSOR.execute("""CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    photo_file_id TEXT,
    force_join_channels TEXT,
    target_channels TEXT,
    url TEXT
)""")
DB.commit()

# ================= CHANNELS =================
CHANNELS_DATA = [
    {"id": "@virallink259", "name": "ভাইরাল ভিদিও লিংক এক্সপ্রেস ২০২৬🔥❤️", "link": "https://t.me/virallink259"},
    {"id": -1002279183424, "name": "Primium App Zone", "link": "https://t.me/+5PNLgcRBC0IxYjll"},
    {"id": "@virallink246", "name": "Bd beauty viral", "link": "https://t.me/virallink246"},
    {"id": "@viralexpress1", "name": "Facebook🔥 Instagram Link🔥", "link": "https://t.me/viralexpress1"},
    {"id": "@movietime467", "name": "🎬MOVIE🔥 TIME💥", "link": "https://t.me/movietime467"},
    {"id": "@viralfacebook9", "name": "BD MMS VIDEO🔥🔥", "link": "https://t.me/viralfacebook9"},
    {"id": "@viralfb24", "name": "দেশি ভাবি ভাইরাল🔥🥵", "link": "https://t.me/viralfb24"},
    {"id": "@fbviral24", "name": "কচি মেয়েদের ভাইরাল ভিদিও🔥", "link": "https://t.me/fbviral24"},
    {"id": -1001550993047, "name": "ভাইরাল ভিদিও রিকুয়েষ্ট🥵", "link": "https://t.me/+WAOUc1rX6Qk3Zjhl"},
    {"id": -1002011739504, "name": "Viral Video BD 🌍🔥", "link": "https://t.me/+la630-IFwHAwYWVl"},
    {"id": -1002444538806, "name": "Ai Prompt Studio 🎨📸", "link": "https://t.me/+AHsGXIDzWmJlZjVl"}
]

# ================= UTILS =================
def is_admin(user_id):
    return user_id in ADMIN_IDS

async def save_user(user_id):
    CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    DB.commit()

async def check_all_joined(user_id, context):
    not_joined = []
    for channel in CHANNELS_DATA:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return not_joined

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)
    stylish_name = f"👤 <b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)

    if not not_joined_list:
        success_text = (
            f"🎉 স্বাগতম {stylish_name}\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
            f"▶️ ভিডিও দেখতে এখনই <b>[Watch Now]</b> বাটনে ক্লিক করুন 🎬✨"
        )
        watch_kb = InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)
        await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup([[watch_kb]]), parse_mode=ParseMode.HTML)
    else:
        buttons = [[InlineKeyboardButton(f"Join {c['name']}", url=c['link'])] for c in not_joined_list]
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        caption = (
            f"Hello {stylish_name},\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
            "সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
            "Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

# ================= BUTTON CALLBACK =================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stylish_name = f"<b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)

    if query.data == "check_status":
        if not not_joined_list:
            await query.answer(f"ধন্যবাদ {user.first_name}! সব চেক করা হয়েছে।", show_alert=True)
            success_text = (
                f"🎉 স্বাগতম {stylish_name}\n"
                f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
                f"▶️ ভিডিও দেখতে এখনই <b>[Watch Now]</b> বাটনে ক্লিক করুন 🎬✨"
            )
            watch_kb = InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)
            await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup([[watch_kb]]), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি! সব লিঙ্কে ক্লিক করে জয়েন করুন।", show_alert=True)

# ================= CHECK =================
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    not_joined_list = await check_all_joined(update.effective_user.id, context)
    if not not_joined_list:
        watch_kb = InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)
        await update.message.reply_text("✅ সব চ্যানেল join করা আছে!", reply_markup=InlineKeyboardMarkup([[watch_kb]]))
    else:
        await update.message.reply_text("❌ এখনো সব চ্যানেলে join করা হয়নি!")

# ================= CHANNEL MANAGEMENT =================
async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        username = context.args[0]
        link = context.args[1]
        button_name = " ".join(context.args[2:])
        CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)", (username, button_name, link))
        DB.commit()
        await update.message.reply_text(f"✅ Channel {username} Added!")
    except:
        await update.message.reply_text("❌ Format: /addchannel @username link Button Name")

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        username = context.args[0]
        CURSOR.execute("DELETE FROM channels WHERE username=?", (username,))
        DB.commit()
        await update.message.reply_text(f"✅ Channel {username} Removed!")
    except:
        await update.message.reply_text("❌ Format: /removechannel @username")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    CURSOR.execute("SELECT * FROM channels")
    rows = CURSOR.fetchall()
    text = "\n".join([f"{r[0]} | {r[1]}" for r in rows])
    await update.message.reply_text(text or "No channels found.")

# ================= POST / BROADCAST WIZARD =================
# Conversation states
(
    POST_TITLE, POST_PHOTO, POST_FORCE_JOIN, POST_TARGET, POST_URL, CONFIRM_SEND, BROADCAST_MODE
) = range(7)

# Temp storage
post_data = {}
broadcast_mode = {}

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    post_data[update.effective_user.id] = {}
    await update.message.reply_text("📌 Step 1: Send Post Title")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['title'] = update.message.text
    await update.message.reply_text("📌 Step 2: Send Post Photo (or /skip to skip)")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['photo_file_id'] = update.message.photo[-1].file_id
    await update.message.reply_text("📌 Step 3: Select Force Join Channels (comma-separated IDs)")
    return POST_FORCE_JOIN

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['photo_file_id'] = None
    await update.message.reply_text("📌 Step 3: Select Force Join Channels (comma-separated IDs)")
    return POST_FORCE_JOIN

async def post_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['force_join_channels'] = update.message.text
    await update.message.reply_text("📌 Step 4: Select Target Channels (comma-separated IDs)")
    return POST_TARGET

async def post_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['target_channels'] = update.message.text
    await update.message.reply_text("📌 Step 5: Send URL or /skip to skip")
    return POST_URL

async def post_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['url'] = update.message.text
    await update_message_preview(update, context)
    return CONFIRM_SEND

async def skip_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data[update.effective_user.id]['url'] = None
    await update_message_preview(update, context)
    return CONFIRM_SEND

async def update_message_preview(update, context):
    data = post_data[update.effective_user.id]
    preview = f"📄 Title: {data['title']}\nForce Join Channels: {data['force_join_channels']}\nTarget Channels: {data['target_channels']}\nURL: {data['url'] or 'None'}"
    await update.message.reply_text(preview)
    await update.message.reply_text("✅ Step 6: Confirm Send? (Yes/No)")

async def confirm_send(update, context):
    text = update.message.text.lower()
    if text == 'yes':
        data = post_data.pop(update.effective_user.id)
        CURSOR.execute("INSERT INTO posts (title, photo_file_id, force_join_channels, target_channels, url) VALUES (?,?,?,?,?)",
                       (data['title'], data['photo_file_id'], data['force_join_channels'], data['target_channels'], data['url']))
        DB.commit()
        await send_to_targets(context, data)
        await update.message.reply_text("✅ Post Sent!")
    else:
        post_data.pop(update.effective_user.id, None)
        await update.message.reply_text("❌ Post Cancelled")
    return ConversationHandler.END

async def send_to_targets(context, data):
    targets = data['target_channels'].split(',')
    for chat_id in targets:
        buttons = []
        if data['force_join_channels']:
            fj = data['force_join_channels'].split(',')
            for c in fj:
                buttons.append([InlineKeyboardButton(f"Join {c}", url=f"https://t.me/{c.strip()}")])
        if data['url']:
            buttons.append([InlineKeyboardButton("Watch Video 🎬", url=data['url'])])
        kb = InlineKeyboardMarkup(buttons) if buttons else None
        if data['photo_file_id']:
            await context.bot.send_photo(chat_id=int(chat_id.strip()), photo=data['photo_file_id'], caption=data['title'], reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=int(chat_id.strip()), text=data['title'], reply_markup=kb)

async def postcancel(update, context):
    post_data.pop(update.effective_user.id, None)
    broadcast_mode.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ Current post/broadcast cancelled")
    return ConversationHandler.END

async def broadcast(update, context):
    if not is_admin(update.effective_user.id):
        return
    broadcast_mode[update.effective_user.id] = True
    await update.message.reply_text("📢 Broadcast mode enabled. Send message/photo to broadcast to all users.")
    return BROADCAST_MODE

async def broadcast_send(update, context):
    if update.effective_user.id not in broadcast_mode:
        return
    CURSOR.execute("SELECT user_id FROM users")
    users = CURSOR.fetchall()
    for u in users:
        try:
            if update.message.photo:
                await context.bot.send_photo(chat_id=u[0], photo=update.message.photo[-1].file_id, caption=update.message.caption)
            elif update.message.text:
                await context.bot.send_message(chat_id=u[0], text=update.message.text)
        except:
            continue
    await update.message.reply_text("✅ Broadcast sent to all users")

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Post Wizard
    post_conv = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo), CommandHandler("skip", skip_photo)],
            POST_FORCE_JOIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_force_join)],
            POST_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_target)],
            POST_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_url), CommandHandler("skip", skip_url)],
            CONFIRM_SEND: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_send)],
            BROADCAST_MODE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_send)]
        },
        fallbacks=[CommandHandler("postcancel", postcancel)]
    )

    app.add_handler(post_conv)

    print("Bot is running with ALL features...")
    app.run_polling()
