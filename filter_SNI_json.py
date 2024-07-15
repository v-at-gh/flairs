#!/usr/bin/env python3

from sys import exit
import argparse
import json
from typing import Dict, List, Optional, Union
from pathlib import Path
from ipaddress import ip_network, ip_address

def is_ip_address(item: str) -> bool:
    try: ip_network(item); return True
    except: return False


class Filter_expression:

    @staticmethod
    def parse_filter_expression(filter_expression) -> List[str]:
        #TODO: implement complex [negative] filters.
        #TODO: implement filter expression validation.
        if isinstance(filter_expression, str):
            separators = [',', '\t', ' ']
            for sep in separators:
                if sep in filter_expression:
                    return [item.strip() for item in filter_expression.split(sep) if item.strip() != '']
            return [item.strip() for item in filter_expression.split() if item.strip() != '']
        return filter_expression

    @staticmethod
    def satisfies_address_filter(address: str, address_filters: Union[str, List[str]]) -> bool:
        if address_filters:
            address_filters = Filter_expression.parse_filter_expression(address_filters)
            for filter in address_filters:
                try: ip_network(filter)
                except Exception as e: print(e); exit(1)
            return any(ip_address(address) in ip_network(filter) for filter in address_filters)
        return True

    @staticmethod
    def satisfies_domain_filter(domain: str, domain_filters: Union[str, List[str]]) -> bool:
        if domain_filters:
            domain_filters = Filter_expression.parse_filter_expression(domain_filters)
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
                    k: [d for d in v if Filter_expression.satisfies_domain_filter(d, domain_filters)]
                    for k, v in test_json_obj['address_to_server_names'].items()
                    if Filter_expression.satisfies_address_filter(k, address_filters)
                }
                result['address_to_server_names'] = {k: v for k, v in address_dict.items() if v}

            if 'server_name_to_addresses' in test_json_obj:
                server_name_dict = {
                    k: [a for a in v if Filter_expression.satisfies_address_filter(a, address_filters)]
                    for k, v in test_json_obj['server_name_to_addresses'].items()
                    if Filter_expression.satisfies_domain_filter(k, domain_filters)
                }
                result['server_name_to_addresses'] = {k: v for k, v in server_name_dict.items() if v}

            if 'server_name_to_addresses' not in test_json_obj and 'address_to_server_names' not in test_json_obj:
                if all(is_ip_address(key) for key in test_json_obj.keys()):
                    address_dict = {
                        k: [domain for domain in v
                            if Filter_expression.satisfies_domain_filter(domain, domain_filters)]
                        for k, v in test_json_obj.items()
                        if Filter_expression.satisfies_address_filter(k, address_filters)
                    }
                    result['address_to_server_names'] = {k: v for k, v in address_dict.items() if v}
                else:
                    server_name_dict = {
                        k: [address for address in v
                            if Filter_expression.satisfies_address_filter(address, address_filters)]
                        for k, v in test_json_obj.items()
                        if Filter_expression.satisfies_domain_filter(k, domain_filters)
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
    #TODO: implement complex [negative] filters,
    # ex: `not (net 17.0.0.0/8 or 192.168.0.0/16) and not (host 1.3.1.2 or 1.4.8.8)`
    parser.add_argument('-n', '--domains')
    parser.add_argument('-i', '--indent', type=int)

    args = parser.parse_args()

    obj = instantiate_json_obj(
        test_json_file_path=args.file,
        address_filters=args.addresses,
        domain_filters=args.domains,
    )

    print(json.dumps(obj, indent=int(args.indent)))

if __name__ == '__main__':
    main()
