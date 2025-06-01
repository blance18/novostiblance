import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

# Конфигурация
API_TOKEN = 'ВАШ_BOT_TOKEN'               # ← сюда вставь свой токен
CHANNEL_ID = '@ВАШ_КАНАЛ'                 # ← сюда вставь @имя_канала
NEWSAPI_KEY = 'ВАШ_NEWSAPI_KEY'           # ← ключ с https://newsapi.org/
KEYWORDS = 'sport'
POSTED_FILE = 'posted_news.json'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot)


def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_posted(posted_ids):
    with open(POSTED_FILE, 'w', encoding='utf-8') as f:
        json.dump(posted_ids, f)


def format_message(article):
    title = f"🏆 <b>{article['title']}</b>"
    description = article.get('description', '') or ''
    intro = "🔥 Свежая новость из мира спорта:\n\n"
    preview = (description[:200] + '…') if description else '📌 Подробнее по ссылке ниже.'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Забрать бонус 1win", url="https://1wtofc.life/casino/list?open=register&p=ybib"),
            InlineKeyboardButton(text="🔗 Подробнее", url=article['url'])
        ]
    ])

    return intro + title + "\n\n" + preview, keyboard


async def fetch_news():
    url = (
        f"https://newsapi.org/v2/everything?q={KEYWORDS}&language=ru&pageSize=5&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('articles', [])
            return []


async def publish_news():
    posted_ids = load_posted()
    articles = await fetch_news()
    new_count = 0

    for article in articles:
        if new_count >= 1:
            break
        uid = article['url']
        if uid not in posted_ids:
            message, keyboard = format_message(article)
            try:
                await bot.send_message(chat_id=CHANNEL_ID, text=message, reply_markup=keyboard)
                posted_ids.append(uid)
                new_count += 1
                await asyncio.sleep(3)
            except Exception as e:
                logging.error(f"❌ Ошибка при отправке: {e}")

    save_posted(posted_ids)
    if new_count == 0:
        logging.info("🔄 Нет новых новостей.")


async def scheduler():
    while True:
        await publish_news()
        await asyncio.sleep(3600)  # 1 новость в час


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await scheduler()


if __name__ == '__main__':
    asyncio.run(main())
