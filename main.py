import feedparser
import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru"
]

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def send_to_telegram_message(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": caption, "disable_web_page_preview": False}
    r = requests.post(url, json=payload)
    print("Telegram response:", r.text)

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
