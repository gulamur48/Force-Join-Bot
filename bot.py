import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- Render Port Fix Start ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check_server():
    # Render নিজে থেকে একটি PORT এসাইন করে, সেটি খুঁজে বের করা
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# আলাদা থ্রেডে সার্ভার চালু করা যাতে বটের কাজে বাধা না দেয়
threading.Thread(target=run_health_check_server, daemon=True).start()
# --- Render Port Fix End ---

# আপনার বট টোকেন (আপনার নতুন টোকেনটি এখানে দিন)
TOKEN = '8510787985:AAGZ9KA-16hl8Tc3H1_GM-D3qCMIGygOUkw' 

# আপনার ৫টি চ্যানেলের ইউজারনেম
CHANNELS = ['@virallink259', '@viralfb24', '@fbviral24', '@viralfacebook9', '@viralexpress1']

# বাটনগুলোতে যে নাম দেখাতে চান
CHANNEL_DISPLAY_NAMES = ["Viral Link 🎬", "Viral FB 🚀", "FB Viral 🔥", "Facebook Viral 📽️", "Viral Express ⚡"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_all_joined(user_id, context):
    not_joined_indices = []
    for i, channel in enumerate(CHANNELS):
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined_indices.append(i)
        except Exception:
            not_joined_indices.append(i)
    return not_joined_indices

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    stylish_name = f"👤 <b>{user.first_name}</b>"
    
    not_joined_indices = await check_all_joined(user_id, context)

    if not not_joined_indices:
        await update.message.reply_text(f"✅ স্বাগতম {stylish_name}!\nআপনি সব চ্যানেলে জয়েন করেছেন। এখন ভিডিও দেখতে পারেন।", parse_mode=ParseMode.HTML)
    else:
        buttons = []
        for index in not_joined_indices:
            name = CHANNEL_DISPLAY_NAMES[index]
            link = CHANNELS[index][1:]
            buttons.append([InlineKeyboardButton(f"Join {name}", url=f"https://t.me/{link}")])
        
        buttons.append([InlineKeyboardButton("Check Joined ✅", callback_data="check_status")])
        
        caption = (
            f"Hello {stylish_name},\n\n"
            "🚨 <b>Attention Please!</b>\n\n"
            "Viral ভিডিও দেখার আগে আমাদের Channel Join করা বাধ্যতামূলক।\n"
            "চ্যানেল Join না করলে ভিডিও অ্যাক্সেস পাওয়া যাবে না ❌\n\n"
            "Join করে <b>Check Joined</b> ক্লিক করুন ✅"
        )
        
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stylish_name = f"<b>{user.first_name}</b>"
    not_joined_indices = await check_all_joined(user.id, context)
    
    if not not_joined_indices:
        await query.answer(f"ধন্যবাদ {user.first_name}! জয়েন হয়েছে।", show_alert=True)
        await query.edit_message_text(f"✅ অভিনন্দন {stylish_name}!\nআপনি সফলভাবে সব চ্যানেলে জয়েন করেছেন।", parse_mode=ParseMode.HTML)
    else:
        await query.answer("❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি!", show_alert=True)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("Bot is running with Render Fix...")
    app.run_polling()
