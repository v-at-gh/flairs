#!/usr/bin/env python3

from typing import List
from src.Netstat import Netstat
from src.Connection import Net_Connection

def get_connections() -> List[Net_Connection]:
    connections = Netstat.get_connections()
    connections.sort(key=lambda c: c.pid)
    return connections

def print_connections():
    for connection in get_connections():
        print(connection.to_csv())

def main():
    print_connections()

if __name__ == '__main__':
    main()