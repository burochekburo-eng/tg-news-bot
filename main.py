import feedparser
import requests
import os

# Секреты из GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Список RSS лент
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=ChatGPT&hl=ru",
    "https://news.google.com/rss/search?q=AI+Israel&hl=ru",
    "https://news.google.com/rss/search?q=Neural+networks&hl=ru"
]

# Функция переписывания новости через OpenAI
def rewrite(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Ты переписываешь новость для Telegram. Сделай пост более детальным: хук, что произошло, подробности, почему важно, вывод, теги. Пиши простым языком, но интересно и цепко."},
            {"role": "user", "content": text}
        ]
    }
    r = requests.post(url, headers=headers, json=data)

    # Проверка ответа
    try:
        return r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("Ошибка OpenAI API:", r.text)
        return text[:400]  # возвращаем немного текста на случай ошибки

# Функция отправки в Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message
    }
    r = requests.post(url, json=payload)
    print("Ответ Telegram API:", r.text)  # чтобы видеть ошибки

# Основной цикл — выбираем только одну самую свежую новость
latest_entry = None

for rss in RSS_FEEDS:
    feed = feedparser.parse(rss)
    if not feed.entries:
        continue
    entry = feed.entries[0]
    # Сравниваем даты, берём самую свежую
    if latest_entry is None or entry.published_parsed > latest_entry.published_parsed:
        latest_entry = entry

# Если нашли новость — переписываем и отправляем
if latest_entry:
    text_to_rewrite = latest_entry.title + "\n\n" + latest_entry.summary
    post = rewrite(text_to_rewrite)
    send_to_telegram(post)
