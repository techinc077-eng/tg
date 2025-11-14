import os
import asyncio
import threading
import http.server
import socketserver
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

# ==============================
#  SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

# Store usernames
group_members = set()


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

    # If no members yet
    if not members:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    # Send batches of 5 users each
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
        except Exception as e:
            print("❌ Reminder error:", e)

        await asyncio.sleep(7)  # Anti-spam delay per batch


# ==============================
#  KEEP-ALIVE SERVER FOR RENDER
# ==============================
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as server:
        print(f"🌐 Keep-alive running on port {PORT}")
        server.serve_forever()


# ==============================
#  AUTO-RESTART PROTECTED BOT LOOP
# ==============================
async def run_bot_forever():

    while True:
        try:
            print("🤖 Starting Telegram bot…")

            app = ApplicationBuilder().token(TOKEN).build()

            # Handle new members
            app.add_handler(
                MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
            )

            # Reminder every 10 minutes
            app.job_queue.run_repeating(send_reminder, interval=600, first=15)

            # Start polling mode
            await app.run_polling(close_loop=False)

        except Exception as e:
            print("❌ BOT CRASHED — Restarting in 5s:", e)

        await asyncio.sleep(5)  # Delay before restart


# ==============================
#  MAIN
# ==============================
async def main():
    # Start keep-alive server in background thread
    threading.Thread(target=keep_alive, daemon=True).start()

    # Start bot forever loop
    await run_bot_forever()


if __name__ == "__main__":
    asyncio.run(main())
