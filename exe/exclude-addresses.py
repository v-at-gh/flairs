#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('network', type=str, help="Network from which we are excluding addresses")
    parser.add_argument('-a', '--addresses', type=str, help="comma or whitespace separated addresses of hosts and/or networks to be excluded")

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    from ipaddress import IPv4Network, IPv6Network
    from src.exclude_addresses import exclude_addresses

    result = exclude_addresses(args.network, args.addresses)
    if isinstance(result, (IPv4Network, IPv6Network)):
        print(result)
    else:
        result_str = "\n".join(str(n) for n in result)
        print(result_str)

if __name__ == '__main__':
    main()
