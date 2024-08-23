#!/usr/bin/env python3
'''To be used with `extract-sni-from-pcap.py` script.'''

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

import json
from typing import Union
from ipaddress import (
    IPv4Network, IPv6Network,
    ip_address, ip_network,
    collapse_addresses
)
from argparse import ArgumentParser, Namespace

class ArgHelp:
    services  = "comma-separated list of domain names or their parts"
    data      = "data from which addresses are extracted"
    separator = "separator for the list of resulting networks. Default is the new line"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('services',          type=str, help=ArgHelp.services)
    parser.add_argument('-d', '--data',      type=str, help=ArgHelp.data)
    parser.add_argument('-s', '--separator', type=str, help=ArgHelp.separator,
                        default='\n')
    return parser.parse_args()

def get_service_addresses_list(
        service_names: Union[str, list, set, tuple],
        data: Union[str, Path, dict, list]
) -> list[Union[IPv4Network,IPv6Network]]:

    if isinstance(data, (str, Path)):
        if Path(data).exists() and Path(data).is_file:
            try:
                with open(data, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    if 'server_name_to_addresses' in data.keys():
                        data = data['server_name_to_addresses'].items()
                #TODO: implement else-case
            except Exception as e: raise e
        elif isinstance(data, str):
            try:
                data = json.loads(data)
                if isinstance(data, dict):
                    if 'server_name_to_addresses' in data.keys():
                        data = data['server_name_to_addresses'].items()
                    #TODO: implement else-case
                #TODO: implement else-case
            except Exception as e: raise e
    elif isinstance(data, dict):
        if 'server_name_to_addresses' in data.keys():
            data = data['server_name_to_addresses'].items()

    if isinstance(service_names, str):
        if ',' not in service_names:
            data = {
                sni: addr for sni, addr in data
                if service_names.lower() in sni.lower()
            }
        else:
            service_names = set(
                n.strip() for n in service_names.strip().split(',')
                if n.strip() != '')
            return get_service_addresses_list(service_names, data)
    elif isinstance(service_names, (list, set, tuple)):
        if all(isinstance(n, str) for n in service_names):
            data = {
                sni: addr for sni, addr in data
                if any(name.strip().lower() in sni.lower()
                       for name in service_names)
            }
        else:
            raise ValueError("All elements of service_name iterable must be strings.")
    else:
        raise ValueError("service_name must be a string or a list of strings.")

    service_addresses = []
    for sni_addr in data.values():
        service_addresses.extend(sni_addr)
    service_addresses = list(
        collapse_addresses(ip_address(addr) for addr in service_addresses))

    return service_addresses

def print_result(result, separator):
    result = separator.join(str(a) for a in result)
    print(result)

def main():
    args = parse_arguments()
    print_result(
        get_service_addresses_list(
            service_names=args.services, data=args.data
        ),
        args.separator
    )

if __name__ == '__main__':
    main()
