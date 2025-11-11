from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import JobQueue
import asyncio

# === SETTINGS ===
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "cr7.soltrendingvote.top"
IMAGE_URL = "https://i.imgur.com/V4PD9LU.jpeg"
GROUP_CHAT_ID = -1003295107465  # Replace with your actual group chat ID

# === WELCOME MESSAGE HANDLER ===
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or member.first_name

        caption = f"""
🐐 *CR7 FAMILY IT’S VOTING TIME!*  

Welcome @{username}! ⚡  
We’re calling on every member of the community to vote for **CR7 Token** and help push us to the top of the trending list! 💪⚡  

By casting your vote, you not only support the project, you also earn rewards:  
💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

Let’s show the world the power of the CR7 community! 🌍🔥  
⭐ *Vote now and secure your rewards!*
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

# === HOURLY REMINDER JOB ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = """
📢 *CR7 FAMILY HOURLY REMINDER!*  

It’s time again to boost **CR7 Token** to the top of the Sol Trending list! 💪⚡  

Each vote brings us closer to victory and you earn:  
💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

Tap below to cast your vote now and claim your rewards in the CR7 movement! 🌍🔥  
#VoteToEarn
"""
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# === MAIN APP ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

  # === MAIN APP ===
async def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Initialize JobQueue manually (for reminders)
    job_queue = app.job_queue
    if job_queue is None:
        from telegram.ext import JobQueue
        job_queue = JobQueue()
        job_queue.set_application(app)
        job_queue.start()

    # Run hourly reminders
    job_queue.run_repeating(send_reminder, interval=60 * 60 * 1, first=10)

    print("🤖 CR7 Bot is live and sending hourly reminders...")

    # Keep bot alive
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()  # keeps the process alive forever

if __name__ == "__main__":
    asyncio.run(main())
