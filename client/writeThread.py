import ast

from scapy.all import *
import threading

from pytun import TunTapDevice, IFF_TAP, IFF_NO_PI
tap = TunTapDevice(name='myTun', flags=(IFF_TAP| IFF_NO_PI))



class WriteThread(threading.Thread):
    def __init__(self, q):
        super(WriteThread, self).__init__()
        self.q = q
        tap.addr = '192.168.2.136'
        tap.dstaddr = '192.168.2.133'
        tap.netmask = '255.255.255.0'
        tap.hwaddr = '\x4e\xe4\xd0\x38\xa1\xc5'
        tap.mtu = 1500
        tap.up()

    def run(self):
        while 1:
            if not self.q: continue
            p = ast.literal_eval(ast.literal_eval(self.q.get()))
            p = ''.join([chr(i) for i in p])
            # p = Raw(p)

            # sendp(p, iface='enp0s25')
            tap.write(p)