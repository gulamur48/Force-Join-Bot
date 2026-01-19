import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, InlineQueryHandler, filters, ContextTypes

# =================== CONFIG ===================
BOT_TOKEN = "8007194607:AAHhuMvS3z814Fr2eF_17K1wv8UPXmvA1kY"
ADMIN_ID = 8013042180
DEMO_API_KEY = "DEMO_API_KEY"

CHANNELS = [
    {"username": "virallink259", "button": "🔥 Join Channel 1 🔥"},
    {"username": "viralfacebook9", "button": "🔥 Join Channel 2 🔥"},
    {"username": "viralfb24", "button": "🔥 Join Channel 3 🔥"},
    {"username": "fbviral24", "button": "🔥 Join Channel 4 🔥"}
]

MESSAGES = {
    "welcome": "💔 Heyy {user} 😘\n\nএই baby 🫦 bot use করতে হলে আগে আমাদের 🔥 hot private channel 🔥 join করতে হবে 💋\nJoin শেষ হলে নিচের **Verify** বাটনে চাপ দাও 😈",
    "verify_success": "💖 Ahhh {user} 😍🔥\n\nসব channel join করা হয়ে গেছে baby 💋\nএখন তুমি আমার full access পেয়েছ 😈\n\n🔗 Terabox/Facebook/Instagram link পাঠাও, বাকি সব আমি handle করবো 🫦",
    "verify_fail": "💔 Oops {user} 😢🔥\n\nএখনো সব channel join করোনি baby 💋\nআগে সব join করো, তারপর আবার **Verify** চাপ দাও 🫦",
    "unsupported": "❌ Sorry {user}, unsupported link 😢"
}

# =================== UTILITIES ===================
async def check_all_joined(user_id, bot):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(f"@{ch['username']}", user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def demo_download_api(link):
    return "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4", "Demo Video"

def build_channel_buttons():
    # 2-row inline buttons
    row1 = [InlineKeyboardButton(CHANNELS[0]['button'], url=f"https://t.me/{CHANNELS[0]['username']}"),
            InlineKeyboardButton(CHANNELS[1]['button'], url=f"https://t.me/{CHANNELS[1]['username']}")]
    row2 = [InlineKeyboardButton(CHANNELS[2]['button'], url=f"https://t.me/{CHANNELS[2]['username']}"),
            InlineKeyboardButton(CHANNELS[3]['button'], url=f"https://t.me/{CHANNELS[3]['username']}")]
    row3 = [InlineKeyboardButton("💋 Verify 💋", callback_data="verify"),
            InlineKeyboardButton("🚀 Viral Share", switch_inline_query="")]
    return [row1, row2, row3]

def build_video_buttons(video_url):
    row1 = [InlineKeyboardButton("📥 Download", url=video_url),
            InlineKeyboardButton("🚀 Share Video", switch_inline_query="")]
    row2 = [InlineKeyboardButton("😈 Join Channel", url=f"https://t.me/{CHANNELS[0]['username']}"),
            InlineKeyboardButton("🔥 More Videos", switch_inline_query="")]
    return [row1, row2]

# =================== HANDLERS ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = build_channel_buttons()
    await update.message.reply_text(
        MESSAGES["welcome"].format(user=user.mention_html()),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    joined = await check_all_joined(user.id, context.bot)
    if joined:
        msg = await query.message.edit_text(
            MESSAGES["verify_success"].format(user=user.mention_html()),
            parse_mode="HTML"
        )
        await asyncio.sleep(8)
        try: await msg.delete()
        except: pass
    else:
        await query.answer()
        await query.message.edit_text(
            MESSAGES["verify_fail"].format(user=user.mention_html()),
            reply_markup=query.message.reply_markup,
            parse_mode="HTML"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not await check_all_joined(user.id, context.bot):
        await start(update, context)
        return

    if any(x in text.lower() for x in ["terabox", "tbox"]):
        url, title = demo_download_api(text)
    elif any(x in text.lower() for x in ["facebook.com", "fb"]):
        url, title = demo_download_api(text)
    elif any(x in text.lower() for x in ["instagram.com", "insta"]):
        url, title = demo_download_api(text)
    else:
        await update.message.reply_text(MESSAGES["unsupported"].format(user=user.mention_html()), parse_mode="HTML")
        return

    buttons = build_video_buttons(url)
    await update.message.reply_video(
        video=url,
        caption=f"🎬 {title}\n\n💖 Hey {user.mention_html()} 😘\nতোমার ভিডিও ready baby 🔥",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

async def inline_query(update, context):
    query = update.inline_query.query or "🔥 Viral Video"
    row1 = [InlineKeyboardButton("🔥 Watch Now", url="https://sample-videos.com"),
            InlineKeyboardButton("💖 Share", switch_inline_query="")]
    row2 = [InlineKeyboardButton("🚀 Use Bot", url=f"https://t.me/{BOT_TOKEN.split(':')[0]}"),
            InlineKeyboardButton("😈 Join Channel", url=f"https://t.me/{CHANNELS[0]['username']}")]
    buttons = [row1, row2]

    result = InlineQueryResultArticle(
        id="1",
        title="🔥 Hot Viral Video",
        input_message_content=InputTextMessageContent("🔥 Hot Viral Video Available!\n👉 Click & Enjoy 😈"),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await update.inline_query.answer([result], cache_time=5)

# =================== APPLICATION ===================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(verify, pattern="verify"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(InlineQueryHandler(inline_query))

print("Bot is running...")
app.run_polling()
