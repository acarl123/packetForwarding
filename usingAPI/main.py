import os

import API
import API.AtumsoftServer as server
import API.AtumsoftUtils as utils


def main():
    tunTap = API.AtumsoftGeneric.AtumsoftGeneric()
    import pprint;pprint.pprint(tunTap.activeHosts)
    tunTap.createTunTapAdapter(name='mytun',ipAddress='192.168.2.100')
    tunTap.openTunTap()

    tunTap.startCapture()

if __name__ == '__main__':
    main()