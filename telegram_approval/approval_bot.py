import os
import sys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path so we can import from firebase_publishing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import update_post_status, list_firebase_posts

# Telegram config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# We store the active session context for each user
# Format: { "chat_id_str": {"posts": [post_dict_1, post_dict_2, ...], "current_index": 0} }
user_sessions = {}

def get_post_message(post):
    """Formats the Firebase post beautifully for Telegram's Markdown."""
    title = post.get('title', 'Untitled')
    score = post.get('score', 'N/A')
    url = post.get('url', '')
    content = post.get('final_post', '')
    
    msg = (
        f"📝 *NEW POST FOR REVIEW*\n"
        f"🎯 *Score:* {score}/100\n"
        f"🗞️ *Src:* [{title}]({url})\n\n"
        f"------------------------------\n"
        f"{content}"
    )
    return msg

def send_next_post(chat_id_str):
    """Fetches the next highest scored NOT_POSTED article from local session and sends it."""
    session = user_sessions.get(chat_id_str)
    
    # If no session or we reached the end of the loaded batch, fetch a fresh batch
    if not session or session["current_index"] >= len(session["posts"]):
        posts = list_firebase_posts(status_filter="NOT_POSTED", limit=10)
        
        if not posts:
            bot.send_message(chat_id_str, "📭 No more `NOT_POSTED` articles left in Firebase!")
            if chat_id_str in user_sessions:
                del user_sessions[chat_id_str]
            return
            
        user_sessions[chat_id_str] = {"posts": posts, "current_index": 0}
        session = user_sessions[chat_id_str]

    # Get the post at the current index
    post = session["posts"][session["current_index"]]
    
    # Create the Interactive Buttons
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data="approve"),
        InlineKeyboardButton("⏭️ Show Next", callback_data="skip"),
    )
    markup.add(
        InlineKeyboardButton("🗑️ Reject", callback_data="reject"),
        InlineKeyboardButton("🛑 Stop Reviewing", callback_data="stop")
    )
    
    message = get_post_message(post)
    
    # Telegram has a 4096 character limit
    if len(message) > 4000:
        message = message[:4000] + "...\n(Truncated)"
        
    bot.send_message(
        chat_id_str, 
        message, 
        reply_markup=markup, 
        parse_mode="Markdown", 
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['start', 'review'])
def handle_review(message):
    """Triggered when you type /start or /review in Telegram"""
    chat_id_str = str(message.chat.id)
    
    # Ensure nobody else can use your bot
    if ALLOWED_CHAT_ID != "YOUR_CHAT_ID" and chat_id_str != str(ALLOWED_CHAT_ID):
        bot.reply_to(message, "⛔ You are not authorized to use this bot.")
        return
        
    bot.send_message(chat_id_str, "🔍 Searching Firebase for the next best posts...")
    send_next_post(chat_id_str)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Triggered when you press one of the inline buttons"""
    chat_id_str = str(call.message.chat.id)
    
    session = user_sessions.get(chat_id_str)
    
    # If a button is clicked but no session exists (e.g. from a push script)
    # create a fresh session on the fly.
    if not session:
        posts = list_firebase_posts(status_filter="NOT_POSTED", limit=10)
        if not posts:
            bot.answer_callback_query(call.id, "No articles found in Firebase.")
            return
        user_sessions[chat_id_str] = {"posts": posts, "current_index": 0}
        session = user_sessions[chat_id_str]
        
    # Boundary check for existing sessions
    if session["current_index"] >= len(session["posts"]):
        bot.answer_callback_query(call.id, "Session expired. Type /review to start over.")
        return

    current_post = session["posts"][session["current_index"]]
    article_id = current_post["article_id"]
    
    if call.data == "approve":
        # Final approval: This will trigger the Google Sheet publisher
        success = update_post_status(article_id, "QUEUED")
        if success:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(chat_id_str, "🚀 *Post Approved!* I've sent it to the factory for publishing in Google Sheets.", parse_mode="Markdown")
            # End the session for today as requested
            if chat_id_str in user_sessions:
                del user_sessions[chat_id_str]
        else:
            bot.answer_callback_query(call.id, "❌ Firebase update failed.")
            
    elif call.data == "skip":
        # SKIP: Leave it in Firebase as NOT_POSTED. Just move to next.
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(chat_id_str, "⏭️ *Post Skipped.* Keeping this in the queue for later!", parse_mode="Markdown")
        session["current_index"] += 1
        send_next_post(chat_id_str)
        
    elif call.data == "reject":
        # REJECT: Move to trash database
        success = update_post_status(article_id, "REJECTED")
        if success:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(chat_id_str, "🗑️ *Post Rejected.* Removed from the main queue.", parse_mode="Markdown")
            session["current_index"] += 1
            send_next_post(chat_id_str)
        else:
            bot.answer_callback_query(call.id, "❌ Firebase update failed.")
            
    elif call.data == "stop":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(chat_id_str, "🛑 Review session stopped. Type /review whenever you want to start again.")
        if chat_id_str in user_sessions:
            del user_sessions[chat_id_str]


if __name__ == "__main__":
    print("🤖 Telegram Approval Bot is running!")
    print("Waiting for /review command...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error running bot: {e}")
