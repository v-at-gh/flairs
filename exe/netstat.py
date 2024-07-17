#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

class ArgHelp:
    resolve   = "resolve host names"
    numeric   = "don't resolve service names"
    all       = "display all sockets"
    listening = "display listening sockets"
    processes = "show process using socket"
    tcp       = "display only TCP sockets"
    udp       = "display only UDP sockets"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-r', '--resolve', action='store_true', help=ArgHelp.resolve)
    parser.add_argument('-n', '--numeric', action='store_true', help=ArgHelp.numeric)
    parser.add_argument('-a', '--all', action='store_true', help=ArgHelp.all)
    parser.add_argument('-l', '--listening', action='store_true', help=ArgHelp.listening)
    parser.add_argument('-p', '--processes', action='store_true', help=ArgHelp.processes)
    parser.add_argument('-t', '--tcp', action='store_true', help=ArgHelp.tcp)
    parser.add_argument('-u', '--udp', action='store_true', help=ArgHelp.udp)

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    #TODO: implement further processing logic using 
    # from src.Utils.Netstat

if __name__ == '__main__':
    main()
