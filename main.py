import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=ChatGPT&hl=ru",
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru",
    "https://news.google.com/rss/search?q=Neural+networks&hl=ru"
]

def rewrite(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Перепиши новость коротко для Telegram, добавь вывод."},
            {"role": "user", "content": text}
        ]
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]

feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

post = rewrite(entry.title + ". " + entry.summary)

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": CHANNEL_ID, "text": post}
)
