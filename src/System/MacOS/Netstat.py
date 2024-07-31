# import json
from typing import Any, Optional, Union
from ipaddress import IPv4Address, IPv6Address
from dataclasses import dataclass, asdict
from subprocess import CompletedProcess, run
import json
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
            proto = 'TCP'; init_class = TCP_Connection; pop_count = 6
            state = cl[5]
        elif cl[0].startswith('udp'):
            proto = 'UDP'; init_class = UDP_Connection; pop_count = 5
            if   cl[11] == '00100': state = 'LISTEN'
            elif cl[11] == '00102': state = 'ESTABLISHED'
            else: state = 'UNKNOWN'
        if   cl[0].endswith('4'): family = 'IPv4'
        elif cl[0].endswith('6'): family = 'IPv6'
        laddr, lport = cl[3].rsplit('.', 1)
        raddr, rport = cl[4].rsplit('.', 1)
        if laddr == '*':
            if   family == 'IPv4': laddr = '0.0.0.0'
            elif family == 'IPv6': laddr = '::'
        if raddr == '*':
            if   family == 'IPv4': raddr = '0.0.0.0'
            elif family == 'IPv6': raddr = '::'
        if lport == '*': lport = '0'
        if rport == '*': rport = '0'
        cv = [family, proto, cl[1], cl[2], laddr, lport, raddr, rport, state]
        # remove already processed items from initial list
        for _ in range(pop_count): cl.pop(0)
        cv.extend(cl)
        for i, (type, value) in enumerate(zip(init_class.__annotations__.values(), cv)):
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

    def to_json(self) -> str:
        return json.dumps(self.to_stringified_dict())

    @classmethod
    def from_json(self): raise NotImplementedError

    def to_csv(self): raise NotImplementedError

    @classmethod
    def from_csv(self): raise NotImplementedError


@dataclass
class Base_Connection(Inet_Connection_Processor):
    family: str
    proto:  str
    recv_q: int
    send_q: int
    laddr: Union[IPv4Address, IPv6Address]
    lport: int
    raddr: Union[IPv4Address, IPv6Address]
    rport: int
    state: str
    rxbytes: int
    txbytes: int
    rhiwat: int
    shiwat: int
    pid:  int
    epid: int
    state_bits: str
    options: str
    gencnt:  str
    flags:  str
    flags1: str
    usscnt: int
    rtncnt: int
    fltrs:  str
class TCP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__
class UDP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__

#TODO: implement as `dataclass`
class Netstat_Inet_Report:

    def __init__(self):
        timestamp, conns = self.get_inet_snapshot()
        self.timestamp = timestamp
        self.connections = conns
        self.pids = set(c.pid for c in self.connections)

    @property
    def pids_of_connections(self) -> list[int]:
        return sorted(self.pids)

    @staticmethod
    def get_inet_snapshot(command_options: Optional[list] = None):
        timestamp = now(); result = Netstat_Inet_Report.run_netstat(command_options)
        #TODO: implement more delicate error-handling someday
        if result.returncode != 0: die(result.returncode, result.stderr)
        conns = Netstat_Inet_Report.process_inet_report(result.stdout)
        return (timestamp, conns)

    @staticmethod
    def process_inet_report(report: str) -> list[Union[TCP_Connection, UDP_Connection]]:
        return [Base_Connection.parse_str(line) for line in report.strip().splitlines() if line.startswith(('tcp', 'udp'))]

    @staticmethod
    def run_netstat(command_options: Optional[list] = None) -> CompletedProcess[str]:
        command = [NETSTAT_BINARY, '-n', '-l', '-v', '-a', '-b', '-W']
        if command_options: command.extend(command_options)
        result = run(command, capture_output=True, text=True, encoding='utf-8')
        return result

#TODO: define `Process` class as an object of process with network connections

def print_conns_dicts():
    conns = Netstat_Inet_Report.process_inet_report(Netstat_Inet_Report.run_netstat().stdout)
    # for c in conns: print(c.as_dict)
    # for c in conns: print(c.to_stringified_dict())
    # for c in conns: print(obj_to_stringified_dict(c))
    for c in conns: print(c.to_json())

if __name__ == '__main__':
    print_conns_dicts()
