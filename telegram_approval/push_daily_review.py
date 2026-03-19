import os
import sys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import list_firebase_posts

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_post_message(post):
    """Formats the Firebase post for Telegram."""
    title = post.get('title', 'Untitled')
    score = post.get('score', 'N/A')
    url = post.get('url', '')
    content = post.get('final_post', '')
    
    msg = (
        f"🌟 *DAILY CONTENT REVIEW*\n"
        f"🎯 *Top Score:* {score}/100\n"
        f"🗞️ *Src:* [{title}]({url})\n\n"
        f"------------------------------\n"
        f"{content}"
    )
    return msg

def push_approval_request():
    """
    Fetches the best article and pushes it to your phone with buttons.
    Requires approval_bot.py to be running to handle the button clicks.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
        return

    bot = telebot.TeleBot(BOT_TOKEN)
    
    print("🔍 Fetching best NOT_POSTED article...")
    # Fetch just the top one for the notification
    posts = list_firebase_posts(status_filter="NOT_POSTED", limit=1)
    
    if not posts:
        print("📭 No articles at all in Firebase!")
        return

    post = posts[0]
    
    # Create the Interactive Buttons (Stateless via prefixes)
    prefix = post["article_id"][:16]
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"apr:{prefix}"),
        InlineKeyboardButton("⏭️ Next", callback_data=f"nxt:{prefix}"),
    )
    markup.add(
        InlineKeyboardButton("🗑️ Reject", callback_data=f"rej:{prefix}"),
        InlineKeyboardButton("⬅️ Prev", callback_data=f"prv:{prefix}"),
    )
    markup.add(
        InlineKeyboardButton("🛑 Stop", callback_data="stop")
    )
    
    message = get_post_message(post)
    if len(message) > 4000:
        message = message[:4000] + "...\n(Truncated)"
        
    print(f"🚀 Pushing Daily Review to your Telegram...")
    try:
        bot.send_message(
            CHAT_ID, 
            message, 
            reply_markup=markup, 
            parse_mode="Markdown", 
            disable_web_page_preview=True
        )
        print("✅ Success! Check your phone.")
        print("\n💡 NOTE: Make sure 'python telegram_approval/approval_bot.py' is running in a background terminal so you can click the buttons!")
    except Exception as e:
        print(f"❌ Failed to push message: {e}")

if __name__ == "__main__":
    push_approval_request()
