import asyncio
import sys
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, JobQueue

# === SETTINGS ===
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465  # Replace with your actual group chat ID

# Store members globally (in-memory)
group_members = set()

# Persistent rotation index file
INDEX_FILE = "last_tag_index.json"

# === Helper functions for persistent rotation ===
def load_last_index():
    try:
        with open(INDEX_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_tag_index", 0)
    except Exception:
        return 0

def save_last_index(index):
    try:
        with open(INDEX_FILE, "w") as f:
            json.dump({"last_tag_index": index}, f)
    except Exception as e:
        print(f"Error saving last_tag_index: {e}")

# Initialize last_tag_index
last_tag_index = load_last_index()

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


# === REMINDER JOB WITH PERSISTENT ROTATION ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    global last_tag_index

    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Main reminder message
    main_message = """
📢*TIME TO RISE CR7 FAMILY!* 🐐

Let’s push CR7 Token straight to the top of the Sol Trending list! 💪⚡ 

Every vote counts — and each one brings you exclusive rewards: 
💰 *CR7 Tokens*
🎁 *SOL Rewards*

Join the movement, claim your rewards, and show the world the power of CR7! 🌍🔥

👇 Tap below to vote & earn now!
"""
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=main_message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    members_list = list(group_members)
    total_users = len(members_list)
    if total_users == 0:
        return

    # Rotate the list starting from last_tag_index
    rotated_list = members_list[last_tag_index:] + members_list[:last_tag_index]

    # Dynamic batch size and delay
    if total_users <= 50:
        batch_size = 5
        delay = 5
    elif total_users <= 200:
        batch_size = 5
        delay = 10
    elif total_users <= 500:
        batch_size = 5
        delay = 15
    else:
        batch_size = 5
        delay = 20

    # Tag users in batches
    for i in range(0, total_users, batch_size):
        batch = rotated_list[i:i + batch_size]
        tags = " ".join([f"@{u}" for u in batch if u])
        if tags.strip():
            try:
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"🔔VOTE NOW! \n{tags}",
                    disable_notification=True
                )
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Error sending batch {batch}: {e}")
                await asyncio.sleep(5)

    # Update last_tag_index and save persistently
    last_tag_index = (last_tag_index + batch_size) % total_users
    save_last_index(last_tag_index)


# === MAIN APP WITH AUTO-RESTART ===
async def main():
    while True:  # Auto-restart loop
        try:
            app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

            # JobQueue for reminders
            job_queue = app.job_queue
            job_queue.run_repeating(send_reminder, interval=60 * 15, first=10)

            print("🤖 CR7 Bot is live and polling for updates...")
            await app.run_polling()
        except Exception as e:
            print(f"⚠️ Bot crashed: {e}. Restarting in 5 seconds...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("🛑 Bot stopped manually.")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
