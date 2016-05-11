from scapy.all import *
import threading, thread
from scapy.layers.inet import IP

import sys, os, subprocess
# sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
from utils import *


IP_ADDRESS = '192.168.1.116'
try:
    MAC_ADDR = getHwAddr('myTun')
except IOError:
    print 'error creating'
    # os.system('ip link add name atum0 type dummy')
    # os.system('ifconfig atum0 up arp')
    # os.system('ifconfig atum0 192.168.2.135')


class SniffThread(threading.Thread):
    def __init__(self):
        super(SniffThread, self).__init__()

    def run(self):
        while 1:
            # Test packet generation --------
            # p = Ether() / IP() / 'Hello World'
            # time.sleep(2)
            # -------------------------------

            sniff(iface='myTun', prn=self.process_packet)


    def process_packet(self, pkt):
        # return if no packet
        if not pkt: return
        if not Ether in pkt: return pkt

        if pkt[Ether].src == 'ac:18:26:4b:18:23':
            return

        # return unchanged packet if broadcast addr
        if pkt[Ether].dst == 'ff:ff:ff:ff:ff:ff':
            print 'broadcast'
            # pkt[Ether].src = 'f0:de:f1:0b:c3:84'
            #
            # if ARP in pkt:
            #     pkt[ARP].hwsrc = 'f0:de:f1:0b:c3:84'
            #     pkt[ARP].psrc = '192.168.2.134'
            # print 'broadcast'
        else:
            pkt[Ether].dst = 'ac:18:26:4b:18:23'
            # pkt[Ether].src = '52:33:b7:53:b6:80'
            if IP in pkt:
                pkt[IP].dst = '192.168.2.133'
                # pkt[IP].src = '192.168.2.135'


        pkt = [ord(c) for c in str(pkt)]
        thread.start_new_thread(POST, (pkt, IP_ADDRESS))