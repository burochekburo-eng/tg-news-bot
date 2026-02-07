import feedparser
import requests
import os
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru"
]

# Простая очистка HTML тегов и сущностей
def clean_html(raw_html):
    clean_text = re.sub(r'<[^>]+>', '', raw_html)  # удаляем теги
    clean_text = clean_text.replace("&nbsp;", " ").replace("&amp;", "&")
    return clean_text.strip()

def send_to_telegram_photo(caption, photo_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption
    }
    r = requests.post(url, data=payload)
    print("Telegram response:", r.text)

def send_to_telegram_message(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": caption, "disable_web_page_preview": False}
    r = requests.post(url, json=payload)
    print("Telegram response:", r.text)

# Берём самую свежую новость
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

    # Берём картинку из RSS, если есть
    photo_url = None
    if "media_content" in latest_entry and len(latest_entry.media_content) > 0:
        photo_url = latest_entry.media_content[0]["url"]
    elif "enclosures" in latest_entry and len(latest_entry.enclosures) > 0:
        photo_url = latest_entry.enclosures[0]["href"]

    caption = f"🔥 {title}\n\n{summary}\n\nИсточник: {link}"

    if photo_url:
        send_to_telegram_photo(caption, photo_url)
    else:
        send_to_telegram_message(caption)
