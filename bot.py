import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

# ================= RENDER HEALTH (optional) =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ================= CONFIG =================
TOKEN = "8510787985:AAHjszZmTMwqvqTfbFMJdqC548zBw4Qh0S0"
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

ADMIN_IDS = [123456789]  # <-- নিজের Telegram numeric ID বসাও

# ================= CHANNEL DATA (UNCHANGED) =================
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

logging.basicConfig(level=logging.INFO)

# ================= STATES =================
POST_TITLE, POST_PHOTO, BROADCAST = range(3)

# ================= HELPERS =================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def check_all_joined(user_id, context):
    not_joined = []
    for ch in CHANNELS_DATA:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status not in ("member", "administrator", "creator"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined

def join_keyboard(channels):
    kb = [[InlineKeyboardButton(f"Join {c['name']}", url=c["link"])] for c in channels]
    kb.append([InlineKeyboardButton("✅ Check Joined", callback_data="check")])
    return InlineKeyboardMarkup(kb)

# ================= START / CHECK =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    not_joined = await check_all_joined(user.id, context)

    if not not_joined:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now", url=WATCH_NOW_URL)]])
        await update.message.reply_text(
            f"🎉 <b>{user.first_name}</b>\nসব channel join করা হয়েছে ✅",
            reply_markup=kb,
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            "🚨 আগে নিচের channel গুলো join করুন:",
            reply_markup=join_keyboard(not_joined),
            parse_mode=ParseMode.HTML
        )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    not_joined = await check_all_joined(q.from_user.id, context)

    if not not_joined:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Watch Now", url=WATCH_NOW_URL)]])
        await q.edit_message_text(
            "✅ সব channel join করা হয়েছে!",
            reply_markup=kb
        )
    else:
        await q.answer("❌ এখনো সব channel join করা হয়নি", show_alert=True)

# ================= NEW POST =================
async def newpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("📝 Post title পাঠাও:")
    return POST_TITLE

async def post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("🖼 এখন photo পাঠাও:")
    return POST_PHOTO

async def post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    title = context.user_data["title"]

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Watch Now", callback_data="check")]
    ])

    await update.message.reply_photo(
        photo=photo,
        caption=title,
        reply_markup=kb
    )
    return ConversationHandler.END

async def postcancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("📢 Broadcast message পাঠাও:")
    return BROADCAST

async def do_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Broadcast sent (demo)")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", start))
    app.add_handler(CallbackQueryHandler(check_callback))

    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("newpost", newpost)],
            states={
                POST_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_title)],
                POST_PHOTO: [MessageHandler(filters.PHOTO, post_photo)],
            },
            fallbacks=[CommandHandler("postcancel", postcancel)]
        )
    )

    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("broadcast", broadcast)],
            states={BROADCAST: [MessageHandler(filters.ALL, do_broadcast)]},
            fallbacks=[CommandHandler("cancel", postcancel)]
        )
    )

    print("✅ Bot running on Render Worker...")
    app.run_polling()
