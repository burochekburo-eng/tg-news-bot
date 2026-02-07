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
            {"role": "system", "content": "Ты переписываешь новость для Telegram: хук, что произошло, почему важно, вывод, теги. Пиши коротко, просто, цепко."},
            {"role": "user", "content": text}
        ]
    }
    r = requests.post(url, headers=headers, json=data)

    # Проверка ответа
    try:
        return r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Ошибка OpenAI API:", r.text)  # выведет что вернул API
        return text[:200]  # просто возвращаем первые 200 символов новости

for rss in RSS_FEEDS:
    feed = feedparser.parse(rss)
    if not feed.entries:
        continue
    entry = feed.entries[0]
    post = rewrite(entry.title + ". " + entry.summary)
    send_to_telegram(post)

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": CHANNEL_ID, "text": post}
)
