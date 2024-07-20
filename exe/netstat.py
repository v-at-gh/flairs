#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from typing import NoReturn
from argparse import ArgumentParser, Namespace

from src.tools import die
from src.System.MacOS.Netstat import SUPPORTED_FAMILIES, SUPPORTED_PROTOS, run_netstat

class ArgHelp:
    # all       = "display all sockets"
    # listening = "display listening sockets"
    ipv4      = "display only IPv4 family sockets"
    ipv6      = "display only IPv6 family sockets"
    tcp       = "display only TCP transport sockets"
    udp       = "display only UDP transport sockets"
    unix      = "display only unix sockets"
    # processes = "show process using socket (Default)"
    # numeric   = "don't resolve service names (Default)"
    # resolve   = "resolve host names"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    # parser.add_argument('-a', '--all', action='store_true', help=ArgHelp.all)
    # parser.add_argument('-l', '--listening', action='store_true', help=ArgHelp.listening)
    parser.add_argument('-4', '--ipv4', action='store_true', help=ArgHelp.ipv4)
    parser.add_argument('-6', '--ipv6', action='store_true', help=ArgHelp.ipv6)
    parser.add_argument('-t', '--tcp',  action='store_true', help=ArgHelp.tcp)
    parser.add_argument('-u', '--udp',  action='store_true', help=ArgHelp.udp)
    parser.add_argument('-x', '--unix', action='store_true', help=ArgHelp.unix)
    # parser.add_argument('-p', '--processes', action='store_true', help=ArgHelp.processes)
    # parser.add_argument('-n', '--numeric',   action='store_true', help=ArgHelp.numeric)
    # parser.add_argument('-r', '--resolve', action='store_true', help=ArgHelp.resolve)

    return parser.parse_args()

def main() -> NoReturn:
    args = parse_arguments()

    # TODO: yes, sir. Unlike the Linux version, 
    # the family and protocol flags in MacOS are mutually exclusive.
    # Implement an algorithm that would reproduce Linux behavior.

    if   args.ipv4   and   args.ipv6   and   args.unix: family = None
    elif args.ipv4 and not args.ipv6 and not args.unix: family = 'inet'
    elif args.ipv6 and not args.ipv4 and not args.unix: family = 'inet6'
    elif args.unix and not args.ipv4 and not args.ipv6: family = 'unix'
    else: family = None

    if   args.tcp   and   args.udp: transport = None
    elif args.tcp and not args.udp: transport = 'tcp'
    elif args.udp and not args.tcp: transport = 'udp'
    else: transport = None

    command_options = []
    if transport:
        transport = transport.lower().strip()
        if transport in SUPPORTED_PROTOS: command_options.extend(['-p', transport])
        else: raise Exception(
            f"Protocol {transport} is not supported. "
            f"Supported protos are: {' '.join(SUPPORTED_PROTOS)}")
    if family:
        family = family.lower().strip()
        if family in SUPPORTED_FAMILIES: command_options.extend(['-f', family])
        else: raise Exception(
            f"Family {family} is not supported. "
            f"Supported families are: {' '.join(SUPPORTED_FAMILIES)}")

    try:
        result = run_netstat(command_options=command_options)
        if not result.stderr:
              die(result.returncode, result.stdout.strip())
        else: die(result.returncode, result.stderr.strip())
    except Exception as e:
        die(result.returncode, f"An error occurred: {e}")

if __name__ == '__main__':
    main()
