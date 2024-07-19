#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from argparse import ArgumentParser, Namespace
from typing import NoReturn, Union
from ipaddress import IPv4Network, IPv6Network, ip_network

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

def validate_args(target_net: str, addrs_str: str) -> Union[tuple[Union[IPv4Network, IPv6Network], str], NoReturn]:
    if not is_string_a_valid_ip_network(target_net):
        print(f"{target_net} is not a valid ip network.", file=sys.stderr)
        sys.exit(1)
    elif not addrs_str:
        print(f"Missing addresses argument. It must be a {ArgHelp.addresses}.", file=sys.stderr)
        sys.exit(2)

    target_net = ip_network(target_net)
    addrs_str = str(addrs_str).strip()

    return target_net, addrs_str

def process_args(target_net: Union[IPv4Network, IPv6Network], addrs_str: str
                        ) -> Union[tuple[set, set, set, set], NoReturn]:
    addr_objs = set()
    inv_addrs = set()
    mis_addrs = set()
    irr_addrs = set()
    if is_string_a_valid_ip_network(addrs_str):
        net_a = ip_network(addrs_str)
        if not isinstance(net_a, type(target_net)):
            mis_addrs.add(net_a)
        elif not net_a.subnet_of(target_net):
            if net_a.supernet_of(target_net):
                irr_addrs.add(net_a)
            else: irr_addrs.add(net_a)
        else: addr_objs.add(net_a)
    else:
        # split the string of addresses to be excluded into a set of strings to avoid duplication
        if ',' in addrs_str:
            addrs = set(a.strip() for a in addrs_str.split(',') if a.strip() != '')
        else:
            if not ' ' in addrs_str:
                print(f"{addrs_str} is not a valid ip network.", file=sys.stderr)
                sys.exit(2)
            addrs = set(a.strip() for a in addrs_str.split() if a.strip() != '')
        for a in addrs:
            if not is_string_a_valid_ip_network(a, strict=False):
                inv_addrs.add(a); continue
            else:  net_a = ip_network(a)
            if not isinstance(net_a, type(target_net)): mis_addrs.add(net_a)
            elif   not net_a.subnet_of(target_net): irr_addrs.add(a)
            else:  addr_objs.add(net_a)
    return addr_objs, inv_addrs, mis_addrs, irr_addrs

def print_errors_and_exit(inv_addrs, mis_addrs, irr_addrs) -> NoReturn:
    wrong_stuff_message_list = []
    for wrong_stuff in zip(
            ('invalid address', 'misfitting address', 'irrelevant address'),
            (inv_addrs, mis_addrs, irr_addrs)):
        if len(wrong_stuff[1]) > 0:
            plural = 'es' if len(wrong_stuff[1]) > 1 else ''
            wrong_stuff_message_list.append(
                f"{wrong_stuff[0]+plural+': '+' '.join(str(item) for item in wrong_stuff[1])}"
            )
    print('\n'.join(wrong_stuff_message_list).strip(), file=sys.stderr)
    sys.exit(2)

def print_result_and_exit(result_nets, separator) -> NoReturn:
    print(separator.join((str(n) for n in result_nets)).strip(), file=sys.stdout)
    sys.exit(0)

def main() -> NoReturn:
    args = parse_arguments()

    if not args.separator: separator = "\n"
    else:  separator = str(args.separator)

    target_net, addrs_str = validate_args(args.network, args.addresses)

    addr_objs, inv_addrs, mis_addrs, irr_addrs \
        = process_args(target_net, addrs_str)

    if not args.ignore and (inv_addrs or mis_addrs or irr_addrs):
        print_errors_and_exit(inv_addrs, mis_addrs, irr_addrs)
    else:
        result_nets = sorted(list(exclude_addresses(target_net, (a for a in addr_objs))))
        if len(result_nets) == 0: print(target_net); sys.exit(0)
        print_result_and_exit(result_nets, separator)

if __name__ == '__main__':
    main()
