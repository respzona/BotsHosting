#!/usr/bin/env python3
"""
🚀 RESPZONA Bot Server - Собственный хостинг
Запусти: python bot_server.py
Бот будет работать 24/7 на твоём сервере/VDS/облаке
"""

import logging
import json
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from flask import Flask, request
import asyncio
import threading

# ====================================================================
# FLASK + WEBHOOK
# ====================================================================

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ✅ КОНФИГУРАЦИЯ - ЗАМЕНИ ТОЛЬКО ЭТО!
TOKEN = "8501298263:AAFsKnHjy9ha9pWji7j36kfQ3e5za01aYdQ"
WEBHOOK_URL = "https://твой-домен.com/webhook"  # ← ЗАМЕНИ НА СВОЙ!
WEBHOOK_PORT = 5000

# Ссылки
WEBAPP_URL = "https://verdant-paprenjak-887d4a.netlify.app/"
TELEGRAM_URL = "https://t.me/RESPZONA"
YOUTUBE_URL = "https://www.youtube.com/@ANTWOORDMUS"
TIKTOK_URL = "https://www.tiktok.com/@respozona"
YOUTUBE_STREAM_URL = "https://www.youtube.com/live/RESPZONA"
TIKTOK_STREAM_URL = "https://www.tiktok.com/@respozona/live"

YOOMONEY_URL = "https://yoomoney.ru/to/4100118663676748"
BOOSTY_DONATE_URL = "https://boosty.to/respzona/donate"

CARD_NUMBER = "2200 7019 4251 1996"
CARD_HOLDER = "RESPZONA"

USERS_FILE = "users_data.json"
ADMIN_ID = 8026939529

application = None

# ====================================================================
# ТРЕКИ
# ====================================================================

TRACKS = {
    'huday': {
        'name': 'HUDAY',
        'file_id': 'CQACAgIAAxkBAAM6aUWjWuDlBxzAyK-ZQi1JOQ8tvRkAAmuTAALKbTFK7KogMulGkc42BA',
        'date': '19.06.2025',
        'artists': 'Aryx, Nng',
        'genre': 'Мемный поп/рэп',
        'description': 'Мемный по настроению, но при этом завалакивающий трек про бездомного и пирог'
    },
    'huday_phonk': {
        'name': 'HUDAY PHONK',
        'file_id': 'CQACAgIAAxkBAANHaUWluTVBY9v6R2dpf9o1VHJLGpgAApGTAALKbTFKhwWrBH7qkD42BA',
        'date': '30.10.2025',
        'artists': 'Aryx, Nng',
        'genre': 'Phonk/Электроника',
        'description': 'Киберпанк-версия легендарного HUDAY с неоновыми синтезаторами'
    },
    'world_run': {
        'name': 'WORLD RUN PHONK',
        'file_id': 'CQACAgIAAxkBAANJaUWl3P9Epi17pyrTZAABD1gsKLwkAAKUkwACym0xSrJw9quY1smxNgQ',
        'date': '01.11.2025',
        'artists': 'Aryx, Nng',
        'genre': 'Phonk/Киберпанк',
        'description': 'Энергетичный трек про скорость, адреналин и движение'
    },
    'secret': {
        'name': '🔒 СЕКРЕТНЫЙ ТРЕК',
        'file_id': None,
        'date': '❓ Дата секрет',
        'artists': 'Aryx, Nng',
        'genre': 'Сюрприз',
        'description': 'Новый трек выйдет очень скоро! Следи за нашими обновлениями 🎵'
    }
}

# ====================================================================
# События
# ====================================================================

EVENTS = [
    {
        'date': '07.01.2025',
        'time': '19:00',
        'title': '🎉 БОЛЬШОЙ НОВОГОДНИЙ СТРИМ',
        'description': 'Масштабная новогодняя трансляция музыки, веселья и общения с фанатами!',
        'platforms': [
            {'name': '🎬 YouTube (БЕСПЛАТНО)', 'url': YOUTUBE_STREAM_URL},
            {'name': '🎵 TikTok Live (БЕСПЛАТНО)', 'url': TIKTOK_STREAM_URL},
            {'name': '💎 Boosty (БЕСПЛАТНО)', 'url': BOOSTY_DONATE_URL}
        ]
    }
]

# ====================================================================
# Работа с пользователями
# ====================================================================

def load_users_data():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            return {}
    return {}

def save_users_data(users_data):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        logger.info("✅ Данные сохранены")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

users_data = load_users_data()

# ====================================================================
# WEBHOOK ENDPOINTS
# ====================================================================

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json()
        if data:
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")
        return 'Error', 500

@app.route('/set-webhook', methods=['GET'])
async def set_webhook_endpoint():
    try:
        success = await application.bot.set_webhook(url=WEBHOOK_URL)
        if success:
            logger.info(f"✅ Вебхук: {WEBHOOK_URL}")
            return f"✅ Вебхук установлен!<br>Бот работает 24/7 🎉", 200
        return "❌ Ошибка", 400
    except Exception as e:
        return f"❌ {e}", 500

@app.route('/health', methods=['GET'])
def health():
    return f'БОТ РАБОТАЕТ 24/7 ✅\nПользователей: {len(users_data)}', 200

@app.route('/stats', methods=['GET'])
def stats():
    return {
        'status': 'online',
        'users': len(users_data),
        'timestamp': datetime.now().isoformat()
    }, 200

# ====================================================================
# КОМАНДЫ
# ====================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(f"👤 {user.first_name} (ID: {user.id}) -> /start")

    if str(chat_id) not in users_data:
        users_data[str(chat_id)] = {
            'user_id': user.id,
            'username': user.username or 'unknown',
            'first_name': user.first_name,
            'notifications_enabled': True,
            'join_date': datetime.now().isoformat()
        }
        save_users_data(users_data)

    keyboard = [
        [InlineKeyboardButton("🎵 Приложение", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton("🎵 Треки", callback_data='tracks'),
            InlineKeyboardButton("🎟️ Билеты", callback_data='tickets')
        ],
        [
            InlineKeyboardButton("💳 Донаты", callback_data='donates'),
            InlineKeyboardButton("🔔 Уведомления", callback_data='notifications')
        ],
        [
            InlineKeyboardButton("📱 Telegram", url=TELEGRAM_URL),
            InlineKeyboardButton("👥 О нас", callback_data='about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎶 Привет, {user.first_name}! Добро пожаловать в RESPZONA! 🎶\n\n"
        f"✨ Слушать треки онлайн\n"
        f"🎤 Узнать о событиях\n"
        f"💳 Поддержать проект\n"
        f"🔔 Включить уведомления\n\n"
        f"Выбери пункт меню! 👇",
        reply_markup=reply_markup
    )

async def notify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав!")
        return

    if not context.args:
        await update.message.reply_text(
            "📢 `/notify huday`\n"
            "📢 `/notify huday_phonk`\n"
            "📢 `/notify world_run`\n"
            "📢 `/notify secret`",
            parse_mode='Markdown'
        )
        return

    track_id = context.args[0]
    if track_id not in TRACKS:
        await update.message.reply_text("❌ Трек не найден")
        return

    await update.message.reply_text(f"📢 Отправляю уведомление...")
    await send_track_notification(context, track_id)
    await update.message.reply_text("✅ Отправлено!")

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет прав!")
        return

    if not context.args:
        await update.message.reply_text("`/broadcast Ваше сообщение`", parse_mode='Markdown')
        return

    message_text = ' '.join(context.args)
    
    if len(message_text) > 4096:
        await update.message.reply_text(f"❌ Слишком длинное! ({len(message_text)}/4096)")
        return

    await update.message.reply_text("📢 Отправляю рассылку...")

    sent = 0
    failed = 0
    blocked = 0

    for chat_id_str, user_data in users_data.items():
        if user_data.get('notifications_enabled', True):
            try:
                chat_id = int(chat_id_str)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📢 **RESPZONA:**\n\n{message_text}",
                    parse_mode='Markdown'
                )
                sent += 1
            except Exception as e:
                error_msg = str(e).lower()
                if 'blocked' in error_msg or 'forbidden' in error_msg:
                    blocked += 1
                    user_data['notifications_enabled'] = False
                    save_users_data(users_data)
                else:
                    failed += 1

    save_users_data(users_data)
    await update.message.reply_text(
        f"✅ **ЗАВЕРШЕНО!**\n\n"
        f"✅ Доставлено: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"🚫 Заблокировано: {blocked}",
        parse_mode='Markdown'
    )

# ====================================================================
# ОБРАБОТЧИКИ КНОПОК
# ====================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'tracks':
        await show_tracks(query)
    elif query.data == 'back_to_menu':
        await back_to_menu(query)

async def show_tracks(query):
    keyboard = [
        [
            InlineKeyboardButton("🎵 HUDAY", callback_data='info_track_huday'),
            InlineKeyboardButton("▶️", callback_data='play_track_huday')
        ],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🎵 **Наши треки:**\n\n"
             "🎵 HUDAY - мемный поп/рэп 🥧\n"
             "🎵 HUDAY PHONK - киберпанк 🌆\n"
             "🎵 WORLD RUN - phonk 🏃\n"
             "🔒 СЕКРЕТНЫЙ - выходит скоро! 🎉",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_menu(query):
    keyboard = [
        [InlineKeyboardButton("🎵 Приложение", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton("🎵 Треки", callback_data='tracks'),
            InlineKeyboardButton("🎟️ Билеты", callback_data='tickets')
        ],
        [
            InlineKeyboardButton("💳 Донаты", callback_data='donates'),
            InlineKeyboardButton("🔔 Уведомления", callback_data='notifications')
        ],
        [
            InlineKeyboardButton("📱 Telegram", url=TELEGRAM_URL),
            InlineKeyboardButton("👥 О нас", callback_data='about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🎶 **RESPZONA** 🎶\n\nВыбери пункт:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    logger.info(f"📝 Текст: {text}")
    await update.message.reply_text("Используй /start для меню")

# ====================================================================
# РАССЫЛКА
# ====================================================================

async def send_track_notification(context: ContextTypes.DEFAULT_TYPE, track_id: str) -> None:
    if track_id not in TRACKS:
        logger.error(f"❌ Трек {track_id} не найден")
        return

    track = TRACKS[track_id]
    sent = 0

    for chat_id_str, user_data in users_data.items():
        if user_data.get('notifications_enabled', True):
            try:
                chat_id = int(chat_id_str)
                text = (
                    f"🎵 **НОВЫЙ ТРЕК!** 🎵\n\n"
                    f"🎵 **{track['name']}**\n\n"
                    f"📅 **Дата:** {track['date']}\n"
                    f"🎤 **Артисты:** {track['artists']}\n"
                    f"🎸 **Жанр:** {track['genre']}\n\n"
                    f"📝 {track['description']}"
                )

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown'
                )

                if track['file_id'] is not None:
                    await context.bot.send_audio(
                        chat_id=chat_id,
                        audio=track['file_id'],
                        title=track['name'],
                        performer='RESPZONA'
                    )

                sent += 1
            except Exception as e:
                logger.error(f"❌ {chat_id_str}: {e}")

    logger.info(f"📊 Отправлено {sent}")

# ====================================================================
# ИНИЦИАЛИЗАЦИЯ
# ====================================================================

def setup_application():
    global application
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify", notify_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    return application

# ====================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ====================================================================

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🚀 ЗАПУСК RESPZONA БОТА 24/7")
    logger.info(f"📊 Загружено {len(users_data)} пользователей")
    logger.info("=" * 70)

    application = setup_application()

    logger.info("✅ Приложение инициализировано")
    logger.info(f"🌐 Вебхук: {WEBHOOK_URL}")
    logger.info(f"🔗 Здоровье: http://localhost:{WEBHOOK_PORT}/health")
    logger.info("")
    logger.info("📋 ЧТО ДЕЛАТЬ:")
    logger.info("1. Замени WEBHOOK_URL на свой домен/IP")
    logger.info("2. Открой в браузере: http://твой-домен/set-webhook")
    logger.info("3. Готово! Бот работает 24/7 🎉")
    logger.info("")
    logger.info("=" * 70)

    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False)
