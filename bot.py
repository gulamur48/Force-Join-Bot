import logging
import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- Render Port Fix ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# --- কনফিগারেশন ---
TOKEN = os.environ.get("BOT_TOKEN") 
WATCH_NOW_URL = "https://mmshotbd.blogspot.com/?m=1"

# আপনার বটের ইউজারনেম এখানে দিন (অ্যাট সাইন @ ছাড়া)
BOT_USERNAME = "Viral_Video_Link_2026_bot" 

# শেয়ার করার টেক্সট এবং লিঙ্ক
SHARE_TEXT = "🔥 অসাধারণ সব ভাইরাল ভিডিও দেখতে নিচের বাটনে ক্লিক করুন! 🎬✨"
# এটি এমন একটি লিঙ্ক যা গ্রুপে শেয়ার করলে সুন্দর দেখাবে
SHARE_URL = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=viral&text={urllib.parse.quote(SHARE_TEXT)}"

# ১১টি চ্যানেলের ডাটাবেস
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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_all_joined(user_id, context):
    not_joined = []
    for channel in CHANNELS_DATA:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append(channel)
        except Exception:
            not_joined.append(channel)
    return not_joined

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stylish_name = f"👤 <b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)

    if not not_joined_list:
        success_text = (
            f"🎉 স্বাগতম {stylish_name}\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️\n"
            f"▶️ ভিডিও দেখতে নিচের বাটনে ক্লিক করুন 🎬"
        )
        keyboard = [
            [InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)],
            [InlineKeyboardButton("Share with Friends 🚀", url=SHARE_URL)]
        ]
        await update.message.reply_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    else:
        # জয়েন না করা চ্যানেলের বাটন তৈরি
        buttons = []
        for channel in not_joined_list:
            buttons.append([InlineKeyboardButton(f"Join {channel['name']}", url=channel['link'])])
        
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        buttons.append([InlineKeyboardButton("Forward to Groups 📤", url=SHARE_URL)])
        
        caption = (
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের নিচের Channel গুলোতে Join করা বাধ্যতামূলক।\n"
            "সবগুলো চ্যানেল Join না করলে ভিডিও লিঙ্ক কাজ করবে না ❌\n\n"
            "Join শেষ হলে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stylish_name = f"<b>{user.first_name}</b>"
    not_joined_list = await check_all_joined(user.id, context)
    
    if not not_joined_list:
        await query.answer("ধন্যবাদ! ভেরিফাই সফল হয়েছে।", show_alert=True)
        success_text = (
            f"🎉 স্বাগতম {stylish_name}\n"
            f"✅ আপনি সফলভাবে সব চ্যানেলে Join করেছেন ❤️"
        )
        keyboard = [
            [InlineKeyboardButton("Watch Now 🎬", url=WATCH_NOW_URL)],
            [InlineKeyboardButton("Share with Friends 🚀", url=SHARE_URL)]
        ]
        await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    else:
        await query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি!", show_alert=True)

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_callback))
        print("Bot is running with Advanced Share system...")
        app.run_polling()
