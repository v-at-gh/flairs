#!/usr/bin/env python3
from subprocess import run

from src.Common import subprocess_run_args
from src.Netstat import Netstat


# test parsing of TCP connections
tcp_connections = Netstat.get_connections(proto='tcp')

bash_command_for_tcp = "netstat -nval -p tcp | grep '^tcp'"
tcp_connections_from_bash = run(bash_command_for_tcp, **subprocess_run_args).stdout.splitlines()

if len(tcp_connections) != len(tcp_connections_from_bash):
    print("There is a problem with TCP connections parsing:")
    print(f"  amount of connections parsed by this program: {len(tcp_connections)}")
    print(f"  amount of connections obtained conventionally: {len(tcp_connections_from_bash)}")
else:
    print('TCP connection parsing works.')

# test parsing of UDP connections
udp_connections = Netstat.get_connections(proto='udp')

bash_command_for_udp = "netstat -nval -p udp | grep '^udp'"
udp_connections_from_bash = run(bash_command_for_udp, **subprocess_run_args).stdout.splitlines()

if len(udp_connections) != len(udp_connections_from_bash):
    print("There is a problem with UDP connections parsing:")
    print(f"  amount of connections parsed by this program: {len(udp_connections)}")
    print(f"  amount of connections obtained conventionally: {len(udp_connections_from_bash)}")
else:
    print('UDP connection parsing works.')
