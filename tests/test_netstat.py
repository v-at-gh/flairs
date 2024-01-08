#!/usr/bin/env python3

import unittest

from src.Netstat import Netstat
from src.Filter import Filter

class TestNetstat(unittest.TestCase):

    def test_get_connections_by_proto(self) -> None:
        connections_all = Netstat.get_connections()
        connections_tcp = Netstat.get_connections(proto='tcp')
        connections_udp = Netstat.get_connections(proto='udp')

        self.assertEqual(len(connections_all), len(connections_tcp) + len(connections_udp))

        connections_all_copy = connections_all.copy()
        for connection in connections_tcp:
            connections_all_copy.remove(connection)

        self.assertEqual(
            sorted(connections_all_copy, key=lambda c: c.localPort),
            sorted(connections_udp, key=lambda c: c.localPort)
        )

        connections_all_copy = connections_all.copy()
        for connection in connections_udp:
            connections_all_copy.remove(connection)

        self.assertEqual(
            sorted(connections_all_copy, key=lambda c: c.localPort),
            sorted(connections_tcp, key=lambda c: c.localPort)
        )

    def test_get_connections_by_interface(self) -> None:
        # Sometimes this test may fail due to the fact
        # that the list of network connections changes
        # while performing data collection functions.
        #TODO: do not panic (as always) and try once again
        interfaces = Netstat.get_interfaces()
        connections = Netstat.get_connections()

        for interface in interfaces:
            connections_by_interface = Netstat.get_connections_by_interface(interface.name)
            expected_connections = [
                connection for connection in connections
                if connection.localAddr in interface.addresses
            ]

            self.assertEqual(
                sorted(connections_by_interface, key = lambda c: c.localPort),
                sorted(expected_connections, key = lambda c: c.localPort)
            )

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
