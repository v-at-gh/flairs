import json
from typing import Any, Optional, Union
from dataclasses import dataclass, asdict, field
from ipaddress import IPv4Address, IPv6Address, ip_address
from subprocess import CompletedProcess, run
from copy import copy
from time import time as now

NETSTAT_BINARY = '/usr/sbin/netstat'
SUPPORTED_PROTOS = ('divert', 'icmp', 'igmp', 'ip', 'tcp', 'udp')
SUPPORTED_FAMILIES = ('inet', 'inet6', 'unix', 'vsock')

# Real TCP states
TCP_States = (
    'ESTABLISHED', 'SYN_SENT', 'SYN_RECEIVED',
    'FIN_WAIT_1', 'FIN_WAIT_2', 'TIME_WAIT',
    'CLOSED', 'CLOSE_WAIT', 'LAST_ACK',
    'LISTEN', 'CLOSING', 'NONE'
)

# (Imaginary UDP states)
UDP_States = (
    'ESTABLISHED', 'LISTEN', 'NONE'
)

# Active Internet connections
INET_Headers = (
    'Proto', 'Recv-Q', 'Send-Q',
    'Local Address', 'Foreign Address', '(state)',
    'rxbytes', 'txbytes', 'rhiwat', 'shiwat',
    'pid', 'epid',
    'state', 'options', 'gencnt',
    'flags', 'flags1',
    'usscnt', 'rtncnt', 'fltrs'
)

# Active Multipath Internet connections
Multipath_Headers = (
    'Proto/ID', 'Flags',
    'Local Address', 'Foreign Address', '(state)'
)

# Active LOCAL (UNIX) domain sockets
UNIX_Headers = (
    'Address', 'Type', 'Recv-Q', 'Send-Q',
    'Inode', 'Conn', 'Refs', 'Nextref',
    'rxbytes', 'txbytes', 'rhiwat', 'shiwat',
    'pid', 'epid', 'Addr'
)

# Registered kernel control modules
Registered_kernel_control_modules_Headers = (
    'id', 'flags', 'pcbcount', 'rcvbuf', 'sndbuf', 'name'
)

# Active kernel event sockets
Active_kernel_event_sockets_Header = (
    'Proto', 'Recv-Q', 'Send-Q',
    'vendor', 'class', 'subcl',
    'rxbytes', 'txbytes',
    'rhiwat', 'shiwat',
    'pid', 'epid'
)

# Active kernel control sockets
Active_kernel_control_sockets_Headers = (
    'Proto', 'Recv-Q', 'Send-Q',
    'rxbytes', 'txbytes',
    'rhiwat', 'shiwat',
    'pid', 'epid',
    'unit', 'id', 'name'
)

def run_netstat(
        command_options: Optional[list] = None,
        # family: Optional[str] = None,
        # proto: Optional[str] = None
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
