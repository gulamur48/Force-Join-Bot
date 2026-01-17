import logging
import os
import threading
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
CURSOR.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
CURSOR.execute("CREATE TABLE IF NOT EXISTS channels (username TEXT PRIMARY KEY, button TEXT, link TEXT)")
DB.commit()

# ================= CHANNELS DATA =================
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

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)
    await update.message.reply_text(f"👋 Hello {user.first_name}!\nUse /newpost to start creating a post.")

# ================= NEWPOST WIZARD =================
POST_TITLE, POST_PHOTO, POST_FORCE_JOIN, POST_TARGET, POST_URL, CONFIRM_SEND = range(6)

async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    context.user_data['post_data'] = {'fj': [], 'target': [], 'photo': None, 'url': None}
    await update.message.reply_text("✨ **Step 1:** Post Title pathan:")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['title'] = update.message.text
    await update.message.reply_text("📸 **Step 2:** Photo pathan ba /skip likhun:")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['photo'] = update.message.photo[-1].file_id
    return await show_fj_menu(update, context)

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_fj_menu(update, context)

async def show_fj_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = context.user_data['post_data']['fj']
    buttons = []
    for c in CHANNELS_DATA:
        status = "✅" if c['id'] in selected else "❌"
        buttons.append([InlineKeyboardButton(f"{status} {c['name']}", callback_data=f"selfj_{c['id']}")])
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="fj_done")])
    
    text = "🔒 **Step 3:** Force Join Channels select korun:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    return POST_FORCE_JOIN

async def fj_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "fj_done":
        return await show_target_menu(update, context)
    
    cid = data.replace("selfj_", "")
    try: cid = int(cid)
    except: pass
    
    if cid in context.user_data['post_data']['fj']:
        context.user_data['post_data']['fj'].remove(cid)
    else:
        context.user_data['post_data']['fj'].append(cid)
    
    await show_fj_menu(update, context)
    return POST_FORCE_JOIN

async def show_target_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = context.user_data['post_data']['target']
    buttons = []
    for c in CHANNELS_DATA:
        status = "✅" if c['id'] in selected else "❌"
        buttons.append([InlineKeyboardButton(f"{status} {c['name']}", callback_data=f"seltg_{c['id']}")])
    buttons.append([InlineKeyboardButton("Done ➡️", callback_data="tg_done")])
    
    await update.callback_query.edit_message_text("🎯 **Step 4:** Target Channels select korun:", reply_markup=InlineKeyboardMarkup(buttons))
    return POST_TARGET

async def target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "tg_done":
        await query.message.reply_text("🔗 **Step 5:** Post URL pathan ba /skip likhun:")
        return POST_URL
    
    cid = data.replace("seltg_", "")
    try: cid = int(cid)
    except: pass
    
    if cid in context.user_data['post_data']['target']:
        context.user_data['post_data']['target'].remove(cid)
    else:
        context.user_data['post_data']['target'].append(cid)
    
    await show_target_menu(update, context)
    return POST_TARGET

async def post_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_data']['url'] = update.message.text
    return await show_summary(update, context)

async def skip_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_summary(update, context)

async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data['post_data']
    summary = (
        "📊 **Post Summary:**\n\n"
        f"📝 **Title:** {d['title']}\n"
        f"🖼 **Photo:** {'Setted ✅' if d['photo'] else 'Skipped ❌'}\n"
        f"🔒 **FJ Channels:** {len(d['fj'])}\n"
        f"🎯 **Targets:** {len(d['target'])}\n"
        f"🔗 **URL:** {d['url'] if d['url'] else 'Default'}\n\n"
        "Confirm send?"
    )
    kb = [[InlineKeyboardButton("✅ Confirm Send", callback_data="conf_send"), 
           InlineKeyboardButton("❌ Cancel", callback_data="conf_cancel")]]
    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    return CONFIRM_SEND

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "conf_cancel":
        await query.edit_message_text("❌ Wizard aborted.")
        return ConversationHandler.END
    
    d = context.user_data['post_data']
    final_url = d['url'] if d['url'] else WATCH_NOW_URL
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Watch Now 🎬", url=final_url)]])
    
    await query.edit_message_text("🚀 Sending post...")
    
    for target in d['target']:
        try:
            if d['photo']:
                await context.bot.send_photo(chat_id=target, photo=d['photo'], caption=d['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                await context.bot.send_message(chat_id=target, text=d['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Failed to send to {target}: {e}")
            
    await query.message.reply_text("✅ Post successfully sent to all targets!")
    return ConversationHandler.END

async def postcancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🚫 Wizard cancelled.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Newpost Wizard
    newpost_conv = ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost)],
        states={
            POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title)],
            POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo), CommandHandler("skip", skip_photo)],
            POST_FORCE_JOIN: [CallbackQueryHandler(fj_callback, pattern="^selfj_|^fj_done$")],
            POST_TARGET: [CallbackQueryHandler(target_callback, pattern="^seltg_|^tg_done$")],
            POST_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_url), CommandHandler("skip", skip_url)],
            CONFIRM_SEND: [CallbackQueryHandler(confirm_handler, pattern="^conf_")],
        },
        fallbacks=[CommandHandler("postcancel", postcancel)],
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(newpost_conv)
    
    print("Bot is active and wizard is ready...")
    app.run_polling()
