#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

class ArgHelp:
    resolve   = "resolve host names"
    numeric   = "don't resolve service names"
    all       = "display all sockets"
    listening = "display listening sockets"
    processes = "show process using socket"
    ipv4      = "display only IPv4 sockets"
    ipv6      = "display only IPv6 sockets"
    tcp       = "display only TCP sockets"
    udp       = "display only UDP sockets"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    # parser.add_argument('-r', '--resolve', action='store_true', help=ArgHelp.resolve)
    # parser.add_argument('-n', '--numeric', action='store_true', help=ArgHelp.numeric)
    # parser.add_argument('-a', '--all', action='store_true', help=ArgHelp.all)
    # parser.add_argument('-l', '--listening', action='store_true', help=ArgHelp.listening)
    # parser.add_argument('-p', '--processes', action='store_true', help=ArgHelp.processes)
    parser.add_argument('-4', '--ipv4', action='store_true', help=ArgHelp.ipv4)
    parser.add_argument('-6', '--ipv6', action='store_true', help=ArgHelp.ipv6)
    parser.add_argument('-t', '--tcp', action='store_true', help=ArgHelp.tcp)
    parser.add_argument('-u', '--udp', action='store_true', help=ArgHelp.udp)

    return parser.parse_args()

def main() -> None:
    import sys
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    if args.tcp and args.udp:       transport = None
    elif args.tcp and not args.udp: transport = 'tcp'
    elif not args.tcp and args.udp: transport = 'udp'
    else: transport = None

    if args.ipv4 and args.ipv4:       family = None
    elif args.ipv4 and not args.ipv6: family = 'inet'
    elif not args.ipv4 and args.ipv6: family = 'inet6'
    else: family = None

    from src.Netstat import run_netstat

    try:
        result = run_netstat(family=family, proto=transport)
        print(result.stdout.strip(), file=sys.stdout)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        sys.exit(result.returncode)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()
