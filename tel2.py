import os
import threading
import http.server
import socketserver
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)
import asyncio

# ==============================
# SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

# Track group members
group_members = set()

# ==============================
# WELCOME MESSAGE
# ==============================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.new_chat_members:
        return

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

# ==============================
# REMINDER MESSAGE
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
        # Send message without tags
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    # Send tags in groups of 5
    for i in range(0, len(members), batch_size):
        batch = members[i:i + batch_size]
        tags = ", ".join(f"@{u}" for u in batch)
        full_msg = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("❌ Error sending reminder:", e)

        await asyncio.sleep(7)  # anti-spam delay

# ==============================
# KEEP-ALIVE SERVER (REQUIRED BY RENDER)
# ==============================
def keep_alive_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌐 Keep-alive server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        print("⚠️ Keep-alive server error:", e)

# ==============================
# MAIN BOT FUNCTION
# ==============================
def main():

    print("🤖 Starting CR7 Bot…")

    app = ApplicationBuilder().token(TOKEN).build()

    # Welcome handler
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )

    # Reminder every 10 minutes
    app.job_queue.run_repeating(
        send_reminder,
        interval=600,   # 10 minutes
        first=15        # fire first reminder after 15 seconds
    )

    # Start bot (handles its own event loop)
    app.run_polling()

# ==============================
# START EVERYTHING
# ==============================
if __name__ == "__main__":

    # Launch keep-alive server on a background thread
    threading.Thread(target=keep_alive_server, daemon=True).start()

    # Run Telegram bot
    main()
