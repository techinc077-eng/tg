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
GROUP_CHAT_ID = -1003295107465  # Replace with your actual group chat ID

# === GLOBAL DATA ===
group_members = set()

# === WELCOME MESSAGE HANDLER ===
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)

        caption = f"""
🚀 *CR7 FAMILY — IT’S VOTING TIME!* 🐐  

Welcome @{username}! ⚡  
It’s time to unite and vote for CR7 Token — let’s push our project to the top of the trending list! 💪🔥  

✅ *By voting, you’ll earn:*  
• 💰 *CR7 Tokens*  
• 🎁 *SOL Rewards*  

Let’s show the world the unstoppable power of the CR7 Community! 🌍💫  

👇 *Tap below to cast your vote & claim your rewards!*
"""
        keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# === REMINDER MESSAGE HANDLER ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Base reminder text (the user asked to have tags included in this message)
    base_message = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top of the Sol Trending list! 💪⚡  

Each vote counts — and brings you exclusive rewards:  
💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to vote & earn now 👇
"""

    members_list = list(group_members)
    if not members_list:
        # Send just the base message if no members tracked
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    batch_size = 5
    # Send one message per batch: base_message + tags inline
    for i in range(0, len(members_list), batch_size):
        batch = members_list[i:i + batch_size]
        # Format tags as comma-separated @user1, @user2, ...
        tags = ", ".join([f"@{u}" for u in batch if u])
        if not tags.strip():
            continue

        full_message = f"{base_message}\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            # safe delay between each message containing 5 tags
            await asyncio.sleep(8)
        except Exception as e:
            print(f"⚠️ Error sending reminder batch {batch}: {e}")
            await asyncio.sleep(3)

# === MAIN APP ===
async def main():
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # JobQueue setup
    job_queue = app.job_queue
    job_queue.run_repeating(send_reminder, interval=60 * 15, first=10)  # Every 15 minutes

    print("🤖 CR7 Bot is live (Welcome + 5-user inline-tag reminders)...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

# === KEEP-ALIVE SERVER FOR RENDER ===
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Keep-alive server running on port {PORT}")
        httpd.serve_forever()

# === START ===
if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    asyncio.run(main())
