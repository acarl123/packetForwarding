from scapy.all import *
import threading, thread

import sys

from scapy.layers.inet import IP

sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.0.111'
MAC_ADDR = getHwAddr('enp0s25')


class SniffThread(threading.Thread):
    def __init__(self):
        super(SniffThread, self).__init__()

    def run(self):
        while 1:
            # Test packet generation --------
            # p = Ether()/IP()/'Hello World'
            # time.sleep(2)
            # -------------------------------

            # Packet sniff from eth interface -----------
            p = sniff(iface='enp0s25', count=1)
            p = self.process_packet(p)
            if not p: continue
            # -------------------------------------------

            p = [ord(c) for c in str(p)]
            print p
            thread.start_new_thread(POST, (p, IP_ADDRESS))

    def process_packet(self, p):
        # return if no packet
        if not p: return

        # return if the packet originated from self
        if p[Ether].src == MAC_ADDR: return

        # return unchanged packet if broadcast addr
        if p[Ether].src == 'ff:ff:ff:ff:ff:ff': return p