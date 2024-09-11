import os
import openai
from gtts import gTTS
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pydub import AudioSegment

# Получение токена Telegram бота и API ключа OpenAI из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
OPENAI_API_KEY =os.environ["OPENAI_API_KEY"]


# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Инициализация истории сообщений (контекста) для каждого пользователя
user_sessions = {}


# Функция для отправки запроса к GPT-4 с сохранением истории сообщений
def get_gpt4_chat_response(user_id, user_message):
    # Если сессия для пользователя еще не создана, создаем её
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system",
             "content": "Ты ассистент, который помогает пользователю с вопросами по программированию."}
        ]

    # Добавляем сообщение пользователя в контекст
    user_sessions[user_id].append({"role": "user", "content": user_message})

    # Отправляем запрос к OpenAI GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Используем модель GPT-4
        messages=user_sessions[user_id],
        max_tokens=150,
        temperature=0.7
    )

    # Получаем текст ответа
    assistant_message = response.choices[0].message['content'].strip()

    # Добавляем ответ модели в историю для сохранения контекста
    user_sessions[user_id].append({"role": "assistant", "content": assistant_message})

    return assistant_message


# Функция для преобразования текста в голос (используя gTTS)
def text_to_speech(text, lang='ru'):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    return "response.mp3"


# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я бот, подключенный к GPT-4. Задавай вопросы, и я отвечу голосом.")


# Обработка текстовых сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    user_message = message.text
    user_id = message.from_user.id  # Получаем ID пользователя

    # Получаем ответ от GPT-4 с сохранением контекста для каждого пользователя
    gpt4_response = get_gpt4_chat_response(user_id, user_message)
    await message.reply(f"GPT-4 ответил: {gpt4_response}")

    # Преобразуем текст в голос
    audio_file = text_to_speech(gpt4_response)
    await message.reply_voice(open(audio_file, 'rb'))

    # Удаляем временные файлы
    os.remove(audio_file)


if __name__ == "__main__":
    executor.start_polling(dp)
