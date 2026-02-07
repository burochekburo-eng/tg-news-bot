import feedparser
import requests
import os
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru"
]

# Простая очистка HTML тегов
def clean_html(raw_html):
    # удаляем все теги
    clean_text = re.sub(r'<[^>]+>', '', raw_html)
    # заменяем HTML сущности
    clean_text = clean_text.replace("&nbsp;", " ").replace("&amp;", "&")
    return clean_text.strip()

def send_to_telegram_message(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": caption, "disable_web_page_preview": False}
    r = requests.post(url, json=payload)
    print("Telegram response:", r.text)

# Берём только одну самую свежую новость
latest_entry = None
for rss in RSS_FEEDS:
    feed = feedparser.parse(rss)
    if not feed.entries:
        continue
    entry = feed.entries[0]
    if latest_entry is None or entry.published_parsed > latest_entry.published_parsed:
        latest_entry = entry

if latest_entry:
    title = clean_html(latest_entry.title)
    link = latest_entry.link
    summary = clean_html(latest_entry.summary)

    caption = f"🔥 {title}\n\n{summary}\n\nИсточник: {link}"
    send_to_telegram_message(caption)
