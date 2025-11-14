import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from aiohttp import web

# ==========================================
# CONFIG
# ==========================================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
GROUP_CHAT_ID = -1003295107465
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"

group_members = set()

# ==========================================
# WELCOME HANDLER
# ==========================================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

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
        btn = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(btn)
        )

# ==========================================
# REMINDER HANDLER
# ==========================================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):

    base_msg = """📢 *TIME TO RISE CR7 FAMILY!* 🐐  

Let’s push CR7 Token straight to the top of Sol Trending! 💪⚡  

💰 *CR7 Tokens*  
🎁 *SOL Rewards*  

🔥 Tap below to Vote & Claim your Reward 👇
"""

    btn = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(btn)

    members = list(group_members)
    batch_size = 5

    if not members:
        await context.bot.send_message(
            GROUP_CHAT_ID,
            base_msg,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return

    for i in range(0, len(members), batch_size):
        batch = members[i:i + batch_size]
        tags = ", ".join([f"@{u}" for u in batch])

        full_msg = f"{base_msg}\n\n{tags}"

        try:
            await context.bot.send_message(
                GROUP_CHAT_ID,
                full_msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("❌ Reminder error:", e)

        await asyncio.sleep(6)


# ==========================================
# AIOHTTP WEBHOOK SERVER
# ==========================================
async def webhook_handler(request):
    data = await request.json()
    await request.app["bot_app"].update_queue.put(data)
    return web.Response(text="OK")

async def start_webhook(app):
    server = web.Application()
    server["bot_app"] = app
    server.router.add_post("/", webhook_handler)

    runner = web.AppRunner(server)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)

    print(f"🌐 Webhook listening on port {port}")
    await site.start()


# ==========================================
# MAIN APP (WEBHOOK MODE)
# ==========================================
async def main():

    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not external_url:
        raise Exception("❌ Set env variable RENDER_EXTERNAL_URL in Render settings!")

    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLERS
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # 🔥 REMINDER EVERY 10 MINUTES
    app.job_queue.run_repeating(send_reminder, interval=600, first=20)

    # Start webhook
    await app.bot.set_webhook(url=f"{external_url}/")
    print("🔗 Webhook set to:", f"{external_url}/")

    await start_webhook(app)
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # Needed for internal async queue

    print("🤖 BOT RUNNING — Webhook mode ACTIVE")

    await asyncio.Event().wait()  # Keep alive forever


# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    asyncio.run(main())
