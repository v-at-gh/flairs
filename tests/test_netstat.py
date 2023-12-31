#!/usr/bin/env python3

import unittest

from src.Netstat import Netstat

class TestNetstat(unittest.TestCase):

    def test_get_connections(self):

        connections_all = Netstat.get_connections()
        connections_tcp = Netstat.get_connections(proto='tcp')
        connections_udp = Netstat.get_connections(proto='udp')

        self.assertEqual(len(connections_all), len(connections_tcp) + len(connections_udp))

        connections_all_copy = list(connections_all)
        for connection in connections_tcp:
            connections_all_copy.remove(connection)
        self.assertEqual(connections_all_copy, list(connections_udp))

        connections_all_copy = list(connections_all)
        for connection in connections_udp:
            connections_all_copy.remove(connection)
        self.assertEqual(connections_all_copy, list(connections_tcp))

if __name__ == '__main__':
    unittest.main()
