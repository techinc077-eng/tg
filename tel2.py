import os
import asyncio
from datetime import datetime, timedelta
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# =========================
# SETTINGS
# =========================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

# =========================
# DATA STORAGE
# =========================
group_members = set()       # all members in group
already_tagged = set()      # members already tagged in reminders
new_users_queue = set()     # newly joined users awaiting reminder

# =========================
# WELCOME MESSAGE
# =========================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_users = []
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)
        new_users_queue.add(username)
        new_users.append(username)

        # Send welcome photo
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

# =========================
# REMINDER MESSAGE (SMART)
# =========================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    base_message = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top of Sol Trending! 💪⚡  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to Vote & Claim your Reward 👇
"""
    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Merge queued new users with untagged members
    untagged_members = list((group_members - already_tagged) | new_users_queue)
    if not untagged_members:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    batch_size = 5
    for i in range(0, len(untagged_members), batch_size):
        batch = untagged_members[i:i+batch_size]
        tags = ", ".join([f"@{u}" for u in batch])
        full_msg = f"{base_message}\n\n{tags}"

        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=full_msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            # Mark these users as tagged
            already_tagged.update(batch)
            # Remove from the queue so they aren’t double-tagged
            new_users_queue.difference_update(batch)
        except Exception as e:
            print("❌ Reminder error:", e)

        await asyncio.sleep(7)  # anti-spam safe delay

# =========================
# RESET TAGGED USERS AT MIDNIGHT UTC
# =========================
async def reset_at_midnight():
    while True:
        now = datetime.utcnow()
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        await asyncio.sleep((next_midnight - now).total_seconds())
        already_tagged.clear()
        print("🔄 Tagged users reset at midnight UTC")

# =========================
# KEEP-ALIVE WEB SERVER
# =========================
async def handle(request):
    return web.Response(text="Bot running ✅")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web keep-alive running on port {port}")

# =========================
# AUTO-RESTART BOT FOREVER
# =========================
async def run_bot_forever():
    while True:
        try:
            print("🤖 Starting Telegram bot…")
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
            # Smart reminder every 10 minutes
            app.job_queue.run_repeating(send_reminder, interval=600, first=15)
            await app.run_polling(close_loop=False)
        except Exception as e:
            print("❌ BOT CRASHED — Restarting in 5s:", e)
            await asyncio.sleep(5)

# =========================
# MAIN
# =========================
async def main():
    await start_web()
    await asyncio.gather(run_bot_forever(), reset_at_midnight())

if __name__ == "__main__":
    asyncio.run(main())
