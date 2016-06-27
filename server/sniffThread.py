import pywintypes
import win32event
from scapyxp.all import *
import threading, thread
from scapyxp.layers.inet import IP
import binascii
from windowsUtils import *

import sys, os, subprocess
# sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
sys.path.append('C:\\Users\\Atumsoft\\PycharmProjects\\packetForwarding')
from server.scapyxp.layers.l2 import Ether
from utils import *
from writeThread import WindowsWriteThread

IP_ADDRESS = '192.168.50.31'
# try:
#     MAC_ADDR = getHwAddr('eth9')
# except IOError:
#     print 'error creating'
#     # os.system('ip link add name atum0 type dummy')
#     # os.system('ifconfig atum0 up arp')
#     # os.system('ifconfig atum0 192.168.2.135')


class SniffThread(threading.Thread):
    ETHERNET_MTU = 1500
    IPv6_HEADER_LENGTH = 40
    IPV6_SRC_INDEXES = [x for x in xrange(22, 38)]
    IPV6_DST_INDEXES = [x for x in xrange(38, 54)]
    IPV4_INDEXES = [x for x in xrange(26, 34)]
    ETH_INDEXES = [x for x in xrange(0, 12)]

    def __init__(self, tapDev=None, transmit=WindowsWriteThread):
        super(SniffThread, self).__init__()
        # store params
        self.tuntap = tapDev
        self.transmit = transmit

        # local variables
        self.goOn = True
        self.overlappedRx = pywintypes.OVERLAPPED()
        self.overlappedRx.hEvent = win32event.CreateEvent(None, 0, 0, None)

        # initialize parent
        threading.Thread.__init__(self)

        # give this thread a name
        self.name = 'readThread'

    def run(self):
        rxbuffer = win32file.AllocateReadBuffer(self.ETHERNET_MTU)
        while 1:
            # Test packet generation --------
            # p = Ether(dst='ac:18:26:4b:18:23') / IP() / 'Hello World'
            # self.process_packet(p)
            # time.sleep(2)
            # -------------------------------

            # sniff(iface='eth5', prn=self.process_packet)

            # buf = self.tap.read(self.tap.mtu)
            # thread.start_new_thread(POST, (buf, IP_ADDRESS))
            l, bytes = win32file.ReadFile(self.tuntap, rxbuffer, self.overlappedRx)
            win32event.WaitForSingleObject(self.overlappedRx.hEvent, win32event.INFINITE)
            self.overlappedRx.Offset = self.overlappedRx.Offset + len(bytes)

            # convert input from a string to a byte list
            p = [(ord(b)) for b in bytes]

            # parse received packet
            # p = p[:12] + p[16:20] + p[12:16] + p[20:]
            # pkt = p[:]
            if (p[0]&0xf0)==0x40:
                # IPv4

                # keep only IPv4 packet
                total_length = 256*p[2]+p[3]
                p = p[:total_length]
                self.process(p)

    def process(self, pkt):
        try:
            # don't replace broadcast packets
            broadcast = binascii.unhexlify('ff:ff:ff:ff:ff:ff'.replace(':', ''))
            broadcast = [(ord(c)) for c in broadcast]
            if broadcast == pkt[0:6]:
                print 'broadcast'

            # replace ether layer
            etherSrc = binascii.unhexlify('00:ff:c6:a8:79:4D'.replace(':', ''))
            etherDst = binascii.unhexlify('4e:e4:d0:38:a1:c5'.replace(':', ''))
            etherAddrs = [(ord(c)) for c in etherDst + etherSrc]
            for (index, replacement) in zip(self.ETH_INDEXES, etherAddrs):
                pkt[index] = replacement
            thread.start_new_thread(POST, (pkt, IP_ADDRESS))

            # if  hex(pkt[14]) == '0x45': # ipv4 packet
            #     ipSrc =socket.inet_aton('169.254.11.86')
            #     ipDst = socket.inet_aton('169.254.11.85')
            #     ipAddrs = [(ord(c)) for c in ipSrc+ipDst]
            #     for (index, replacement) in zip(self.IPV4_INDEXES, ipAddrs):
            #         pkt[index] = replacement
            #
            # elif hex(pkt[14]) == '0x60': # ipv6 packet:
            #
            #     # Convert and replace ipv6 addresses
            #     ipv6Src = ipaddr.IPv6Address('fe80::f2de:f1ff:fe0b:c384').exploded.replace(':','')
            #     ipv6SrcHex = ''
            #     for (char1, char2) in zip(ipv6Src[0::2], ipv6Src[1::2]):
            #         ipv6SrcHex += chr(int(char1+char2, 16))
            #     ipv6SrcHex = [(ord(c)) for c in ipv6SrcHex]
            #     for (index, replacement) in zip(self.IPV6_SRC_INDEXES, ipv6SrcHex):
            #         pkt[index] = replacement
            #
            #     ipv6Dst = ipaddr.IPv6Address('fe80::ae18:26ff:fe4b:1823').exploded.replace(':','')
            #     ipv6DstHex = ''
            #     for (char1, char2) in zip(ipv6Dst[0::2], ipv6Dst[1::2]):
            #         ipv6DstHex += chr(int(char1 + char2, 16))
            #     ipv6DstHex = [(ord(c)) for c in ipv6DstHex]
            #     for (index, replacement) in zip(self.IPV6_DST_INDEXES, ipv6DstHex):
            #         pkt[index] = replacement
        except Exception, e:
            print e.message

    def process_packet(self, pkt):
        # return if no packet
        if not pkt: return
        if not Ether in pkt: return pkt

        if pkt[Ether].src == '4e:e4:d0:38:a1:c5':#'ac:18:26:4b:18:23':
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
            pkt[Ether].dst = '4e:e4:d0:38:a1:c5'#'ac:18:26:4b:18:23'
            # pkt[Ether].src = '52:33:b7:53:b6:80'
            if IP in pkt:
                pkt[IP].dst = '192.168.2.136'
                # pkt[IP].src = '192.168.2.135'


        pkt = [ord(c) for c in str(pkt)]
        thread.start_new_thread(POST, (pkt, IP_ADDRESS))