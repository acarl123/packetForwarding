from scapy.all import *
import threading, thread

import sys

from scapy.layers.inet import IP

sys.path.append('/home/andy/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.50.65'
MAC_ADDR = getHwAddr('enp0s25')
print MAC_ADDR


class SniffThread(threading.Thread):
    def __init__(self):
        super(SniffThread, self).__init__()

    def run(self):
        while 1:
            # Test packet generation --------
            # p = Ether()/IP()/'Hello World'
            # self.process_packet(p)
            # time.sleep(2)
            # -------------------------------

            # Packet sniff from eth interface -----------
            sniff(iface='myTun', prn=self.process_packet)
            # -------------------------------------------

    def process_packet(self, pkt):
        # return if no packet
        if not pkt: return

        # return when sniffing a packet that was just injected
        if pkt[Ether].src == '00:ff:c6:a8:79:4D':#'4e:e4:d0:38:a1:c5':
            return

        # return if the packet originated from self
        if pkt[Ether].src == MAC_ADDR:
            print 'from self'
            return

        # return unchanged packet if broadcast addr
        if pkt[Ether].dst == 'ff:ff:ff:ff:ff:ff':
            print 'broadcast'

        # if ARP in pkt:
        #     pkt[Ether].src = 'ac:18:26:4b:18:23'
        #     pkt[Ether].dst = '52:33:b7:53:b6:80'
        #     print 'arp'
        #     pkt[ARP].hwdst = '52:33:b7:53:b6:80'
        #     pkt[ARP].pdst = '192.168.2.135'
        #     return pkt

        else:
            # pkt[Ether].src = 'ac:18:26:4b:18:23'
            pkt[Ether].dst = '00:ff:c6:a8:79:4D'#'4e:e4:d0:38:a1:c5'
            if IP in pkt:
                # pkt[IP].src = '192.168.2.133'
                pkt[IP].dst = '192.168.2.131'

        pkt = [ord(c) for c in str(pkt)]
        thread.start_new_thread(POST, (pkt, IP_ADDRESS))