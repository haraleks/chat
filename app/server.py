import asyncio
from asyncio import transports
from typing import Optional


def last_message(self):
    for last_m in self.server.messag_list[-10:]:
        self.transport.write(f"{last_m}\n".encode())  # отправляем переписку новому пользвателю


def mess_all_users(self, message):
    for user in self.server.clients:
        user.transport.write(message)


class ServerProtokol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport


    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        decoded = data.decode()
        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith('login:'):
                self.login = decoded.replace('login:','').replace('\r\n','')
                if self.login in self.server.login_lst:
                    self.transport.write((f'Такой логин существует. Введите другой login:\n'.encode()))
                    del self.login
                else:
                    self.transport.write(f'Привет, {self.login}!\n'.encode())
                    self.server.login_lst.append(self.login)
                    last_message(self)
            else:
                self.transport.write(('Неправильный логин\n'.encode()))


    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport


    def connection_lost(self, exception):
        mess_live = f'{self.login} покинул чат:\n'.encode()
        self.server.clients.remove((self))
        self.server.login_lst.remove((self.login))
        mess_all_users(self,mess_live)


    def send_message(self, content: str):
        message = f"{self.login}: {content}"
        self.server.messag_list.append((message))
        all_message = self.server.messag_list
        if len(all_message) > 10:  #удаление лишних сообщений
            self.server.messag_list.pop(0)
        mess_all_users(self,message.encode())


class Server:
    clients: list
    login_lst: list
    messag_list: list

    def __init__(self):
        self.clients = []
        self.login_lst = []
        self.messag_list = []


    def build_protocol(self):
        return ServerProtokol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888,
        )

        print('Сервер запущен...')

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print('Сервер остановлен вручную')