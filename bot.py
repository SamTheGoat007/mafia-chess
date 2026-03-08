import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import telebot
import re
import os
import threading  # Required to run two things at once
import time       # Required for the 1-hour wait

# Get secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBSITE_URL = "https://samthegoat007.github.io/mafia-chess/"

bot = telebot.TeleBot(TOKEN)

# --- 1. REPLIES TO MENTIONS ---
@bot.message_handler(func=lambda message: True)
def reply_to_mention(message):
    bot_info = bot.get_me()
    # Responds if tagged or in private DM
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
                bot.send_message(CHAT_ID, f"🕒 *MAFIA CHESS*\nStarts in ~3 hours!", parse_mode='Markdown')
            elif timedelta(minutes=0) < time_until <= timedelta(hours=1):
                bot.send_message(CHAT_ID, f"🚨 *ONE HOUR WARNING*\n🔗 [LINK]({t_link})", parse_mode='Markdown')
    except Exception as e:
        print(f"Error: {e}")

# --- 2. THE BACKGROUND LOOP ---
def background_monitor():
    while True:
        run_check()
        time.sleep(3600)  # Wait exactly 1 hour before checking again

# --- 3. START EVERYTHING ---
if __name__ == "__main__":
    # This starts the website checker in the background
    checker_thread = threading.Thread(target=background_monitor)
    checker_thread.daemon = True 
    checker_thread.start()

    print("Bot is now running forever...")
    # This is the "Magic" line that keeps the script from ending
    bot.infinity_polling()
