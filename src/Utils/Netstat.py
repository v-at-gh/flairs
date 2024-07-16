from typing import List, Optional
from dataclasses import dataclass, field
from subprocess import run

from ipaddress import ip_address

from .Common import subprocess_run_kwargs
from .Connection import Net_Connection, TCP_Connection, UDP_Connection

protos = ('tcp', 'udp')
families = ('inet', 'inet6')

@dataclass
class Interface:
    name: str
    addresses: List[str] = field(default_factory=list)

class Netstat:

    @staticmethod
    def get_interfaces() -> List[Interface]:
        command = "netstat -inl"
        lines = [
            line.split() for line in
            run(command, **subprocess_run_kwargs).stdout.splitlines()[1:]
        ]
        lines = [
            line for line in lines
            if len(line) == 9 and not line[2].startswith('<Link')
        ]
        interfaces = []
        for iface in set([line[0] for line in lines]):
            iface = Interface(
                name=iface,
                addresses=[line[3] for line in lines if line[0] == iface]
            )
            interfaces.append(iface)
        return interfaces

    @staticmethod
    def _run_netstat_to_get_connections(
            proto: Optional[str] = None,
            family: Optional[str] = None
        ) -> List[str]:
        proto_selector = f'-p {proto}' if proto is not None else ''
        family_selector = f'-f {family}' if family is not None else ''
        netstat_command = f"netstat -nval {family_selector} {proto_selector}"
        netstat_out = run(netstat_command, **subprocess_run_kwargs).stdout
        netstat_lines = netstat_out.splitlines()
        return netstat_lines

    @staticmethod
    def _parse_netstat_connection(
            netstat_connection_line: str
        ) -> Net_Connection:
        connection_classes = {'tcp': TCP_Connection, 'udp': UDP_Connection}
        proto = netstat_connection_line.split()[0].lower()
        proto = next(
            (protocol_name for protocol_name in protos if proto.startswith(protocol_name)),
            proto
        )
        parse_connection = connection_classes[proto]
        connection = parse_connection(*netstat_connection_line.split())
        return connection

    @staticmethod
    def get_connections(
            proto: Optional[str] = None,
            family: Optional[str] = None,
            netstat_lines: Optional[List[str]] = None
        ) -> List[Net_Connection]:
        if netstat_lines is None:
            netstat_lines = Netstat._run_netstat_to_get_connections(proto, family)
        connections = [
            Netstat._parse_netstat_connection(line) for line
            in netstat_lines if line.startswith(protos)
        ]
        return connections

    @staticmethod
    def get_pids_of_processes_with_connections(
        connections: Optional[List[Net_Connection]] = None
    ) -> List[int]:
        if connections is None:
            connections = Netstat.get_connections()
        pids = sorted(set(connection.pid for connection in connections))
        return pids

    @staticmethod
    def get_connections_by_interface(
        interface: str,
        connections: Optional[List[Net_Connection]] = None
    ) -> List[Net_Connection]:
        if connections is None:
            connections = Netstat.get_connections()
        try:
            ip_address(interface)
            connections_by_interface = [
                connection for connection in connections
                if connection.localAddr == interface
            ]
        except ValueError:
            connections_by_interface = []
            for iface in Netstat.get_interfaces():
                if iface.name == interface:
                    connections_by_interface.extend(
                        [
                            connection for connection in connections
                            if connection.localAddr in iface.addresses
                        ]
                    )
        return connections_by_interface
