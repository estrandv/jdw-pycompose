import math
from time import sleep

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading

class Listener:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.messages: dict[str, list] = {}

        server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1", 13456), self.dispatcher)
        print("Serving on {}".format(server.server_address))

        threading.Thread(target=server.serve_forever, daemon=True)

    def wait_for(self, addr: str):

        if addr not in self.messages:
            self.messages[addr] = []

        current_amount = len(self.messages[addr])

        def register(addr, args):
            print("GOT MESSAGE!", addr)
            self.messages[addr].append(args)

        self.dispatcher.map(addr, register)

        while len(self.messages[addr]) <= current_amount:
            sleep(0.5)
            print("Polling...")
