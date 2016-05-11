import ast

from scapy.all import *
import threading



class WriteThread(threading.Thread):
    def __init__(self, q):
        super(WriteThread, self).__init__()
        self.q = q

    def run(self):
        while 1:
            if not self.q: continue
            p = ast.literal_eval(ast.literal_eval(self.q.get()))
            p = ''.join([chr(i) for i in p])
            p = Raw(p)

            sendp(p, iface='mytun')
