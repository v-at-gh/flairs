#/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

from argparse import ArgumentParser, Namespace

from src.tools import die
from src.net_tools import IPv4_Internet, IPv6_Internet

class ArgHelp:
    vpn_name       = "name for VPN"
    endpoint       = "endpoint's ip address and port"
    network        = "virtual private network for private addresses allocation"
    peers          = "initial number of VPN peers"
    users          = "initial number of VPN users. User can have multiple peers"
    user_names     = "comma (or space but no both) separated names of VPN users"
    peers_per_user = "initial number of peers per user"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('endpoint',               type=str, help=ArgHelp.endpoint)
    parser.add_argument('-N', '--vpn-name',       type=str, help=ArgHelp.vpn_name)
    parser.add_argument('-n', '--network',        type=str, help=ArgHelp.network)
    parser.add_argument('-p', '--peers',          type=str, help=ArgHelp.peers)
    parser.add_argument('-u', '--users',          type=int, help=ArgHelp.users)
    parser.add_argument('-U', '--user-names',     type=str, help=ArgHelp.user_names)
    parser.add_argument('-P', '--peers-per-user', type=int, help=ArgHelp.peers_per_user)
    return parser.parse_args()

def process_args(args: Namespace) -> Namespace:
    from ipaddress import(
        IPv4Address, IPv6Address,
        IPv4Network, IPv6Network,
        ip_address, ip_network
    )
    if not args.vpn_name: args.vpn_name = 'vpn_0'

    if args.endpoint:
        if not isinstance(args.endpoint, (IPv4Address, IPv6Address)):
            try: args.endpoint = ip_address(args.endpoint)
            except ValueError: die(1, f"{args.endpoint} is not a valid IP address.")

    if not args.network: args.network = ip_network('10.0.0.0/24')
    else:
        if not isinstance(args.network, (IPv4Network, IPv6Network)):
            try: args.network = ip_network(args.network)
            except ValueError: die(1, f"{args.network} is not a valid IP network.")

    if args.endpoint in args.network \
        and (args.network not in (IPv4_Internet, IPv6_Internet)):
        die(2, f"Address of endpoint {args.endpoint} belongs to network {args.network}.")

    if args.users:
        try:
            args.users = int(args.users)
            if args.users < 1: die(3, "Are you kidding?")
        except: die(3, "Amount of initial VPN users must be a natural number.")

    if args.user_names:
        #TODO: handle duplicates and sanitize names
        if ',' in args.user_names:
            args.user_names = [name.strip() for name in args.user_names.strip().split(',')]
        else:
            args.user_names = [name.strip() for name in args.user_names.strip().split()]

    return args

def main():
    from pprint import pprint

    from src.VPN.Classes import VPN

    args: Namespace = parse_arguments()
    args: Namespace = process_args(args)

    vpn = VPN.create_vpn(
        name     = args.vpn_name,
        endpoint = args.endpoint,
        network  = args.network
    )

    if args.user_names:
        users_amount = len(args.user_names)
    if args.user_names and (
        (users_amount > vpn.addrs_left) or (
            args.peers_per_user and (
                users_amount * args.peers_per_user > vpn.addrs_left
            )
        )
    ):
        die(4, (
            f"VPN's address pool does not have enough addresses"
            f" to allocate for {len(args.user_names)} users."
            f" Network {vpn.network} has {vpn.addrs_left} addresses available for client peers."
        ))

    #TODO: implement multiple peer creation
    if args.user_names and not args.peers_per_user:
        for name in args.user_names:
            vpn.add_peer(name=name)
    elif args.user_names and args.peers_per_user:
        for name in args.user_names:
            for i in range(args.peers_per_user):
                vpn.add_peer(name=f"{name}_{i+1}")

    # print(vpn.to_json())
    pprint(vpn)

if __name__ == '__main__':
    main()