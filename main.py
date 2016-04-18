from scapy.all import *
from threading import Thread


def send(data, iface):
    sendp(data, iface=iface)

def sniffLocal():
    while 1:
        p = sniff(iface='atum0', count=1)
        thr = Thread(target=send, args=(p, 'enp0s3'))
        thr.setDaemon(True)
        thr.start()

def main():
    sniffOther = Thread(target=sniffLocal)
    sniffOther.setDaemon(True)
    sniffOther.start()
    while 1:
        p = sniff(iface='enp0s3', count=1)
        thr = Thread(target=send, args=(p,'atum0'))
        thr.setDaemon(True)
        thr.start()


main()