#!/usr/bin/env python3

from sys import exit
import argparse
import json
from typing import Dict, List, Optional, Union
from pathlib import Path
from ipaddress import ip_network, ip_address

def parse_filter(filter_expression) -> List[str]:
    if isinstance(filter_expression, str):
        separators = [',', '\t', ' ']
        for sep in separators:
            if sep in filter_expression:
                return [item.strip() for item in filter_expression.split(sep) if item.strip() != '']
        return [item.strip() for item in filter_expression.split() if item.strip() != '']
    return filter_expression

def validate_ip_address(item: str) -> bool:
    try: ip_network(item); return True
    except: return False

def address_filter_func(address: str, address_filters: Union[str, List[str]]) -> bool:
    if address_filters:
        address_filters = parse_filter(address_filters)
        return any(ip_address(address) in ip_network(filter) for filter in address_filters)
    return True

def domain_filter_func(domain: str, domain_filters: Union[str, List[str]]) -> bool:
    if domain_filters:
        domain_filters = parse_filter(domain_filters)
        return any(filter in domain for filter in domain_filters)
    return True

def instantiate_json_obj(
        test_json_file_path: str,
        address_filters: Optional[Union[str, List[str]]] = None,
        domain_filters:  Optional[Union[str, List[str]]] = None,
) -> Dict[str, Dict[str, List[str]]]:

    if Path(test_json_file_path).exists():
        with open(test_json_file_path, 'r', encoding='utf-8') as f:
            test_json_obj = json.load(f)
            result = {}

            if 'address_to_server_names' in test_json_obj:
                address_dict = {
                    k: [d for d in v if domain_filter_func(d, domain_filters)]
                    for k, v in test_json_obj['address_to_server_names'].items()
                    if address_filter_func(k, address_filters)
                }
                result['address_to_server_names'] = {k: v for k, v in address_dict.items() if v}

            if 'server_name_to_addresses' in test_json_obj:
                server_name_dict = {
                    k: [a for a in v if address_filter_func(a, address_filters)]
                    for k, v in test_json_obj['server_name_to_addresses'].items()
                    if domain_filter_func(k, domain_filters)
                }
                result['server_name_to_addresses'] = {k: v for k, v in server_name_dict.items() if v}

            if 'server_name_to_addresses' not in test_json_obj and 'address_to_server_names' not in test_json_obj:
                if all(validate_ip_address(key) for key in test_json_obj.keys()):
                    address_dict = {
                        k: [d for d in v if domain_filter_func(d, domain_filters)]
                        for k, v in test_json_obj.items()
                        if address_filter_func(k, address_filters)
                    }
                    result['address_to_server_names'] = {k: v for k, v in address_dict.items() if v}
                else:
                    server_name_dict = {
                        k: [a for a in v if address_filter_func(a, address_filters)]
                        for k, v in test_json_obj.items()
                        if domain_filter_func(k, domain_filters)
                    }
                    result['server_name_to_addresses'] = {k: v for k, v in server_name_dict.items() if v}

            return result
    else:
        print(f"File {test_json_file_path} does not exist.")
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-a', '--addresses')
    parser.add_argument('-n', '--domains')
    parser.add_argument('-i', '--indent')

    args = parser.parse_args()

    obj = instantiate_json_obj(
        test_json_file_path=args.file,
        address_filters=args.addresses,
        domain_filters=args.domains,
    )

    print(json.dumps(obj, indent=args.indent))

if __name__ == '__main__':
    main()