from scapy.all import *
import threading, thread

import sys

from scapy.layers.inet import IP

sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.0.111'


class SniffThread(threading.Thread):
    def __init__(self):
        super(SniffThread, self).__init__()

    def run(self):
        while 1:
            p = Ether()/IP()/'Hello World'
            time.sleep(2)

            p = [ord(c) for c in str(p)]
            print p
            thread.start_new_thread(POST, (p, IP_ADDRESS))