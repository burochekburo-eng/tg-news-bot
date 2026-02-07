import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_KEY = 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

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=ChatGPT&hl=ru",
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru",
    "https://news.google.com/rss/search?q=Neural+networks&hl=ru"
]

data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "Перепиши коротко"},
        {"role": "user", "content": "Привет, мир!"}
    ]
}

r = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    },
    json=data
)

print(r.json()))

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
