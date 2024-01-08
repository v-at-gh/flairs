import unittest

from src.Filter import Filter

class TestNetstat(unittest.TestCase):

    def test_pcap_filters(self) -> None:

        self.assertEqual(
            'not ((src host 192.168.1.1 and tcp src port 80) or (dst host 192.168.1.1 and tcp dst port 80))',
            Filter.tcpdump_endpoint_filter(proto='tcp', addr='192.168.1.1', port=80)
        )
        self.assertEqual(
            '((src net 192.168.1.0/24 and udp src port 80) or (dst net 192.168.1.0/24 and udp dst port 80))',
            Filter.tcpdump_endpoint_filter(proto='udp', addr='192.168.1.0/24', port=80, filter_goal='include')
        )
        self.assertEqual(
            'not ((ip.src == 192.168.1.1 and udp.srcport == 80) or (ip.dst == 192.168.1.1 and udp.dstport == 80))',
            Filter.wireshark_endpoint_filter(proto='udp', addr='192.168.1.1', port=80)
        )
        self.assertEqual(
            'not ((ip.src == 192.168.1.0/24 and tcp.srcport == 80) or (ip.dst == 192.168.1.0/24 and tcp.dstport == 80))',
            Filter.wireshark_endpoint_filter(proto='tcp', addr='192.168.1.0/24', port=80)
        )

if __name__ == '__main__':
    unittest.main()
