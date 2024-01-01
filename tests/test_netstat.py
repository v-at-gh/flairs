#!/usr/bin/env python3

import unittest

from src.Netstat import Netstat

class TestNetstat(unittest.TestCase):

    def test_get_connections(self):

        connections_all = Netstat.get_connections()
        connections_tcp = Netstat.get_connections(proto='tcp')
        connections_udp = Netstat.get_connections(proto='udp')
        # #TODO 0: make family selector more flexible, eg: [4|6], [ipv4|ipv6], [inet4|inet6]
        # connections_ipv4 = Netstat.get_connections(family='inet')
        # connections_ipv6 = Netstat.get_connections(family='inet6')

        # self.assertEqual(len(connections_all), len(connections_ipv4) + len(connections_ipv6))
        # TODO 1: fix the bug:
        # '''
        # Traceback (most recent call last):
        # File "./tests/test_netstat.py", line 18, in test_get_connections
        #     self.assertEqual(len(connections_all), len(connections_ipv4) + len(connections_ipv6))
        # AssertionError: 79 != 80
        # '''

        self.assertEqual(len(connections_all), len(connections_tcp) + len(connections_udp))

        connections_all_copy = connections_all.copy()
        for connection in connections_tcp:
            connections_all_copy.remove(connection)

        self.assertEqual(connections_all_copy, connections_udp)

        connections_all_copy = connections_all.copy()
        for connection in connections_udp:
            connections_all_copy.remove(connection)

        self.assertEqual(connections_all_copy, connections_tcp)

if __name__ == '__main__':
    unittest.main()
