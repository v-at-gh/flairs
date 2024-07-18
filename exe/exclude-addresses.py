#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from argparse import ArgumentParser, Namespace
from ipaddress import ip_network

from src.net_tools import exclude_addresses, is_string_a_valid_ip_network


class ArgHelp:
    network   = "The network from which we exclude addresses"
    addresses = "comma or whitespace separated addresses of hosts and/or networks to be excluded"
    separator = "separator for the list of resulting networks. Default is the new line"
    ignore    = "ignore non-valid input arguments (except the target network)"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('network', type=str, help=ArgHelp.network)
    parser.add_argument('-a', '--addresses', type=str, help=ArgHelp.addresses)
    parser.add_argument('-s', '--separator', type=str, help=ArgHelp.separator)
    parser.add_argument('-i', '--ignore', action='store_true', help=ArgHelp.ignore)
    return parser.parse_args()

def process_args(target_network, addresses_str) -> tuple[set, set, set, set]:
    address_objs = set()
    invalid_addresses = set()
    misfitting_addresses = set()
    irrelevant_addresses = set()
    if is_string_a_valid_ip_network(addresses_str):
        net_a = ip_network(addresses_str)
        if not isinstance(net_a, type(target_network)):
            misfitting_addresses.add(net_a)
        elif not net_a.subnet_of(target_network):
            if net_a.supernet_of(target_network):
                irrelevant_addresses.add(net_a)
            else: irrelevant_addresses.add(net_a)
        else: address_objs.add(net_a)
    else:
        # split the string of addresses to be excluded into a set of strings to avoid duplication
        if ',' in addresses_str:
            addresses = set(a.strip() for a in addresses_str.split(',') if a.strip() != '')
        else:
            if not ' ' in addresses_str:
                print(f"{addresses_str} is not a valid ip network.", file=sys.stderr)
                sys.exit(2)
            addresses = set(a.strip() for a in addresses_str.split() if a.strip() != '')
        for a in addresses:
            if not is_string_a_valid_ip_network(a, strict=False):
                invalid_addresses.add(a); continue
            else:  net_a = ip_network(a)
            if not isinstance(net_a, type(target_network)): misfitting_addresses.add(net_a)
            elif   not net_a.subnet_of(target_network): irrelevant_addresses.add(a)
            else:  address_objs.add(net_a)
    return address_objs, invalid_addresses, misfitting_addresses, irrelevant_addresses

def print_result(resulting_networks, separator) -> None:
    print(separator.join((str(n) for n in resulting_networks)).strip(), file=sys.stdout)

def main() -> None:
    args = parse_arguments()

    if not args.separator: separator = "\n"
    else:  separator = str(args.separator)

    if not is_string_a_valid_ip_network(args.network):
        print(f"{args.network} is not a valid ip network.", file=sys.stderr)
        sys.exit(1)
    elif not args.addresses:
        print(f"Missing addresses argument. It must be a {ArgHelp.addresses}.", file=sys.stderr)
        sys.exit(2)

    target_network = ip_network(args.network)
    addresses_str = str(args.addresses).strip()

    address_objs, invalid_addresses, misfitting_addresses, irrelevant_addresses \
        = process_args(target_network, addresses_str)

    if not args.ignore and (invalid_addresses or misfitting_addresses or irrelevant_addresses):
        wrong_stuff_message_list = []
        for wrong_stuff in zip(
                ('invalid address', 'misfitting address', 'irrelevant address'),
                (invalid_addresses, misfitting_addresses, irrelevant_addresses)):
            if len(wrong_stuff[1]) > 0:
                plural = 'es' if len(wrong_stuff[1]) > 1 else ''
                wrong_stuff_message_list.append(
                    f"{wrong_stuff[0]+plural+': '+' '.join(str(item) for item in wrong_stuff[1])}"
                )
        print('\n'.join(wrong_stuff_message_list).strip(), file=sys.stderr)
        sys.exit(2)
    else:
        resulting_networks = sorted(list(exclude_addresses(target_network, (a for a in address_objs))))
        if len(resulting_networks) == 0: print(target_network)
        print_result(resulting_networks, separator)
        sys.exit(0)

if __name__ == '__main__':
    main()