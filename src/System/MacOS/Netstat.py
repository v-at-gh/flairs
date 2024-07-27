# import json
from typing import Any, Optional, Union
from ipaddress import IPv4Address, IPv6Address
from dataclasses import dataclass, asdict
from subprocess import CompletedProcess, run
from time import time as now

NETSTAT_BINARY = '/usr/sbin/netstat'
SUPPORTED_PROTOS = ('divert', 'icmp', 'igmp', 'ip', 'tcp', 'udp')
SUPPORTED_FAMILIES = ('inet', 'inet6', 'unix', 'vsock')

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from tools import cast_value

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
        cv = [family, proto, cl[1], cl[2],
              laddr, lport, raddr, rport, state]
        # remove already processed items from initial list
        for _ in range(pop_count):
            cl.pop(0)
        cv.extend(cl)
        for i, (type, value) in enumerate(zip(init_class.__annotations__.values(), cv)):
            cv[i] = cast_value(value, type)
        return init_class(*cv)

    @property
    def lsock(self) -> str:
        return f"{str(self.laddr)}:{str(self.lport)}"

    @property
    def rsock(self) -> str:
        return f"{str(self.raddr)}:{str(self.rport)}"

@dataclass
class Base_Connection(Inet_Connection_Processor):
    family: str
    proto: str
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
    pid: int
    epid: int
    state_bits: str
    options: str
    gencnt: str
    flags: str
    flags1: str
    usscnt: int
    rtncnt: int
    fltrs: str
class TCP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__
class UDP_Connection(Base_Connection): __annotations__ = Base_Connection.__annotations__

class Report:
    @staticmethod
    def process_report(report: str):
        for line in report.strip().splitlines():
            if line.startswith(('tcp', 'udp')):
                conn = Base_Connection.parse_str(line)
                print(f"{conn.pid} {conn.proto} {conn.state} {conn.state_bits} {conn.lsock} <> {conn.rsock}")

def run_netstat(
        command_options: Optional[list] = None,
) -> CompletedProcess[str]:

    command = [NETSTAT_BINARY, '-n', '-l', '-v', '-a', '-b', '-W']
    # options validation and pre-processing is in the executable script now
    if command_options: command.extend(command_options)

    # timestamp = now()
    result = run(
        command,
        capture_output=True, text=True,
    )
    return result
    # return (timestamp, result)

if __name__ == '__main__':
    Report.process_report(run_netstat().stdout)
