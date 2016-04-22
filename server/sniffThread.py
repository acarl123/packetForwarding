from scapy.all import *
import threading, thread
from scapy.layers.inet import IP

from utils import *


IP_ADDRESS = '192.168.0.111'


class SniffThread(threading.Thread):
    def __init__(self):
        pass

    def run(self):
        while 1:
            p = sniff(iface='atum0', count=1)

            thread.start_new_thread(POST, (p))
