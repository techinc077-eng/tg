import os
import asyncio
import threading
import http.server
import socketserver
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ==============================
# SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

group_members = set()  # Track users

# ==============================
# WELCOME MESSAGE
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
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    # Send batches of 5 members
    for i in range(0, len(members), batch_size):
        batch = members[i:i+batch_size]
        tags = ", ".join([f"@{u}" for u in batch])
        full_message = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("❌ Reminder error:", e)
        await asyncio.sleep(7)  # small delay to avoid spam

# ==============================
# KEEP-ALIVE SERVER (Render requirement)
# ==============================
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 Keep-alive server running on port {port}")
        httpd.serve_forever()

# ==============================
# RUN BOT FOREVER
# ==============================
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.job_queue.run_repeating(send_reminder, interval=600, first=15)  # every 10 minutes

    print("🤖 BOT STARTED — Welcome + 10-min reminders active")
    await app.run_polling()

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    # Start keep-alive in a separate thread
    threading.Thread(target=keep_alive, daemon=True).start()
    asyncio.run(run_bot())
