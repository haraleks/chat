import asyncio
from asyncio import transports

from PySide2.QtWidgets import QMainWindow, QApplication
from asyncqt import QEventLoop

from app.interface import Ui_MainWindow

class ClineProtocol(asyncio.Protocol):
    transport: transports.Transport
    window: 'MainWindow'

    def __init__(self, chat_window: 'MainWindow'):
        self.window = chat_window

    def data_received(self, data):
        decoded = data.decode()
        self.window.append_text(decoded)

    def send_data(self, message: str):
        encoded = message.encode()
        self.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.window.append_text('Подключено')
        self.transport = transport

    def connection_lost(self, exception):
        self.window.append_text('Отключено')

class MainWindow(QMainWindow, Ui_MainWindow):
    protocol: ClineProtocol

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.send_button.clicked.connect(self.button_hendler)

    def button_hendler(self):
        message_text = self.messag_input.text()
        self. messag_input.clear()
        self.protocol.send_data(message_text)

    def append_text(self, content: str):
        self.message_box.appendPlainText(content)

    def buld_protocol(self):
        self.protocol = ClineProtocol(self)
        return self.protocol

    async def start(self):
        self.show()
        event_loop = asyncio.get_running_loop()

        corutine = event_loop.create_connection(
            self.buld_protocol,
            "127.0.0.1",
            8888
        )

        await asyncio.wait_for(corutine, 1000)



app = QApplication()
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
window = MainWindow()

loop.create_task(window.start())
loop.run_forever()

