import _winreg as reg
import win32file
import win32event
import pywintypes
import threading
import time

#============================ defines =========================================

## IPv4 configuration of your TUN interface (represented as a list of integers)
TUN_IPv4_ADDRESS    = [ 192,  168,2,131] ##< The IPv4 address of the TUN interface.
TUN_IPv4_NETWORK    = [ 192,  168,2,0] ##< The IPv4 address of the TUN interface's network.
TUN_IPv4_NETMASK    = [255,255,255,0] ##< The IPv4 netmask of the TUN interface.

## Key in the Windows registry where to find all network interfaces (don't change, this is always the same)
ADAPTER_KEY         = r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}'

## Value of the ComponentId key in the registry corresponding to your TUN interface.
TUNTAP_COMPONENT_ID = 'tap0901'

#============================ helpers =========================================

#=== tun/tap-related functions

def get_tuntap_ComponentId():
    '''
    \brief Retrieve the instance ID of the TUN/TAP interface from the Windows
        registry,

    This function loops through all the sub-entries at the following location
    in the Windows registry: reg.HKEY_LOCAL_MACHINE, ADAPTER_KEY

    It looks for one which has the 'ComponentId' key set to
    TUNTAP_COMPONENT_ID, and returns the value of the 'NetCfgInstanceId' key.

    \return The 'ComponentId' associated with the TUN/TAP interface, a string
        of the form "{A9A413D7-4D1C-47BA-A3A9-92F091828881}".
    '''
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, ADAPTER_KEY) as adapters:
        try:
            for i in xrange(10000):
                key_name = reg.EnumKey(adapters, i)
                with reg.OpenKey(adapters, key_name) as adapter:
                    try:
                        component_id = reg.QueryValueEx(adapter, 'ComponentId')[0]
                        if component_id == TUNTAP_COMPONENT_ID:
                            return reg.QueryValueEx(adapter, 'NetCfgInstanceId')[0]
                    except WindowsError, err:
                        pass
        except WindowsError, err:
            pass

def CTL_CODE(device_type, function, method, access):
    return (device_type << 16) | (access << 14) | (function << 2) | method;

def TAP_CONTROL_CODE(request, method):
    return CTL_CODE(34, request, method, 0)

TAP_IOCTL_SET_MEDIA_STATUS        = TAP_CONTROL_CODE( 6, 0)
TAP_IOCTL_CONFIG_TUN              = TAP_CONTROL_CODE(10, 0)

def openTunTap():
    '''
    \brief Open a TUN/TAP interface and switch it to TUN mode.

    \return The handler of the interface, which can be used for later
        read/write operations.
    '''

    # retrieve the ComponentId from the TUN/TAP interface
    componentId = get_tuntap_ComponentId()
    print('componentId = {0}'.format(componentId))

    # create a win32file for manipulating the TUN/TAP interface
    tuntap = win32file.CreateFile(
        r'\\.\Global\%s.tap' % componentId,
        win32file.GENERIC_READ    | win32file.GENERIC_WRITE,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_ATTRIBUTE_SYSTEM | win32file.FILE_FLAG_OVERLAPPED,
        None
    )
    print('tuntap      = {0}'.format(tuntap.handle))

    # have Windows consider the interface now connected
    win32file.DeviceIoControl(
        tuntap,
        TAP_IOCTL_SET_MEDIA_STATUS,
        '\x01\x00\x00\x00',
        None
    )

    # prepare the parameter passed to the TAP_IOCTL_CONFIG_TUN commmand.
    # This needs to be a 12-character long string representing
    # - the tun interface's IPv4 address (4 characters)
    # - the tun interface's IPv4 network address (4 characters)
    # - the tun interface's IPv4 network mask (4 characters)
    configTunParam  = []
    configTunParam += TUN_IPv4_ADDRESS
    configTunParam += TUN_IPv4_NETWORK
    configTunParam += TUN_IPv4_NETMASK
    configTunParam  = ''.join([chr(b) for b in configTunParam])

    # switch to TUN mode (by default the interface runs in TAP mode)
    # win32file.DeviceIoControl(
    #     tuntap,
    #     TAP_IOCTL_CONFIG_TUN,
    #     configTunParam,
    #     None
    # )

    # return the handler of the TUN interface
    return tuntap

#=== misc

def formatByteList(byteList):
    '''
    \brief Format a byte list into a string, which can then be printed.

    For example:
       [0x00,0x11,0x22] -> '(3 bytes) 001122'

    \param[in] byteList A list of integer, each representing a byte.

    \return A string representing the byte list.
    '''
    return '({0} bytes) {1}'.format(len(byteList),''.join(['%02x'%b for b in byteList]))

def carry_around_add(a, b):
    '''
    \brief Helper function for checksum calculation.
    '''
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(byteList):
    '''
    \brief Calculate the checksum over a byte list.

    This is the checksum calculation used in e.g. the ICMPv6 header.

    \return The checksum, a 2-byte integer.
    '''
    s = 0
    for i in range(0, len(byteList), 2):
        w = byteList[i] + (byteList[i+1] << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff