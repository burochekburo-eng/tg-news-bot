import feedparser
import requests
import os
from bs4 import BeautifulSoup  # можно добавить в workflow pip install beautifulsoup4

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru"
]

def get_full_article(url):
    """Получаем текст и главное фото со страницы статьи"""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Текст статьи
        paragraphs = soup.find_all("p")
        text = "\n\n".join([p.get_text() for p in paragraphs])
        if len(text) < 500:  # если мало текста, берём весь
            text = soup.get_text()

        # Картинка статьи
        img_tag = soup.find("img")
        img_url = img_tag['src'] if img_tag else None

        return text, img_url
    except Exception as e:
        print("Ошибка получения статьи:", e)
        return "", None

def send_to_telegram_photo(caption, photo_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption
    }
    r = requests.post(url, data=payload)
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
    title = latest_entry.title
    link = latest_entry.link

    # Получаем полный текст статьи и картинку
    full_text, photo_url = get_full_article(link)

    # Если текста мало, используем summary из RSS
    if len(full_text) < 100:
        full_text = latest_entry.summary

    caption = f"🔥 {title}\n\n{full_text}\n\nИсточник: {link}"

    if photo_url:
        send_to_telegram_photo(caption, photo_url)
    else:
        # если картинки нет, просто текст
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHANNEL_ID, "text": caption}
        r = requests.post(url, json=payload)
        print("Telegram response:", r.text)
