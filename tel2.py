import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

# ==============================
# SETTINGS
# ==============================
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "https://cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465

# Track group users
group_members = set()

# ==============================
# WELCOME HANDLER
# ==============================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)

        caption = f"""
🚨 *CR7 FAMILY — NOW OR NEVER!* 🐐🔥

@{username}, *Your vote = Rewards.*
$CR7 is climbing Sol Trending and we need every vote RIGHT NOW.

*Vote Now → Claim $SOL + $CR7 token reward. No wait. No delay.
Claim it the moment you vote.*

This is your window, don’t miss it.
Tap Below, *Vote, Secure your Reward,* and Push $CR7 to the top! ⚡🚀
"""
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
        )

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=button
        )

# ==============================
# REMINDER HANDLER
# ==============================
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):

    base_msg = """🔥 *CR7 FAMILY — THIS IS YOUR MOMENT!* ⚡🐐 

$CR7 is surging, but we need your vote RIGHT NOW to lock our spot on Sol Trending.

💰*Vote Now → Claim instant $SOL + $CR7 token reward.*🎁
*Miss it → You lose the drop.*

Don’t wait. Don’t think.
Tap below to *Vote and Claim your Reward* before it’s gone. 🚀💰
"""

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    )

    members = list(group_members)
    batch_size = 5

    # No tags yet? Send only base message
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
        tags = ", ".join(f"@{u}" for u in batch)

        msg = f"{base_msg}\n\n{tags}"

        try:
            await context.bot.send_message(
                GROUP_CHAT_ID,
                msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("❌ Reminder error:", e)

        await asyncio.sleep(6)  # flood-safe delay

# ==============================
# MAIN BOT LOOP (FOREVER)
# ==============================
def main():
    print("🤖 CR7 Bot starting (Worker mode, runs forever)...")

    app = ApplicationBuilder().token(TOKEN).build()

    # Welcome messages
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Reminders every 10 minutes
    app.job_queue.run_repeating(send_reminder, interval=600, first=20)

    # Worker: Run polling forever
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
