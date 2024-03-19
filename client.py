import asyncio
import json
import os
import logging

from functools import partial

logging.basicConfig(level=logging.INFO,
                    filename="client.log",
                    filemode="w",
                    encoding='utf-8',
                    format="%(asctime)s;%(levelname)s;%(message)s;"
                    )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


class ChatClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.is_connect = False


    async def connect(self):
        logging.info("Попытка присоединиться...")
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.is_connect = True
        await self.send_message(event="join",login=self.username)
        asyncio.create_task(self.receive_messages())


    async def receive_messages(self,):
        while data := await self.reader.readline():
            message = json.loads(data.decode())
            if message["event"] == "message":
                logging.info(f"{message['user'] if message['user'] != self.username else 'Вы'}: {message['text']}")
            elif message["event"] == "leave":
                logging.info(f"{message['login']} вышел")
            elif message["event"] == "join":
                logging.info(f"{message['login']} зашел")


    async def send_message(self, **kwargs):
            try:
                data = json.dumps(kwargs)
                self.writer.write(data.encode() + b"\n")
                await self.writer.drain()
            except ConnectionError as e:
                logging.info(f"Ошибка отправки сообщения: {str(e)}")
                writer.close()
                await writer.wait_closed()


    async def start_chatting(self):
        try:
            await self.connect()
            while True:
                message_text = await async_input()
                if message_text.lower() == 'quit':
                    await self.send_message(event="leave", login=self.username)
                    self.writer.close()
                    await self.writer.wait_closed()
                    break
                else:
                    await self.send_message(event="message", text=message_text, user=self.username)
        except Exception as err:
            logging.critical(f"Ошибка соединения: {str(err)}")


async def async_input() -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, '',)


if __name__ == "__main__":
    try:
        username = input("Введите имя: ")
        chat_client = ChatClient(os.getenv('HOST'),os.getenv('PORT'), username)
        asyncio.run(chat_client.start_chatting())
    except KeyboardInterrupt:
        logging.error("Завершение")
