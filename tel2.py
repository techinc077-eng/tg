import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, JobQueue

TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465
group_members = set()


# === WELCOME HANDLER ===
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)

        caption = f"""
🚀 *CR7 FAMILY — IT’S VOTING TIME!* 🐐 

Welcome @{username}! ⚡  
It’s time to unite and vote for CR7 Token! 💪🔥 

✅ **By voting, you’ll earn:**
• 💰 *CR7 Tokens*
• 🎁 *SOL Rewards*

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


# === REMINDER JOB ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for username in list(group_members):
        if not username:
            continue

        message = f"""
📢 *TIME TO RISE CR7 FAMILY!* 🐐 @{username}

Every vote counts — claim your rewards:  
💰 *CR7 Tokens*  
🎁 *SOL Rewards*

👇 Tap below to vote & earn now!
"""
        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await asyncio.sleep(7)
        except Exception as e:
            print(f"Error sending reminder to @{username}: {e}")
            await asyncio.sleep(2)


# === MAIN APP ===
async def main():
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # JobQueue for reminders
    job_queue = app.job_queue
    job_queue.run_repeating(send_reminder, interval=60 * 15, first=10)

    # Webhook setup
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        raise RuntimeError("RENDER_EXTERNAL_URL not set!")

    port = int(os.environ.get("PORT", 8080))
    webhook_url = f"{render_url}/"

    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=webhook_url)

    # This blocks forever — keeps the bot running
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="",
        webhook_url=webhook_url,
    )


if __name__ == "__main__":
    asyncio.run(main())
