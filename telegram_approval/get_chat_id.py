import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

print("🤖 Waiting for a message from you on Telegram...")
print("👉 Go to t.me/Agentic_approval_bot on your phone and say 'hello'")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print("\n" + "="*50)
    print(f"📩 RECEIVED MESSAGE FROM: {message.from_user.username} (@{message.from_user.username})")
    print(f"🔢 YOUR CHAT ID IS: {message.chat.id}")
    print("="*50 + "\n")
    
    bot.reply_to(message, f"I got your message! Your true Telegram Chat ID is: {message.chat.id}")

bot.polling()
