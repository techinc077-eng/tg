import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import threading
import http.server
import socketserver
from datetime import datetime

# ==============================
#  SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465
LOG_FILE = "bot.log"

# Store usernames
group_members = set()

# ==============================
#  LOGGING FUNCTION
# ==============================
def log_event(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

# ==============================
#  WELCOME MESSAGE
# ==============================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)

        caption = f"""
🚀 *CR7 FAMILY — IT’S VOTING TIME!* 🐐  

Welcome @{username}! ⚡  
Let’s unite and vote CR7 Token to the top! 💪🔥  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

👇 Tap below to vote & claim your Rewards!
"""
        keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        log_event(f"✅ Welcome message sent to @{username}")

# ==============================
#  REMINDER MESSAGE
# ==============================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    base_message = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top of Sol Trending! 💪⚡  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to Vote & Claim your Reward 👇
"""
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    members = list(group_members)
    batch_size = 5

    if not members:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        log_event("📢 Reminder sent (no users tagged)")
        return

    for i in range(0, len(members), batch_size):
        batch = members[i:i + batch_size]
        tags = ", ".join([f"@{u}" for u in batch])
        full_msg = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            log_event(f"📢 Reminder sent to: {tags}")
        except Exception as e:
            log_event(f"❌ Reminder error: {e}")
        await asyncio.sleep(7)

# ==============================
#  KEEP-ALIVE SERVER
# ==============================
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            log_event(f"🌐 Keep-alive server running on port {PORT}")
            httpd.serve_forever()
    except OSError:
        log_event(f"⚠️ Port {PORT} already in use. Keep-alive server skipped.")

# ==============================
#  BOT START / AUTO-RESTART
# ==============================
async def run_bot_forever():
    while True:
        app = None
        try:
            log_event("🤖 Starting Telegram bot…")
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

            # Repeating reminder every 10 minutes
            app.job_queue.run_repeating(send_reminder, interval=600, first=15)

            await app.initialize()
            await app.start()
            await app.run_polling(stop_signals=None)

        except Exception as e:
            log_event(f"❌ BOT CRASHED — Restarting in 5s: {e}")
            if app:
                try:
                    await app.stop()
                    await app.shutdown()
                except Exception:
                    pass
            await asyncio.sleep(5)

# ==============================
#  MAIN
# ==============================
async def main():
    threading.Thread(target=keep_alive, daemon=True).start()
    await run_bot_forever()

if __name__ == "__main__":
    asyncio.run(main())
