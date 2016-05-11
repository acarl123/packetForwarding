import ast

from flask import Flask, request
from flask.ext.api import status
import Queue
import os, sys
from pytun import TunTapDevice, IFF_TAP, IFF_NO_PI

sys.path.append('/home/atumsoft/PycharmProjects/packetForwarding/')
from utils import *

from sniffThread import SniffThread
from writeThread import WriteThread
tap = TunTapDevice(name='myTun', flags=(IFF_TAP| IFF_NO_PI))


inputQ = Queue.Queue()
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', defaults={'path': ''},methods=['POST'])
@app.route('/<path:path>',methods=['POST'])
def main(path, *args, **kwargs):
    # inputQ.put(request.data)
    p = ast.literal_eval(ast.literal_eval(request.data))
    p = ''.join([chr(i) for i in p])
    tap.write(p)
    return request.data, status.HTTP_200_OK


if __name__ == '__main__':
    tap.addr = '192.168.2.136'
    tap.dstaddr = '192.168.2.133'
    tap.netmask = '255.255.255.0'
    tap.hwaddr = '\x4e\xe4\xd0\x38\xa1\xc5'
    tap.mtu = 1500
    tap.up()

    sniffer = SniffThread(tap)
    sniffer.setDaemon(True)
    sniffer.start()

    # writer = WriteThread(inputQ)
    # writer.setDaemon(True)
    # writer.start()

    app.debug = False
    app.run(host='0.0.0.0')
