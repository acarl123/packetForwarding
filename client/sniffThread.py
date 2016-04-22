from scapy.all import *
import threading, thread


from utils import *


IP_ADDRESS = '192.168.0.111'


class SniffThread(threading.Thread):
    def __init__(self):
        pass

    def run(self):
        while 1:
            p = Ether()/IP()/'Hello World'
            time.sleep(2)

            thread.start_new_thread(POST, (p))