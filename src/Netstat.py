import json
from typing import Any, Optional, Union
from dataclasses import dataclass, asdict, field
from ipaddress import IPv4Address, IPv6Address, ip_address
from subprocess import CompletedProcess, run
from copy import copy
from time import time as now

NETSTAT_BINARY = 'netstat'
SUPPORTED_PROTOS = ('divert', 'icmp', 'igmp', 'ip', 'tcp', 'udp')

TCP_States = (
    'ESTABLISHED', 'SYN_SENT', 'SYN_RECEIVED',
    'FIN_WAIT_1', 'FIN_WAIT_2', 'TIME_WAIT',
    'CLOSED', 'CLOSE_WAIT', 'LAST_ACK',
    'LISTEN', 'CLOSING', 'NONE'
)

UDP_States = (
    'ESTABLISHED', 'LISTEN', 'NONE'
)

# def cast_value(value: Any, target_type:
#      Union[int, float, str, IPv4Address, IPv6Address]
# ) -> Union[int, float, str, IPv4Address, IPv6Address]:
#     if target_type == Union[IPv4Address, IPv6Address]: return ip_address(value)
#     elif target_type == int:
#         if isinstance(value, int): return value
#         else: return int(value.replace(',', ''))
#     elif target_type == float: return float(value)
#     elif target_type == str:   return str(value)

# class Connection_Processor:

#     @classmethod
#     def parse_str(cls, obj_str: str):
#         obj_list = obj_str.split()
#         resulting_obj_list = []
#         fields = list(cls.__annotations__.values())
#         # cls.__name__


#     @property
#     def as_dict(self) -> dict[str, Any]:
#         return asdict(self)

#     def to_json(self) -> str:
#         obj = copy(self.as_dict)
#         for k, v in self.as_dict.items():
#             if isinstance(v, (IPv4Address, IPv6Address)):
#                 obj[k] = str(v)
#         return json.dumps(obj)


# @dataclass
# class Base_Connection(Connection_Processor):
#     family: int
#     proto: str
#     recv_q: int
#     send_q: int
#     local_address: Union[IPv4Address, IPv6Address]
#     local_port: int
#     foreign_address: Union[IPv4Address, IPv6Address]
#     foreign_port: int
#     state: str
#     rxbytes: int
#     txbytes: int
#     rhiwat: int
#     shiwat: int
#     pid: int
#     epid: int
#     state_bits: str
#     options: str
#     gencnt: str
#     flags: str
#     flags1: str
#     usscnt: int
#     rtncnt: int
#     fltrs: str
# class TCP_Connection(Base_Connection):
#     __annotations__ = Base_Connection.__annotations__
# class UDP_Connection(Base_Connection):
#     __annotations__ = Base_Connection.__annotations__


# class Netstat_Processor:

#     @staticmethod
#     def parse_page(page: str):
#         netstat_out_lines = page.strip().splitlines()
#         connection_classes = {'tcp': TCP_Connection, 'udp': UDP_Connection}
#         proto = netstat_out_lines[0].lower()
#         proto = next(
#             (protocol_name for protocol_name in SUPPORTED_PROTOS if proto.startswith(protocol_name)),
#             proto
#         )

#         netstat_out_obj = netstat_out_lines
#         return netstat_out_obj

def run_netstat(
        family: Optional[str] = None,
        proto: Optional[str] = None
) -> CompletedProcess[str]:

    command = [NETSTAT_BINARY, '-n', '-f', 'inet', '-l', '-v', '-a', '-b']
    if proto and proto.lower() in SUPPORTED_PROTOS:
        proto = proto.lower()
        command.extend(['-p', proto])
    if family:
        command.extend(['-f', family])

    #TODO wrap `netstat` invokation to a helper function
    # , so it returns a timestamp, and [optionally] info about processes
    # utilizing network sockets, like in Linux version of `ss`/`netstat`
    timestamp = now()
    result = run(
        command,
        capture_output=True, text=True,
    )
    return result
    # return (timestamp, result)
