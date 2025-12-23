# 🚀 RESPZONA Bot - Docker образ
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY bot_server.py .
COPY README.md .

# Порт
EXPOSE 5000

# Переменные окружения (замени перед запуском)
ENV TOKEN="8501298263:AAFsKnHjy9ha9pWji7j36kfQ3e5za01aYdQ"
ENV WEBHOOK_URL="https://твой-домен.com/webhook"
ENV WEBHOOK_PORT="5000"

# Запуск
CMD ["python", "bot_server.py"]
