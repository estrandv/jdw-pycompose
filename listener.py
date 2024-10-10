import math
from time import sleep

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import threading

# TODO: Complete hackjob, essentially only works for nrt_record_finished, the only usage
class Listener:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.messages: list[str] = []
        self.server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1", 13456), self.dispatcher)
        print("Serving on {}".format(self.server.server_address))

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def wait_for(self, addr):
        before = len(self.messages)
        self.dispatcher.map(addr, register, self)
        times = 5
        count = 0
        while len(self.messages) == before:
            print("Waiting for", addr)
            sleep(1)
            if count >= times:
                raise Exception("Timed out waiting for jdw-sc response", addr)
        self.dispatcher.unmap(addr, register, self)

# TODO: This is the main reason we can't listen for more than a very specific message: fixed arg set
def register(addr, args, status, file_path):
    print("Response from Router:", addr, status, file_path)
    args[0].messages.append(file_path)
