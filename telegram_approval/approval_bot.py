import os
import sys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path so we can import from firebase_publishing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import update_post_status, list_firebase_posts, find_article_by_prefix

# Telegram config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# We store the active session context for each user
user_sessions = {}

def get_post_message(post):
    """Formats the Firebase post beautifully for Telegram's Markdown."""
    title = post.get('title', 'Untitled')
    score = post.get('score', 'N/A')
    url = post.get('url', '')
    content = post.get('final_post', '')
    
    msg = (
        f"📝 *CONTENT REVIEW*\n"
        f"🎯 *Score:* {score}/100\n"
        f"🗞️ *Src:* [{title}]({url})\n\n"
        f"------------------------------\n"
        f"{content}"
    )
    return msg

def get_post_markup(article_id):
    """Creates the stateless Interactive Buttons with embedded ID prefix."""
    prefix = article_id[:16]
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
    return markup

def send_post_by_index(chat_id_str, index):
    """Sends the post at a specific index in the current session."""
    session = user_sessions.get(chat_id_str)
    if not session or index < 0 or index >= len(session["posts"]):
        bot.send_message(chat_id_str, "🛑 End of queue or invalid navigation. Type /review to refresh.")
        return

    session["current_index"] = index
    post = session["posts"][index]
    
    markup = get_post_markup(post["article_id"])
    message = get_post_message(post)
    
    if len(message) > 4000:
        message = message[:4000] + "...\n(Truncated)"
        
    bot.send_message(
        chat_id_str, 
        message, 
        reply_markup=markup, 
        parse_mode="Markdown", 
        disable_web_page_preview=True
    )

def send_next_post(chat_id_str):
    """Starter for /review command."""
    posts = list_firebase_posts(status_filter="NOT_POSTED", limit=20)
    if not posts:
        bot.send_message(chat_id_str, "📭 No `NOT_POSTED` articles left in Firebase!")
        return
        
    user_sessions[chat_id_str] = {"posts": posts, "current_index": 0}
    send_post_by_index(chat_id_str, 0)

@bot.message_handler(commands=['start', 'review'])
def handle_review(message):
    chat_id_str = str(message.chat.id)
    if ALLOWED_CHAT_ID and chat_id_str != str(ALLOWED_CHAT_ID):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.send_message(chat_id_str, "🔍 Fetching latest queue...")
    send_next_post(chat_id_str)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id_str = str(call.message.chat.id)
    data = call.data

    if data == "stop":
        bot.edit_message_reply_markup(chat_id_str, call.message.message_id, reply_markup=None)
        bot.send_message(chat_id_str, "🛑 Stopped. Type /review to restart.")
        return

    if ":" not in data:
        return

    action, prefix = data.split(":")
    
    # Resolve the article from prefix for statelessness
    article = find_article_by_prefix(prefix)
    if not article:
        bot.answer_callback_query(call.id, "❌ Article no longer found in Firebase.")
        return

    article_id = article["article_id"]

    # Helper function to ensure we have a session to navigate from
    def get_session():
        if chat_id_str not in user_sessions:
            posts = list_firebase_posts(status_filter="NOT_POSTED", limit=20)
            user_sessions[chat_id_str] = {"posts": posts, "current_index": 0}
        return user_sessions[chat_id_str]

    if action == "apr":
        success = update_post_status(article_id, "QUEUED")
        if success:
            bot.edit_message_reply_markup(chat_id_str, call.message.message_id, reply_markup=None)
            bot.send_message(chat_id_str, f"🚀 *Approved:* {article['title'][:50]}...", parse_mode="Markdown")
            
            # Find next in session
            session = get_session()
            try:
                curr_idx = next(i for i, p in enumerate(session["posts"]) if p["article_id"] == article_id)
                send_post_by_index(chat_id_str, curr_idx + 1)
            except StopIteration:
                send_next_post(chat_id_str) # Restart queue if not found
        else:
            bot.answer_callback_query(call.id, "❌ Update failed.")

    elif action == "rej":
        success = update_post_status(article_id, "REJECTED")
        if success:
            bot.edit_message_reply_markup(chat_id_str, call.message.message_id, reply_markup=None)
            bot.send_message(chat_id_str, "🗑️ Post Rejected.", parse_mode="Markdown")
            
            # Find next in session
            session = get_session()
            try:
                curr_idx = next(i for i, p in enumerate(session["posts"]) if p["article_id"] == article_id)
                send_post_by_index(chat_id_str, curr_idx + 1)
            except StopIteration:
                send_next_post(chat_id_str)
        else:
            bot.answer_callback_query(call.id, "❌ Update failed.")

    elif action == "nxt":
        bot.edit_message_reply_markup(chat_id_str, call.message.message_id, reply_markup=None)
        session = get_session()
        try:
            curr_idx = next(i for i, p in enumerate(session["posts"]) if p["article_id"] == article_id)
            send_post_by_index(chat_id_str, curr_idx + 1)
        except StopIteration:
            send_next_post(chat_id_str)

    elif action == "prv":
        bot.edit_message_reply_markup(chat_id_str, call.message.message_id, reply_markup=None)
        session = get_session()
        try:
            curr_idx = next(i for i, p in enumerate(session["posts"]) if p["article_id"] == article_id)
            send_post_by_index(chat_id_str, curr_idx - 1)
        except StopIteration:
            # If not in current list, just show first
            send_post_by_index(chat_id_str, 0)


if __name__ == "__main__":
    print("🤖 Telegram Approval Bot is running!")
    print("Waiting for /review command...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error running bot: {e}")
