from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import JobQueue
import asyncio

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
🚀 **CR7 FAMILY — IT’S VOTING TIME!** 🐐 

Welcome @{username}! ⚡  
It’s time to unite and vote for CR7 Token, let’s push our project to the top of the trending list! 💪🔥 

✅ By voting, you’ll earn:
• 💰 **CR7 Tokens**
• 🎁 **SOL Rewards**

Let’s show the world the unstoppable power of the CR7 Community! 🌍💫
👇 **Tap below to cast your vote & claim your rewards!**
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


# === REMINDER JOB WITH TAGGING ===
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

    # Send main reminder message
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    # Tag users in batches of 20
    members_list = list(group_members)
    batch_size = 20

    for i in range(0, len(members_list), batch_size):
        batch = members_list[i:i + batch_size]
        tags = " ".join([f"@{u}" for u in batch if u])
        if tags.strip():
            try:
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"🔔 Reminder for our loyal members:\n{tags}",
                    disable_notification=True
                )
                await asyncio.sleep(5)  # slight delay to avoid spam
            except Exception as e:
                print(f"Error tagging batch: {e}")


# === MAIN APP ===
async def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Initialize JobQueue
    job_queue = app.job_queue
    if job_queue is None:
        job_queue = JobQueue()
        job_queue.set_application(app)
        job_queue.start()

    # Run hourly reminders
    job_queue.run_repeating(send_reminder, interval=60 * 60 * 1, first=10)

    print("🤖 CR7 Bot is live and sending hourly reminders with tags...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()  # keeps the process alive forever


if __name__ == "__main__":
    asyncio.run(main())
