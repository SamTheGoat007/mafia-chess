import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import telebot
import re
import os

# Get secrets from GitHub Environment
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBSITE_URL = "https://samthegoat007.github.io/mafia-chess/"

bot = telebot.TeleBot(TOKEN)

# --- NEW: Handler for mentions ---
@bot.message_handler(func=lambda message: True)
def reply_to_mention(message):
    # This checks if the bot's username is mentioned in the text
    # Or if it's a private message to the bot
    bot_info = bot.get_me()
    if f"@{bot_info.username}" in message.text or message.chat.type == "private":
        bot.reply_to(message, "انا بوت المافيا 🕵️‍♂️")

def extract_tournament_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    page_text = soup.get_text()
    date_pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}'
    date_match = re.search(date_pattern, page_text)
    link_tag = soup.find('a', href=re.compile(r'chess\.com/(tournament|live)'))
    t_time = datetime.strptime(date_match.group(), "%Y-%m-%d %H:%M") if date_match else None
    t_link = link_tag['href'] if link_tag else None
    return t_time, t_link

def run_check():
    try:
        response = requests.get(WEBSITE_URL, timeout=15)
        t_time, t_link = extract_tournament_details(response.text)

        if t_time and t_link:
            now = datetime.now()
            time_until = t_time - now
            
            if timedelta(hours=2) < time_until <= timedelta(hours=3):
                msg = f"🕒 *MAFIA CHESS REPORT*\nStarts in ~3 hours!\n📅 {t_time.strftime('%B %d, %H:%M')}"
                bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            
            elif timedelta(minutes=0) < time_until <= timedelta(hours=1):
                msg = f"🚨 *ONE HOUR WARNING*\nJoin now!\n🔗 [LINK]({t_link})"
                bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
    except Exception as e:
        print(f"Error checking website: {e}")

if __name__ == "__main__":
    # 1. Run the tournament check once
    run_check()
    
    # 2. Start listening for messages (mentions)
    print("Bot is listening...")
    bot.infinity_polling()
