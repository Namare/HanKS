import os
import openai
from gtts import gTTS
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pydub import AudioSegment

# Токен вашего Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


# Функция для отправки текста к GPT-4 и получения ответа
def get_gpt4_response(prompt):
    response = openai.Completion.create(
        engine="gpt-4",  # Указание использования модели GPT-4
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()


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
    # Получаем ответ от GPT-4
    gpt4_response = get_gpt4_response(user_message)
    await message.reply(f"GPT-4 ответил: {gpt4_response}")

    # Преобразуем текст в голос
    audio_file = text_to_speech(gpt4_response)
    await message.reply_voice(open(audio_file, 'rb'))

    # Удаляем временные файлы
    os.remove(audio_file)


if __name__ == "__main__":
    executor.start_polling(dp)
