from subprocess import run

from .Common import subprocess_run_args
from .Connection import TCP_Connection, UDP_Connection

protos = ('tcp', 'udp')
families = ('inet', 'inet6')

class Netstat:

    def _run_netstat(
            proto: protos = None,
            family: families = None
        ) -> list[str]:
        proto_selector = '-p ' + proto if proto is not None else ''
        family_selector = '-f ' + family if family is not None else ''

        netstat_command = f"netstat -nval {family_selector} {proto_selector}"
        netstat_out = run(netstat_command, **subprocess_run_args).stdout
        netstat_lines = netstat_out.splitlines()

        return netstat_lines

    def _parse_netstat_connection(
            netstat_connection_line: str
        ) -> TCP_Connection | UDP_Connection:
        Connection_Classes = {'tcp': TCP_Connection, 'udp': UDP_Connection}
        proto = netstat_connection_line.split()[0]

        for protocol_name in protos:
            if proto.startswith(protocol_name):
                proto = protocol_name
        Parse_Connection = Connection_Classes[proto]
        connection = Parse_Connection(*netstat_connection_line.split())

        return connection

    @staticmethod
    def get_connections(
            proto: protos = None,
            family: families = None,
            netstat_lines: str = None
        ) -> list[TCP_Connection | UDP_Connection]:
        if netstat_lines is None:
            netstat_lines = Netstat._run_netstat(family, proto)

        connections = []
        for line in netstat_lines:
            if line.startswith(protos):
                connection = Netstat._parse_netstat_connection(line)
                connections.append(connection)

        return connections

    @staticmethod
    def get_connection_pids(connections=None) -> list[int]:
        if connections is None:
            connections = Netstat.get_connections()
        pids = sorted(set([connection.pid for connection in connections]))
        return pids