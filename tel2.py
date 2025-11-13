import asyncio
import sys
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# === SETTINGS ===
TOKEN = "7571535805:AAGDJBJqzuytpjpce9ivNG6eAUaRTYeQBuY"
VOTE_LINK = "cr7.soltrendingvote.top"
IMAGE_URL = "https://icohtech.ng/cr7.jpg"
GROUP_CHAT_ID = -1003295107465  # Replace with your actual group chat ID

# Persistent files
MEMBERS_FILE = "group_members.json"
INDEX_FILE = "last_tag_index.json"

# === HELPER FUNCTIONS FOR PERSISTENCE ===
def load_members():
    try:
        with open(MEMBERS_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("members", []))
    except Exception:
        return set()

def save_members():
    try:
        with open(MEMBERS_FILE, "w") as f:
            json.dump({"members": list(group_members)}, f)
    except Exception as e:
        print(f"Error saving group_members: {e}")

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

# Load persistent data
group_members = load_members()
last_tag_index = load_last_index()

# === WELCOME MESSAGE HANDLER ===
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global group_members
    for member in update.message.new_chat_members:
        username = member.username or member.first_name
        group_members.add(username)
        save_members()  # Save immediately

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

# === FUNCTION TO PRUNE INACTIVE USERS ===
async def prune_inactive_members(context: ContextTypes.DEFAULT_TYPE):
    global group_members
    try:
        chat = await context.bot.get_chat(GROUP_CHAT_ID)
        current_members = set()
        async for member in chat.get_members():
            if member.user.username:
                current_members.add(member.user.username)

        removed = group_members - current_members
        if removed:
            group_members.intersection_update(current_members)
            save_members()
            print(f"Pruned inactive members: {removed}")
        return removed
    except Exception as e:
        print(f"Error pruning inactive members: {e}")
        return set()

# === MANUAL /PRUNE COMMAND ===
async def manual_prune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_member = await context.bot.get_chat_member(GROUP_CHAT_ID, user.id)
    if chat_member.status not in ("administrator", "creator"):
        await update.message.reply_text("❌ Only admins can run this command.")
        return

    removed = await prune_inactive_members(context)
    if removed:
        await update.message.reply_text(f"✅ Pruned inactive members: {', '.join(removed)}")
    else:
        await update.message.reply_text("✅ No inactive members to prune.")

# === NEW /MEMBERS COMMAND ===
async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_member = await context.bot.get_chat_member(GROUP_CHAT_ID, user.id)
    if chat_member.status not in ("administrator", "creator"):
        await update.message.reply_text("❌ Only admins can run this command.")
        return

    if not group_members:
        await update.message.reply_text("No members are currently tracked.")
        return

    members_list = sorted(group_members)
    # Telegram messages have a max length, split if necessary
    chunk_size = 50
    for i in range(0, len(members_list), chunk_size):
        chunk = members_list[i:i+chunk_size]
        await update.message.reply_text("Tracked members:\n" + "\n".join(f"@{m}" for m in chunk))

# === REMINDER JOB WITH FULL PERSISTENCE AND CLEANUP ===
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    global last_tag_index

    # Prune inactive members automatically
    await prune_inactive_members(context)

    keyboard = [[InlineKeyboardButton("🗳️ VOTE $CR7", url=VOTE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

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

    rotated_list = members_list[last_tag_index:] + members_list[:last_tag_index]

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

    last_tag_index = (last_tag_index + batch_size) % total_users
    save_last_index(last_tag_index)

# === MAIN APP WITH PROPER AUTO-RESTART ===
async def main():
    while True:
        app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
        try:
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
            app.add_handler(CommandHandler("prune", manual_prune))
            app.add_handler(CommandHandler("members", show_members))
            job_queue = app.job_queue
            job_queue.run_repeating(send_reminder, interval=60 * 15, first=10)

            print("🤖 CR7 Bot is live and polling for updates...")
            await app.run_polling()
        except Exception as e:
            print(f"⚠️ Bot crashed: {e}. Restarting in 5 seconds...")
            await app.shutdown()
            await app.stop()
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("🛑 Bot stopped manually.")
            await app.shutdown()
            await app.stop()
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
