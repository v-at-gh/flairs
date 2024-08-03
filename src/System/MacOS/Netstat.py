import json
from typing import Optional, Union
from ipaddress import IPv4Address, IPv6Address
from socket import (
    AddressFamily,
    AF_INET as AF_INET4,
    AF_INET6,
    SocketKind,
    SOCK_STREAM,
    SOCK_DGRAM
)
from dataclasses import dataclass, asdict, field
from subprocess import CompletedProcess, run
from time import time as now

NETSTAT_BINARY = '/usr/sbin/netstat'
SUPPORTED_PROTOS = ('divert', 'icmp', 'igmp', 'ip', 'tcp', 'udp')
SUPPORTED_FAMILIES = ('inet', 'inet6', 'unix', 'vsock')

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools import cast_value, die, obj_to_stringified_dict

class TCP_Connection: ...
class UDP_Connection: ...

class Inet_Connection_Processor:
    @classmethod
    def parse_str(cls, conn_str: str) -> Union[TCP_Connection, UDP_Connection]:
        cl = [i.strip() for i in conn_str.split()]
        if   cl[0].startswith('tcp'):
            proto = SOCK_STREAM; init_class = TCP_Connection; pop_count = 6
            state = cl[5]
        elif cl[0].startswith('udp'):
            proto = SOCK_DGRAM; init_class = UDP_Connection; pop_count = 5
            if   cl[11] == '00100': state = 'LISTEN'
            elif cl[11] == '00102': state = 'ESTABLISHED'
            else: state = 'UNKNOWN'
        if   cl[0].endswith('4'): family = AF_INET4
        elif cl[0].endswith('6'): family = AF_INET6
        laddr, lport = cl[3].rsplit('.', 1)
        raddr, rport = cl[4].rsplit('.', 1)
        if laddr == '*':
            if   family == AF_INET4: laddr = '0.0.0.0'
            elif family == AF_INET6: laddr = '::'
        if raddr == '*':
            if   family == AF_INET4: raddr = '0.0.0.0'
            elif family == AF_INET6: raddr = '::'
        if lport == '*': lport = '0'
        if rport == '*': rport = '0'
        cv = [family, proto, cl[1], cl[2], laddr, lport, raddr, rport, state]
        # remove already processed items from initial list
        for _ in range(pop_count): cl.pop(0)
        cv.extend(cl); del cl
        for i, (type, value) in enumerate(zip(
                init_class.__annotations__.values(), cv
        )):
            cv[i] = cast_value(value, type)
        return init_class(*cv)

    @property
    def lsock(self) -> str: return f"{str(self.laddr)}:{str(self.lport)}"
    @property
    def rsock(self) -> str: return f"{str(self.raddr)}:{str(self.rport)}"
    @property
    def sock_pair(self) -> str: return f"{self.lsock} <> {self.rsock}"

    @property
    def as_dict(self) -> dict[str, Union[int, str, IPv4Address, IPv6Address]]:
        return asdict(self)
    def to_stringified_dict(self) -> dict[str, Union[int, str]]:
        return obj_to_stringified_dict(self)

    @classmethod
    def from_json(cls): raise NotImplementedError
    def to_json(self) -> str: return json.dumps(self.to_stringified_dict())

    @classmethod
    def from_csv(cls): raise NotImplementedError
    def to_csv(self) -> str: return ','.join(str(v) for v in self.as_dict.values())


@dataclass
class Base_Connection(Inet_Connection_Processor):
    family: AddressFamily; proto: SocketKind
    recv_q: int; send_q: int
    laddr: Union[IPv4Address, IPv6Address]; lport: int
    raddr: Union[IPv4Address, IPv6Address]; rport: int
    state: str
    rxbytes:    int; txbytes: int
    rhiwat:     int;  shiwat: int
    pid:        int;    epid: int
    state_bits: str
    options: str
    gencnt:  str
    flags:   str; flags1: str
    usscnt:  int; rtncnt: int
    fltrs:   str
class TCP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__
class UDP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__

@dataclass
class Netstat_Inet_Report:
    timestamp: float
    connections: tuple[Union[TCP_Connection, UDP_Connection]]
    pids: set[int] = field(init=False)

    def __post_init__(self):
        self.pids = {c.pid for c in self.connections}

    @property
    def pids_csv(self) -> str:
        return ','.join(str(p) for p in self.pids)

    @classmethod
    def instantiate_report(cls):
        timestamp = now()
        connections = cls.process_inet_report()
        return cls(timestamp, connections)

    @property
    def udp_connections(self) -> tuple[UDP_Connection]:
        return tuple(filter(lambda c: c.proto == SOCK_DGRAM, self.connections))

    @property
    def tcp_connections(self) -> tuple[TCP_Connection]:
        return tuple(filter(lambda c: c.proto == SOCK_STREAM, self.connections))

    @property
    def pids_of_connections(self) -> list[int]: return sorted(self.pids)

    @staticmethod
    def process_inet_report(report: Optional[str] = None,
                 command_options: Optional[tuple] = None
    ):
        if not report:
            try:
                netstat = Netstat_Inet_Report.run_netstat(command_options)
                if netstat.returncode != 0: die(1, netstat.stderr)
                report = netstat.stdout
            except Exception as e: raise e
        return tuple(Base_Connection.parse_str(line) for
                     line in report.strip().splitlines()
                     if line.startswith(('tcp', 'udp')))

    @staticmethod
    def run_netstat(command_options: Optional[list] = None) -> CompletedProcess[str]:
        command = [NETSTAT_BINARY, '-n', '-l', '-v', '-a', '-b', '-W']
        if command_options: command.extend(command_options)
        result = run(command, capture_output=True, text=True, encoding='utf-8')
        return result

from time import time

def get_conns():
    return Netstat_Inet_Report.process_inet_report()

def print_conns_dicts(conns):
    for c in conns: print(c.to_json())
def print_conns_csvs(conns):
    for c in conns: print(c.to_csv())

def write_conns_dicts(conns):
    # "["+",".join(c.to_json() for c in conns)+"]"
    with open(f"netstat.{now}.json", "w", encoding="utf-8") as f:
        f.write("["+",".join(c.to_json() for c in conns)+"]")

def write_conns_csvs(conns):
    # for c in conns: print(c.to_csv())
    with open(f"netstat.{now}.csv", "w", encoding="utf-8") as f:
        f.write('\n'.join(c.to_csv() for c in conns)+'\n')

if __name__ == '__main__':
    report = Netstat_Inet_Report.instantiate_report()
    print(report.pids_csv)
    # print(report.tcp_connections)
    # print(report.udp_connections)
    # print(report.__dict__)
    # print(report.__dict__)

    # now = int(time())
    # conns = list(get_conns())

    # # print_conns_dicts()
    # write_conns_csvs(conns)
    # write_conns_dicts(conns)
