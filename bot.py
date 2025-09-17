




import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔑 Данные для запуска
API_ID = 29683541
API_HASH = "3a9d6a1205003b0145bc9b6b8d8e1193"
BOT_TOKEN = "8355197925:AAEKSpqlEe6WwfewmxAncIJzZvxyOEYej2o"

app = Client("anon_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# username -> user_id
users = {}
# user_id -> None (ждёт username) или user_id получателя
chats = {}

# список эмодзи
ANON_EMOJIS = ["🕵️", "👻", "😶‍🌫️", "🎭", "❤️‍🔥", "💌", "🖤", "🤫", "🌑", "💔"]

logging.basicConfig(level=logging.INFO)

INSTRUCTION = (
"👋 Привет я бот.\n\n"
"Мая функция отправлять файлы📁 или сообщение✍️ пользователям анонимно.\n\n"
"Вот маленкий инструкция⚙️ как можно использовать меня;\n\n"
"1️⃣ Введи /setuser\n"
"2️⃣ Напиши @username получателья"

)


# /start
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user = message.from_user
    if user and user.username:
        users[user.username.lower()] = user.id
        chats[user.id] = None
        await message.reply(INSTRUCTION)
    else:
        await message.reply("❌ У тебя нет @username — добавь его в настройках Telegram.")


# /setuser
@app.on_message(filters.command("setuser"))
async def setuser(client, message: Message):
    user_id = message.from_user.id
    chats[user_id] = None
    await message.reply("✍️ Напиши @username получателя (например: @vasya).")


# обработка сообщений
@app.on_message(filters.private & ~filters.command(["start", "setuser"]))
async def handler(client, message: Message):
    sender_id = message.from_user.id

    # ждём username
    if sender_id in chats and chats[sender_id] is None and message.text:
        if not message.text.startswith("@"):
            await message.reply("⚠️ Нужно ввести username в формате: @username")
            return

        target_username = message.text[1:].lower()
        if target_username not in users:
            await message.reply("❌ Этот пользователь ещё не запускал бота.")
            return

        chats[sender_id] = users[target_username]
        await message.reply(f"✅ Получатель @{target_username} установлен. Теперь отправь сообщение.")
        return

    # если есть установленный получатель
    if sender_id in chats and chats[sender_id]:
        target_id = chats[sender_id]
        emoji = random.choice(ANON_EMOJIS)

        try:
            if message.text:
                await app.send_message(target_id, f"{emoji} Анонимное сообщение:\n\n{message.text}")

            elif message.voice:
                await app.send_voice(target_id, message.voice.file_id, caption=f"{emoji} Анонимное сообщение")

            elif message.photo:
                await app.send_photo(target_id, message.photo.file_id, caption=f"{emoji} Анонимное сообщение")

            elif message.document:
                await app.send_document(target_id, message.document.file_id, caption=f"{emoji} Анонимное сообщение")

            elif message.audio:
                await app.send_audio(target_id, message.audio.file_id, caption=f"{emoji} Анонимное сообщение")

            elif message.video:
                await app.send_video(target_id, message.video.file_id, caption=f"{emoji} Анонимное сообщение")

            else:
                await app.copy_message(target_id, from_chat_id=sender_id, message_id=message.message_id)

            # ✅ ответ пользователю + сброс чата
            await message.reply("✅ Сообщение доставлено!\n\n" + INSTRUCTION)
            chats[sender_id] = None  # сбрасываем, снова ждём username

        except Exception as e:
            logging.exception("Ошибка при пересылке:")
            await message.reply("⚠️ Ошибка при отправке сообщения.")
            chats[sender_id] = None
    else:
        await message.reply("❌ Сначала выбери получателя через /setuser")


if __name__ == "__main__":
    app.run()
