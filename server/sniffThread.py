from scapy.all import *
import threading, thread
from scapy.layers.inet import IP

import sys
sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.0.105'


class SniffThread(threading.Thread):
    def __init__(self):
        super(SniffThread, self).__init__()

    def run(self):
        while 1:
            p = sniff(iface='atum0', count=1)

            thread.start_new_thread(POST, (p, IP_ADDRESS))
