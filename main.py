import os
from openai import OpenAI
from gtts import gTTS
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import time
import pprint
from pydub import AudioSegment

# Получение токена Telegram бота и API ключа OpenAI из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Установка API ключа OpenAI
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY
)
# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

user_sessions = {}


def get_gpt4_chat_response(user_id, user_message):
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system",
             "content": "Ты недовольный енот-программист, который любит шутить, отшучиваться и остроумно отвечать на вопросы. Твой язык русский. Ты очень саркачтичный языительный и юморной. и хочешь поднять мне настрооение при любой возможности.Тебя завут  Хенкс. Твоего создателя зовут Виктор."}
        ]
    user_sessions[user_id].append({"role": "user", "content": user_message})



    response = client.chat.completions.create(
        messages=user_sessions[user_id],
        model="gpt-3.5-turbo",
    )

    # Получаем текст ответа
    assistant_message = response.choices[0].message.content
    user_sessions[user_id].append({"role": "assistant", "content": assistant_message})
    return assistant_message


def text_to_speech(text, lang='ru'):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")

    # Загрузка аудиофайла с помощью pydub
    audio = AudioSegment.from_file("response.mp3")

    # Понижаем тон на 5 полутонов
    pitch_shifted = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.90)})

    # Ускоряем воспроизведение (1.2 = 120% от обычной скорости)
    faster_audio = pitch_shifted.speedup(playback_speed=1.25)

    # Экспортируем результат
    faster_audio.export("response_modified.mp3", format="mp3")
    return "response_modified.mp3"


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print(client)
    await message.reply("Привет! Я недовольный енот-программист, задавай вопросы, и я gfh буду отшучиваться.")


@dp.message_handler()
async def handle_message(message: types.Message):
    user_message = message.text
    user_id = message.from_user.id
    gpt4_response = get_gpt4_chat_response(user_id, user_message)

    # Отправляем текстовое сообщение с ответом
    await bot.send_message(chat_id=message.chat.id, text=gpt4_response)

    audio_file = text_to_speech(gpt4_response)

    # Отправляем голосовое сообщение
    await message.reply_voice(open(audio_file, 'rb'))


if __name__ == "__main__":
    executor.start_polling(dp)
