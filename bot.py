import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import telebot
import re
import os

# Configuration
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBSITE_URL = "https://samthegoat007.github.io/mafia-chess/"

bot = telebot.TeleBot(TOKEN)

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
        t_time_raw, t_link = extract_tournament_details(response.text)

        if t_time_raw:
            # Baghdad Time Zone (UTC+3)
            baghdad_tz = timezone(timedelta(hours=3))
            t_time = t_time_raw.replace(tzinfo=baghdad_tz)
            now = datetime.now(baghdad_tz)
            
            diff = t_time - now
            total_seconds = int(diff.total_seconds())

            if total_seconds > 0:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                
                intro = "انا بوت المافيا 🕵️‍♂️"
                status = f"Next Tournament in: *{hours} hours and {minutes} minutes*"
                link = f"🔗 [Tournament Link]({t_link if t_link else WEBSITE_URL})"
                
                # --- LOGIC CHANGE HERE ---
                
                # 1. IF LESS THAN 1 HOUR: SEND MENTION/PIN
                if hours == 0:
                    msg = f"🚨 *FINAL WARNING - MENTION ALL* 🚨\n\n{intro}\n{status}\n{link}\n\nJoin now! 🔥"
                    sent_msg = bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                    try:
                        # This notifies everyone even if they are muted
                        bot.pin_chat_message(CHAT_ID, sent_msg.message_id, disable_notification=False)
                    except:
                        print("Bot needs Admin rights to pin!")
                
                # 2. IF MORE THAN 1 HOUR: JUST SEND REGULAR MESSAGE (NO PIN/MENTION)
                else:
                    msg = f"🕒 *MAFIA STATUS REPORT*\n\n{intro}\n{status}\n{link}"
                    # disable_notification=True makes it a silent message for regular updates
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown', disable_notification=True)
            else:
                print("Tournament already started.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
