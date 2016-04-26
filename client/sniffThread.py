from scapy.all import *
import threading, thread

import sys

from scapy.layers.inet import IP

sys.path.append('/home/andy/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.1.115'
MAC_ADDR = getHwAddr('enp0s25')
print MAC_ADDR


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
            p = sniff(iface='enp0s25', count=1)[0]
            p = self.process_packet(p)
            if not p: continue
            # -------------------------------------------

            p = [ord(c) for c in str(p)]
            thread.start_new_thread(POST, (p, IP_ADDRESS))

    def process_packet(self, p):
        pkt = p.copy()
        # return if no packet
        if not pkt:
            print 'none'
            return

        if pkt[Ether].src == '52:33:b7:53:b6:80':
            return

        # return unchanged packet if broadcast addr
        if pkt[Ether].dst == 'ff:ff:ff:ff:ff:ff':
            print 'broadcast'
            return pkt

        # return if the packet originated from self
        if pkt[Ether].src == MAC_ADDR:
            print 'from self'
            return

        pkt[Ether].src = 'ac:18:26:4b:18:23'
        pkt[Ether].dst = '52:33:b7:53:b6:80'
        if IP in pkt:
            pkt[IP].src = '192.168.2.133'
            pkt[IP].dst = '192.168.2.135'
        return pkt