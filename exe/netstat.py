#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-r', '--resolve', action='store_true', help="resolve host names")
    parser.add_argument('-n', '--numeric', action='store_true', help="don't resolve service names")
    parser.add_argument('-a', '--all', action='store_true', help="display all sockets")
    parser.add_argument('-l', '--listening', action='store_true', help="display listening sockets")
    parser.add_argument('-p', '--processes', action='store_true', help="show process using socket")
    parser.add_argument('-t', '--tcp', action='store_true', help="display only TCP sockets")
    parser.add_argument('-u', '--udp', action='store_true', help="display only UDP sockets")

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
