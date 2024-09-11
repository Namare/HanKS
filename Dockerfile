FROM python:3.10-slim

# Установим ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . /app

# Переходим в рабочую директорию
WORKDIR /app

# Указываем команду для запуска бота
CMD ["python", "main.py"]
