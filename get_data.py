#!/usr/bin/env python3

from src.Netstat import Netstat
from src.Process import Process

def get_data() -> list:
    connections = Netstat.get_connections()
    pids = Netstat.get_pids_of_processes_with_connections(connections)
    processes = [Process(pid) for pid in pids]
    processes_with_connections = []
    for process in processes:
        processes_with_connections.append(process.get_connections_of_this_process())
    return processes_with_connections

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Print current connection state in different formats.")
    parser.add_argument('--format', choices=['dict', 'json'],
                        default='json',
                        help="Output format (default: json)")
    args = parser.parse_args()
    data = get_data()

    if args.format == 'dict':
        from pprint import pprint
        pprint(data)
    elif args.format == 'json':
        from json import dumps
        print(dumps(data))

if __name__ == '__main__':
    main()
