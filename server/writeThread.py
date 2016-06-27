import ast

from scapy.all import *
import threading
from windowsUtils import *
import requests
import binascii



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

            sendp(p, iface='eth5')

class WindowsWriteThread(threading.Thread):
    '''
    \brief Thread with periodically sends IPv4 and IPv6 echo requests.
    '''

    SLEEP_PERIOD   = 1

    def __init__(self,tuntap,inputq):

        # store params
        self.tuntap               = tuntap
        self.inputq               = inputq

        # local variables
        self.goOn                 = True
        self.createIPv6           = False
        self.overlappedTx         = pywintypes.OVERLAPPED()
        self.overlappedTx.hEvent  = win32event.CreateEvent(None, 0, 0, None)

        # initialize parent
        threading.Thread.__init__(self)

        # give this thread a name
        self.name                 = 'writeThread'

    def run(self):

        while self.goOn:

            # # sleep a bit
            # time.sleep(self.SLEEP_PERIOD)
            #
            # # create an echo request
            # dataToTransmit = self._createEchoRequest()

            if not self.inputq:
                pass
                # time.sleep(self.SLEEP_PERIOD)
                # dataToTransmit = self._createEchoRequest()
            else:

                # need to fix this...
                dataToTransmit = ast.literal_eval(ast.literal_eval(self.inputq.get()))

                # remove 14 byte header that was added
                dataToTransmit = dataToTransmit
                # print 'Packet: %s' % dataToTransmit

                # with open('testfile.txt', 'a+') as outfile:
                #     outfile.write( str(hexdump(''.join([chr(b) for b in dataToTransmit]))) )
                #     outfile.write( '\n\n\n' )

                # transmit
                self.transmit(dataToTransmit)

    #======================== public ==========================================

    def close(self):
        self.goOn = False

    def transmit(self,dataToTransmit,echo=True):
        # remove old headers
        # dataToTransmit = dataToTransmit[28:]
        MacAddrs = binascii.hexlify(''.join([chr(s) for s in dataToTransmit[:14]]))
        data  = ''.join([chr(b) for b in dataToTransmit])
        # data = Raw(b'%s' % data)
        # with open('test.log', 'a') as logfile:
        #     logfile.write('\n%s\n' % (MacAddrs))
        # data = IP()/UDP()/(b'%s' % data)
        # data = str(data)

        # write over tuntap interface

        win32file.WriteFile(self.tuntap, data, self.overlappedTx)
        win32event.WaitForSingleObject(self.overlappedTx.hEvent, win32event.INFINITE)
        self.overlappedTx.Offset = self.overlappedTx.Offset + len(data)

        # sendp(data, iface='eth9')