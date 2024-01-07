#!/usr/bin/env python3

import unittest

from src.Netstat import Netstat

class TestNetstat(unittest.TestCase):

    def test_get_connections_by_proto(self):
        connections_all = Netstat.get_connections()
        connections_tcp = Netstat.get_connections(proto='tcp')
        connections_udp = Netstat.get_connections(proto='udp')
        self.assertEqual(len(connections_all), len(connections_tcp) + len(connections_udp))

        connections_all_copy = connections_all.copy()
        for connection in connections_tcp:
            connections_all_copy.remove(connection)
        self.assertEqual(connections_all_copy, connections_udp)

        connections_all_copy = connections_all.copy()
        for connection in connections_udp:
            connections_all_copy.remove(connection)
        self.assertEqual(connections_all_copy, connections_tcp)

    def test_get_connections_by_interface(self):
        interfaces = Netstat.get_interfaces()
        connections = Netstat.get_connections()

        for interface in interfaces:
            connections_by_interface = Netstat.get_connections_by_interface(interface.name)
            expected_connections = [connection for connection in connections if connection.localAddr in interface.addresses]

            self.assertEqual(connections_by_interface, expected_connections)

if __name__ == '__main__':
    unittest.main()
