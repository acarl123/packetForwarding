from scapy.all import *
import threading



class WriteThread(threading.Thread):
    def __init__(self, q):
        self.q = q

    def run(self):
        while 1:
            if not self.q: continue

            p = Raw(self.q.get())
            sendp(p, iface='atum0')
