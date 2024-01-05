# Not implemented yet.
'''
The purpose of this class is to provide methods for creating capture/preview filters for tcpdump/wireshark.
For exmaple:

-- tcpdump/tshark capture filter:
'not ((src host 1.1.1.1 and src udp port 443) or (dst host 1.1.1.1 and dst udp port 443))'

-- tshark/wireshark preview filter:
'not ((ip.src == 1.1.1.1 and udp.srcport == 443) or (ip.dst == 1.1.1.1 and udp.dstport == 443))'
'''

purposes = ('capture', 'preview')

from itertools import permutations
from .Netstat import Netstat

class Filter:
    ifaces = Netstat.get_interfaces()

    @staticmethod
    def return_capture_filter(
        purpose:purposes='capture',
        iface:ifaces=None,
        process=None,
        destination=None,
        proto=None
    ):
        capture_filter = ''
        return capture_filter
