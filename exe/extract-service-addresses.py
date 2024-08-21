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

def get_service_addresses_list(
        service_name: Union[str, list, set, tuple],
        data: Union[str, Path, dict, list]
) -> list[Union[IPv4Network,IPv6Network]]:

    def extract_server_name_to_addresses_dict_items(data: dict):
        if 'server_name_to_addresses' in data.keys(): return data['server_name_to_addresses'].items()
        #TODO: implement else-case

    if isinstance(data, (str, Path)):
        if Path(data).exists() and Path(data).is_file:
            try:
                with open(data, 'r', encoding='utf-8') as file: data = json.load(file)
                if isinstance(data, dict): data = extract_server_name_to_addresses_dict_items(data)
                #TODO: implement else-case
            except Exception as e: raise e
        elif isinstance(data, str):
            try:
                data = json.loads(data)
                if isinstance(data, dict): data = extract_server_name_to_addresses_dict_items(data)
                #TODO: implement else-case
            except Exception as e: raise e
    elif isinstance(data, dict): data = extract_server_name_to_addresses_dict_items(data)

    if isinstance(service_name, str):
        if ',' not in service_name: data = {sni: addr for sni, addr in data if service_name.lower() in sni.lower()}
        else: service_name = set(n.strip() for n in service_name.strip().split(',') if n.strip() != ''); return get_service_addresses_list(service_name, data)
    elif isinstance(service_name, (list, set, tuple)):
        if all(isinstance(n, str) for n in service_name): data = {sni: addr for sni, addr in data if any(name.strip().lower() in sni.lower() for name in service_name)}
        else: raise ValueError("All elements of service_name iterable must be strings.")
    else: raise ValueError("service_name must be a string or a list of strings.")

    service_addresses = []
    for sni_addr in data.values(): service_addresses.extend(sni_addr)
    service_addresses = list(collapse_addresses(ip_address(addr) for addr in service_addresses))

    return service_addresses