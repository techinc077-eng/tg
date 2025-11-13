from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio
import threading
import http.server
import socketserver
import os

# === SETTINGS ===
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

# === GLOBAL DATA ===
group_members = set()

# === WELCOME ===
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

# === REMINDER ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):

    base_message = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top of Sol Trending! 💪⚡  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to Vote & Claim your Reward👇
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
        return

    for i in range(0, len(members), batch_size):
        batch = members[i:i + batch_size]
        tags = ", ".join(f"@{u}" for u in batch)
        message = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await asyncio.sleep(5)
        except Exception as e:
            print("Error sending:", e)
            await asyncio.sleep(3)

# === KEEP-ALIVE ===
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler

    # prevent port-in-use crash
    try:
        with socketserver.TCPServer(("", PORT), handler) as server:
            print(f"🌐 Keep-alive running on port {PORT}")
            server.serve_forever()
    except OSError:
        print("⚠ Port already in use — skipping keep-alive server")

# === START BOT ===
def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.job_queue.run_repeating(send_reminder, interval=600, first=10)

    print("🤖 BOT RUNNING — Polling active")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    start_bot()
