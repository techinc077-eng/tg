import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from aiohttp import web

# ==============================
#  SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465  # Your group ID

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

    if not members:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=base_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    # Send batches of 5 users tagged per message
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

        await asyncio.sleep(7)  # anti-spam delay

# ==============================
#  KEEP-ALIVE WEB SERVER
# ==============================
async def handle(request):
    return web.Response(text="Bot OK — Running")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web keep-alive server active on port {port}")

# ==============================
#  BOT START / AUTO-RESTART
# ==============================
async def run_bot_forever():
    while True:
        try:
            print("🤖 Starting Telegram bot…")
            application = ApplicationBuilder().token(TOKEN).build()
            application.add_handler(
                MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
            )

            # Repeating reminder every 10 minutes
            application.job_queue.run_repeating(send_reminder, interval=600, first=15)

            # Run bot polling (blocking)
            await application.run_polling(close_loop=False)

        except Exception as e:
            print("❌ BOT CRASHED — Restarting in 5s:", e)

        await asyncio.sleep(5)  # delay before auto-restart

# ==============================
#  MAIN
# ==============================
async def main():
    # Start web server
    await start_web()
    # Start bot
    await run_bot_forever()

if __name__ == "__main__":
    asyncio.run(main())
