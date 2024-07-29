from telethon.tl.types import MessageEntityTextUrl
from glob import glob
import datetime
import os
import logging  # стандартная библиотека для логирования
from telethon import TelegramClient, events, sync, connection  # pip3 install telethon
from telethon.tl.functions.channels import JoinChannelRequest
from config import API_ID, API_HASH  # получение айди и хэша нашего приложения из файла config.py
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError


# настройка логгера
logging.basicConfig(
    level=logging.INFO,
    filename='parser_log.log',
    filemode='w',
    format="%(asctime)s %(levelname)s %(message)s"
)


url = ["https://t.me/+HqfVmcDt3DVjYmUy",]
flag = True


async def get_channel_id(client, link):  # получение ID канала
    m = await client.get_messages(link, limit=1)
    channel_id = m[0].peer_id.channel_id
    return str(channel_id)


def clearify_text(msg):  # очищение текста от символов гиперссылки
    text = msg.message
    text_splitted = text.split()
    text_listed = [word for word in text_splitted if word != ' ']
    return " ".join(text_listed)


def get_message_content(client, msg, url, channel_name, directory_name):  # получение содержимого сообщения
    msg_date = str(msg.date)  # дата отправки сообщения
    msg_url = url + '/' + str(msg.id)  # каст ссылки на сообщение
    if msg.message:  # если сообщение содержит текст, запись этого текста в текстовый файл в папке сообщения
        text = clearify_text(msg=msg)
        print(f"{channel_name}/{directory_name}/{directory_name}")
        print(text)
    #    database.db_chats(name_chat=channel_name, text=text)
    if msg.media:  # если сообщение содержит медиа (фото, видео, документы, файлы), загрузка медиа в папку сообщения
        client.download_media(message=msg, file=f"{channel_name}/{directory_name}")


async def parse(client, url):  # сбор сообщений из канала
    err = []  # переменная возможной ошибки
    channel_id = await get_channel_id(client, url)  # получение ID канала
    os.makedirs(channel_id, exist_ok=True)  # создание папки канала в текущей директории  # получение даты, с которой начинать парсинг
    async for message in client.iter_messages(url, reverse=True):  # итератор по сообщениям (урл - ссылка
                                                                                 # на канал, реверс - итерация от старых
                                                                                 # к новым, офсет - дата с которой
                                                                                 # начинать парсинг
        try:
            directory_name = str(message.id)  # получение ID сообщения
            os.makedirs(f"{channel_id}/{directory_name}", exist_ok=True)  # создание папки сообщения
            get_message_content(client, message, url, channel_id, directory_name)  # обработка сообщения

        except Exception as passing:  # обработка ошибок
            err.append(passing)
            continue
    return err  # возврат возможных ошибок


async def main():
    async with TelegramClient('new', API_ID, API_HASH) as client:
        for channel in url:
            try:
                await client(JoinChannelRequest(channel))
                err = await parse(client, channel)  # обработка сообщений
            except FloodWaitError as fwe:
                print(f'Waiting for {fwe}')
                await asyncio.sleep(delay=fwe.seconds)
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())