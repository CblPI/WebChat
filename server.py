import asyncio
import json
import os
import logging

from asyncio import StreamReader

logging.basicConfig(level=logging.INFO,
                    filename="server.log",
                    filemode="w",
                    encoding='utf-8',
                    format="%(asctime)s;%(levelname)s;%(message)s;"
                    )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class ChatServer:
    def __init__(self, port):
        self.host = '127.0.0.1'
        self.port = port
        self.clients = {}

    async def handle_client(self, reader: StreamReader, writer):
        async for data in reader:
            message = data.decode()
            try:
                message = json.loads(message)
                if message["event"] == "join":
                    self.clients[writer] = message["login"]
                    await self.send_to_all({"event": "join", "login": message["login"]})
                    logging.info(f'Пользователь {message["login"]} присоединился.')
                elif message["event"] == "message":
                    await self.send_to_all({"event": "message", "text": message["text"], "user": self.clients[writer]})
                    logging.info(f'Сообщение от {self.clients[writer]}: {message["text"]}')
                elif message["event"] == "leave":
                    del self.clients[writer]
                    await self.send_to_all({"event": "leave", "login": message["login"]})
                    logging.info(f'Пользователь: {message["login"]} покинул чат.')
            except json.JSONDecodeError:
                logging.error("Неверный JSON от клиента")


    async def send_to_all(self, message):
        for client_writer in self.clients:
            client_writer.write(json.dumps(message).encode() + b"\n")
            await client_writer.drain()

    async def run_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        logging.info(f'Сервер запущен на: [{self.host}:{self.port}]')

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    port = os.getenv('PORT')
    if (port is not None):
        try:
            chat_server = ChatServer(port)
            asyncio.run(chat_server.run_server())
        except KeyboardInterrupt:
            logging.critical(f"Остановлено с {KeyboardInterrupt}")
    else: logging.critical("Необходимо добавить значение порта в переменную окружения!")