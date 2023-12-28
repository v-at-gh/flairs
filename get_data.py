#!/usr/bin/env python3

from src.Netstat import Netstat
from src.Process import Process

def get_data():

    connections = Netstat.get_connections()
    pids = Netstat.get_connection_pids(connections)
    processes = [Process(pid) for pid in pids]

    processes_with_connections = []
    for process in processes:
        processes_with_connections.append(process.get_connections_of_process())

    return processes_with_connections

def main():
    # If this file is executed directly, then return the state of the current connections:
    #   in dict representation if `--format dict` argument is passed
    #   in json representation if `--format json` argument is passed
    import argparse
    parser = argparse.ArgumentParser(description="Print current connection state in different formats.")
    parser.add_argument('--format', choices=['dict', 'json'],
                        default='json', help="Output format (default: json)")

    args = parser.parse_args()

    data = get_data()

    if args.format == 'dict':
        print(data)
    elif args.format == 'json':
        from json import dumps
        print(dumps(data))

if __name__ == '__main__':
    main()