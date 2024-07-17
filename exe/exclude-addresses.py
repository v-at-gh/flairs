#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    network_help = "Network from which we are excluding addresses"
    addresses_help = "comma or whitespace separated addresses of hosts and/or networks to be excluded"
    separator_help = "separator for a list of resulting networks. Default is the new line"
    parser = ArgumentParser()
    parser.add_argument('network', type=str, help=network_help)
    parser.add_argument('-a', '--addresses', type=str, help=addresses_help)
    parser.add_argument('-s', '--separator', type=str, help=separator_help)

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    # This script solves the following problem:
    # https://codereview.stackexchange.com/questions/245922/ip-address-exclusion-algorithm
    # https://stackoverflow.com/questions/66204457/how-can-i-remove-two-or-more-subnet-from-a-network

    import sys
    from src.net_tools import exclude_addresses, is_string_a_valid_ip_network

    if not args.separator:
        separator = "\n"
    else:
        separator = str(args.separator)

    #TODO 1: Maybe implement the following as a new argument validation function?
    if not is_string_a_valid_ip_network(args.network):
        print(f"{args.network} is not a valid ip network 1.", file=sys.stderr)
        sys.exit(1)
    else:
        from ipaddress import ip_network
        target_network = ip_network(args.network)

    if not is_string_a_valid_ip_network(args.addresses):
        if not ',' in args.addresses:
            if not ' ' in args.addresses:
                print(f"{args.addresses} is not a valid ip network.", file=sys.stderr)
                sys.exit(2)
            addresses = set(a.strip() for a in args.addresses.split() if a.strip() != '')
        else:
            addresses = set(a.strip() for a in args.addresses.split(',') if a.strip() != '')
        #TODO 2: collect all invalid and misfitting addresses and inform user, instead of exiting at first error
        for a in addresses:
            if not is_string_a_valid_ip_network(a):
                print(f"{a} is not a valid ip address of network.", file=sys.stderr)
                sys.exit(3)
            net_a = ip_network(a)
            if not isinstance(net_a, type(target_network)):
                print(f"TypeError: {net_a} and {target_network} are not of the same version", file=sys.stderr)
                sys.exit(4)
            elif not net_a.subnet_of(target_network):
                print(f"{a} is not subnet of target network {target_network}.", file=sys.stderr)
                sys.exit(5)
        #TODO 0: seems like now the following part is not necessary. Think about it.
        resulting_networks_str = separator.join(
            str(n) for n in exclude_addresses(
                target_network, [net_a for a in addresses
                                 if net_a.subnet_of(target_network)]
            )
        )
        if len(resulting_networks_str) == 0:
            resulting_networks_str = target_network
        print(f"{resulting_networks_str}", file=sys.stdout)
        sys.exit(0)
    else:
        net_a = ip_network(args.addresses)
        if not isinstance(net_a, type(target_network)):
            print(f"TypeError: {net_a} and {target_network} are not of the same version", file=sys.stderr)
            sys.exit(4)
        if not net_a.subnet_of(target_network):
            if net_a.supernet_of(target_network):
                print(f"{target_network} is subnet of {net_a}", file=sys.stdout)
                sys.exit(5)
            elif not net_a.subnet_of(target_network):
                print(f"{net_a} is not related to {target_network}", file=sys.stdout)
                sys.exit(6)
        else:
            resulting_networks = list(ip_network(target_network).address_exclude(net_a))
            print(f"{separator.join(str(n) for n in resulting_networks)}", file=sys.stdout)
            sys.exit(0)


if __name__ == '__main__':
    main()
