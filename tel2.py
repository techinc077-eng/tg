from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import JobQueue
import asyncio
import os
import threading
import http.server
import socketserver

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
It’s time to unite and vote for CR7 Token. Let’s push our project to the top! 💪🔥  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

👇 Tap below to vote & claim your rewards!
"""

        keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# === REMINDER ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    base_message = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top! 💪⚡  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to vote & earn now 👇
"""

    members_list = list(group_members)

    if not members_list:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    batch_size = 5

    for i in range(0, len(members_list), batch_size):
        batch = members_list[i:i + batch_size]
        tags = ", ".join([f"@{u}" for u in batch if u])

        full_message = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await asyncio.sleep(8)
        except Exception as e:
            print(f"⚠️ Error sending reminder batch: {e}")
            await asyncio.sleep(3)

# === MAIN APP ===
async def main():
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Job Queue
    job_queue = app.job_queue
    job_queue.run_repeating(send_reminder, interval=60 * 10, first=5)

    print("🤖 CR7 Bot running... reminders active forever")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep bot alive without blocking JobQueue
    while True:
        await asyncio.sleep(5)

# === KEEP-ALIVE SERVER FOR RENDER ===
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌐 Keep-alive server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    asyncio.run(main())
