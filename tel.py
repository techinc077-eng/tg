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
VOTE_LINK = "cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465  # Replace with your actual group chat ID

# Store members globally (in-memory)
group_members = set()


# === WELCOME MESSAGE HANDLER ===
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)

        caption = f"""
🚀 *CR7 FAMILY — IT’S VOTING TIME!* 🐐 

Welcome @{username}! ⚡  
It’s time to unite and vote for CR7 Token, let’s push our project to the top of the trending list! 💪🔥 

✅ **By voting, you’ll earn:**
• 💰 *CR7 Tokens*
• 🎁 *SOL Rewards*

Let’s show the world the unstoppable power of the CR7 Community! 🌍💫

👇 *Tap below to cast your vote & claim your rewards!*
"""

        keyboard = [
            [InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# === REMINDER JOB WITH INDIVIDUAL TAGGING ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    members_list = list(group_members)

    if not members_list:
        print("No members found for reminder.")
        return

    print(f"Sending reminder to {len(members_list)} members...")

    for username in members_list:
        if not username:
            continue

        message = f"""
📢 *TIME TO RISE CR7 FAMILY!* 🐐 @{username}

Let’s push CR7 Token straight to the top of the Sol Trending list! 💪⚡  

Each vote brings you closer to your rewards:  
💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

Join the movement, claim your rewards, and show the world the power of CR7! 🌍🔥  

👇 Tap below to vote & earn now!
"""

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await asyncio.sleep(7)  # Wait 7 seconds between each mention (safe delay)
        except Exception as e:
            print(f"Error sending reminder to @{username}: {e}")
            await asyncio.sleep(2)  # small pause before continuing

# === MAIN APP ===
async def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # JobQueue for reminders
    job_queue = app.job_queue
    if job_queue is None:
        job_queue = JobQueue()
        job_queue.set_application(app)
        job_queue.start()

    job_queue.run_repeating(send_reminder, interval=60 * 15, first=10)

    print("🤖 CR7 Bot running via webhook...")

    await app.initialize()
    await app.start()

    # ✅ Use webhook instead of polling
    PORT = int(os.environ.get("PORT", 8080))
    await app.bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_URL']}/")
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_URL']}/"
    )



# === KEEP-ALIVE SERVER (for Render or Replit) ===
def keep_alive():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Keep-alive server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()


if __name__ == "__main__":
    asyncio.run(main())
