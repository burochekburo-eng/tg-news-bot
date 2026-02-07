import feedparser
import requests
import os
import re
from newspaper import Article

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru"
]

MAX_TEXT_LENGTH = 1200  # оптимально для Telegram

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    return clean_text(article.text)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

# --- Получаем самую свежую новость ---
latest_entry = None

for rss in RSS_FEEDS:
    feed = feedparser.parse(rss)
    if not feed.entries:
        continue

    entry = feed.entries[0]

    if latest_entry is None or entry.published_parsed > latest_entry.published_parsed:
        latest_entry = entry

if not latest_entry:
    print("Нет новостей")
    exit()

title = clean_text(latest_entry.title)
link = latest_entry.link

# --- Пытаемся взять текст статьи ---
try:
    article_text = extract_article_text(link)
    article_preview = article_text[:MAX_TEXT_LENGTH]
except Exception as e:
    article_preview = clean_text(latest_entry.summary)

# --- Формируем пост ---
message = (
    f"🔥 {title}\n\n"
    f"{article_preview}\n\n"
    f"Источник: {link}"
)

send_to_telegram(message)
print("Новость отправлена")
