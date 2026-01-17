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

# ================= HEALTH CHECK (FOR RENDER) =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running perfectly!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

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

# ================= 11 ORIGINAL CHANNELS (UNTOUCHED) =================
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
async def get_all_channels():
    CURSOR.execute("SELECT username, button, link FROM channels")
    rows = CURSOR.fetchall()
    db_channels = [{"id": r[0], "name": r[1], "link": r[2]} for r in rows]
    return CHANNELS_DATA + db_channels

async def check_all_joined(user_id, context, fj_list):
    not_joined = []
    for channel in fj_list:
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
    CURSOR.execute("INSERT OR IGNORE INTO users VALUES (?)", (user.id,))
    DB.commit()
    all_ch = await get_all_channels()
    not_joined = await check_all_joined(user.id, context, all_ch)

    if not not_joined:
        text = (f"🌈 <b>স্বাগতম প্রিয়, {user.first_name}!</b> 💖✨\n\n"
                f"🌟 <b>Congratulation!</b> আপনার ভেরিফিকেশন সফলভাবে সম্পন্ন হয়েছে। ✅\n"
                f"এখন আপনি আমাদের সব প্রিমিয়াম এবং ভাইরাল ভিডিওগুলো উপভোগ করতে পারবেন। 🔞🔥\n\n"
                f"🚀 <b>ভিডিও দেখতে নিচের বাটনে ক্লিক করুন:</b> 👇🎥")
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿", url=WATCH_NOW_URL)]]), parse_mode=ParseMode.HTML)
    else:
        btns = [[InlineKeyboardButton(f"➕ জয়েন: {c['name']} 🚀", url=c['link'])] for c in not_joined]
        btns.append([InlineKeyboardButton("✅ জয়েন সম্পন্ন করেছি (Verify) 🔄✨", callback_data="check_status")])
        text = (f"👋 <b>হ্যালো {user.first_name}!</b> ❤️🔥\n\n"
                f"🚨 <b>Attention Please!</b> 🔞\n"
                f"ভাইরাল কন্টেন্টগুলো দেখার আগে আপনাকে আমাদের সব চ্যানেলে জয়েন করতে হবে। 💎✨\n\n"
                f"⚠️ <b>সবগুলো চ্যানেল জয়েন না করলে ভিডিও লিঙ্ক কাজ করবে না!</b> ❌\n"
                f"জয়েন শেষ করে নিচের ভেরিফাই বাটনে ক্লিক করুন। 👇💫")
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

# ================= NEWPOST WIZARD =================
P_TITLE, P_PHOTO, P_FJ, P_TARGET, P_CONFIRM = range(5)

async def newpost_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return ConversationHandler.END
    msg = await update.message.reply_text("📝 <b>নতুন পোস্ট তৈরি করুন</b> ✨🔥\n\nপ্রথমে পোস্টের জন্য একটি সুন্দর টাইটেল বা ক্যাপশন লিখে পাঠান: 👇💫", parse_mode=ParseMode.HTML)
    context.user_data['post'] = {'title': '', 'photo': None, 'fj': [], 'target': []}
    context.user_data['last_msg'] = msg.message_id
    return P_TITLE

async def p_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post']['title'] = update.message.text
    await update.message.delete()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_msg'])
    msg = await update.message.reply_text("📸 <b>ধাপ ২: ফটো আপলোড করুন</b> ✨🖼️\n\nপোস্টের জন্য একটি ফটো পাঠান। ফটো না দিতে চাইলে /skip লিখে পাঠান: ⏭️💎", parse_mode=ParseMode.HTML)
    context.user_data['last_msg'] = msg.message_id
    return P_PHOTO

async def p_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data['post']['photo'] = update.message.photo[-1].file_id
    await update.message.delete()
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['last_msg'])
    return await show_fj_menu(update, context)

async def show_fj_menu(update, context):
    all_ch = await get_all_channels()
    sel = context.user_data['post']['fj']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"tfj_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("➡️ পরবর্তী ধাপ (Target) ✨🚀", callback_data="fj_done")])
    text = "🔒 <b>ধাপ ৩: ফোর্স জয়েন (FJ)</b> 🛡️✨\n\nভিডিও দেখার আগে কোন চ্যানেলগুলো জয়েন করা বাধ্যতামূলক? নিচের লিস্ট থেকে সিলেক্ট করুন: 👇🔥"
    msg = await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    context.user_data['last_msg'] = msg.message_id
    return P_FJ

async def fj_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.data.replace("tfj_", "")
    if cid in context.user_data['post']['fj']: context.user_data['post']['fj'].remove(cid)
    else: context.user_data['post']['fj'].append(cid)
    all_ch = await get_all_channels()
    sel = context.user_data['post']['fj']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"tfj_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("➡️ পরবর্তী ধাপ (Target) ✨🚀", callback_data="fj_done")])
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))

async def fj_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.delete()
    return await show_target_menu(update, context)

async def show_target_menu(update, context):
    all_ch = await get_all_channels()
    sel = context.user_data['post']['target']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"ttg_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("📊 প্রিভিউ দেখুন (Preview) 🚀🎬", callback_data="tg_done")])
    text = "🎯 <b>ধাপ ৪: টার্গেট চ্যানেল</b> 📡✨\n\nপোস্টটি কোন কোন চ্যানেলে পাঠাতে চান? নিচের লিস্ট থেকে সিলেক্ট করুন: 👇💫"
    msg = await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    context.user_data['last_msg'] = msg.message_id
    return P_TARGET

async def tg_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.data.replace("ttg_", "")
    if cid in context.user_data['post']['target']: context.user_data['post']['target'].remove(cid)
    else: context.user_data['post']['target'].append(cid)
    all_ch = await get_all_channels()
    sel = context.user_data['post']['target']
    btns = [[InlineKeyboardButton(f"{'✅' if str(c['id']) in sel else '❌'} {c['name']}", callback_data=f"ttg_{c['id']}")] for c in all_ch]
    btns.append([InlineKeyboardButton("📊 প্রিভিউ দেখুন (Preview) 🚀🎬", callback_data="tg_done")])
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))

async def tg_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()
    p = context.user_data['post']
    prev = (f"🏁 <b>ফাইনাল প্রিভিউ (Final Preview)</b> 💎✨\n\n"
            f"📝 <b>টাইটেল:</b> <code>{p['title']}</code>\n"
            f"🔒 <b>ফোর্স জয়েন:</b> {len(p['fj'])}টি চ্যানেল\n"
            f"🎯 <b>টার্গেট:</b> {len(p['target'])}টি চ্যানেলে পোস্ট হবে।\n\n"
            f"সবকিছু ঠিক থাকলে নিচের বাটনে ক্লিক করুন। 👇💫")
    btns = [[InlineKeyboardButton("🚀 এখনই পাঠান (Confirm) ✅🔥", callback_data="send_now")], [InlineKeyboardButton("❌ বাতিল করুন (Cancel) 🚫", callback_data="cancel")]]
    if p['photo']: await query.message.reply_photo(photo=p['photo'], caption=prev, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    else: await query.message.reply_text(prev, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)
    return P_CONFIRM

async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    p = context.user_data['post']
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿", callback_data=f"cp_{','.join(p['fj'])}")]])
    done = 0
    for tid in p['target']:
        try:
            if p['photo']: await context.bot.send_photo(chat_id=tid, photo=p['photo'], caption=p['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
            else: await context.bot.send_message(chat_id=tid, text=p['title'], reply_markup=kb, parse_mode=ParseMode.HTML)
            done += 1
        except: pass
    await query.message.delete()
    await query.message.reply_text(f"🎊 <b>অভিনন্দন!</b> ✅🔥\n\nসফলভাবে {done}টি চ্যানেলে আপনার পোস্টটি পাঠানো হয়েছে। 🚀💎", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# ================= ADD CHANNEL WIZARD =================
A_ID, A_LINK, A_NAME = range(10, 13)
async def addch_start(update, context):
    if update.effective_user.id not in ADMIN_IDS: return ConversationHandler.END
    await update.message.reply_text("✨ <b>নতুন চ্যানেল যোগ করুন</b> ➕💎\n\nপ্রথমে চ্যানেলের আইডি বা ইউজারনেমটি পাঠান (যেমন: @username): 👇🚀", parse_mode=ParseMode.HTML)
    return A_ID

async def a_id(update, context):
    context.user_data['aid'] = update.message.text
    await update.message.reply_text("🔗 এবার চ্যানেলের <b>ইনভাইট লিঙ্কটি (Invite Link)</b> পাঠান: 👇💫", parse_mode=ParseMode.HTML)
    return A_LINK

async def a_link(update, context):
    context.user_data['alink'] = update.message.text
    await update.message.reply_text("🔘 সবশেষে জয়েন বাটনের জন্য একটি <b>নাম</b> দিন: 👇🔥", parse_mode=ParseMode.HTML)
    return A_NAME

async def a_save(update, context):
    CURSOR.execute("INSERT OR REPLACE INTO channels VALUES (?,?,?)", (context.user_data['aid'], update.message.text, context.user_data['alink']))
    DB.commit()
    await update.message.reply_text("✅ <b>চ্যানেলটি সফলভাবে ডাটাবেসে সেভ করা হয়েছে!</b> 🎉🚀💎", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

# ================= COMMON LOGIC =================
async def cb_handler(update, context):
    query = update.callback_query
    all_ch = await get_all_channels()
    if query.data == "check_status":
        not_joined = await check_all_joined(query.from_user.id, context, all_ch)
        if not not_joined: await query.edit_message_text("✅ <b>অভিনন্দন!</b> 💖✨\n\nআপনার ভেরিফিকেশন সফল হয়েছে। ভিডিও দেখতে নিচের বাটনে ক্লিক করুন। 👇🎬", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 এখনই দেখুন (Watch Now) ✨🍿", url=WATCH_NOW_URL)]]), parse_mode=ParseMode.HTML)
        else: await query.answer("❌ আপনি এখনো সব চ্যানেলে জয়েন করেননি! দয়া করে জয়েন করুন। 🔥", show_alert=True)
    elif query.data.startswith("cp_"):
        fjs = query.data.replace("cp_", "").split(",")
        fj_ch = [c for c in all_ch if str(c['id']) in fjs]
        missing = await check_all_joined(query.from_user.id, context, fj_ch)
        if not missing: await query.message.reply_text(f"🚀 <b>আপনার প্রিমিয়াম ভিডিও লিঙ্ক:</b> ✨🔥\n\n{WATCH_NOW_URL}", parse_mode=ParseMode.HTML)
        else:
            btns = [[InlineKeyboardButton(f"➕ জয়েন: {c['name']} 🚀", url=c['link'])] for c in missing]
            btns.append([InlineKeyboardButton("ভেরিফাই করুন 🔄✨", callback_data=query.data)])
            await query.message.reply_text("⛔ <b>অ্যাক্সেস ডিনাইড!</b> 🔞\n\nভিডিও দেখতে আগে নিচের চ্যানেলগুলোতে জয়েন করুন: 👇🔥", reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.HTML)

async def cancel(update, context):
    if update.callback_query: await update.callback_query.message.delete()
    await update.effective_message.reply_text("❌ অপারেশনটি বাতিল করা হয়েছে। 🚫")
    return ConversationHandler.END

# ================= APP INITIALIZATION =================
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("newpost", newpost_start)],
        states={
            P_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_title)],
            P_PHOTO: [MessageHandler(filters.PHOTO, p_photo), CommandHandler("skip", p_photo)],
            P_FJ: [CallbackQueryHandler(fj_toggle, pattern="^tfj_"), CallbackQueryHandler(fj_done, pattern="^fj_done$")],
            P_TARGET: [CallbackQueryHandler(tg_toggle, pattern="^ttg_"), CallbackQueryHandler(tg_done, pattern="^tg_done$")],
            P_CONFIRM: [CallbackQueryHandler(send_now, pattern="^send_now$"), CallbackQueryHandler(cancel, pattern="^cancel$")]
        }, fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addchannel", addch_start)],
        states={A_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, a_id)], A_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, a_link)], A_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, a_save)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb_handler))
    
    print("Bot is successfully running with Extra Premium UI...")
    app.run_polling()
