import os
import sys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path so we can import from firebase_publishing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import get_next_post_to_publish

# Telegram config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


bot = telebot.TeleBot(BOT_TOKEN)

def send_first_post():
    print(f"🔍 Fetching the best NOT_POSTED article from Firebase...")
    post = get_next_post_to_publish()
    
    if not post:
        print("📭 No NOT_POSTED articles left in Firebase!")
        return

    title = post.get('title', 'Untitled')
    score = post.get('score', 'N/A')
    url = post.get('url', '')
    content = post.get('final_post', '')
    
    message = (
        f"📝 *TEST: DIRECT PUSH*\n"
        f"🎯 *Score:* {score}/100\n"
        f"🗞️ *Src:* [{title}]({url})\n\n"
        f"------------------------------\n"
        f"{content}"
    )
    
    if len(message) > 4000:
        message = message[:4000] + "...\n(Truncated)"
        
    print(f"🚀 Sending message to Chat ID {CHAT_ID}...")
    
    try:
        bot.send_message(
            chat_id=CHAT_ID, 
            text=message, 
            parse_mode="Markdown", 
            disable_web_page_preview=True
        )
        print("✅ Message successfully sent to Telegram!")
        print("Note: The article is still in 'NOT_POSTED' status in Firebase.")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        print("\nIMPORTANT: If you got an 'Unauthorized' or 'chat not found' error,")
        print("it means you haven't started a conversation with the bot yet.")
        print("👉 Go to t.me/Agentic_approval_bot on your phone and click 'Start', then run this again!")

if __name__ == "__main__":
    send_first_post()
