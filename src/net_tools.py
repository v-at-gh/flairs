from typing import Iterator, List, Union
from ipaddress import IPv4Network, IPv6Network
from ipaddress import ip_address, ip_network, collapse_addresses

def is_string_a_valid_ip_address(item: str) -> bool:
    try: ip_address(item); return True
    except: return False

def is_string_a_valid_ip_network(item: str, strict: bool = False) -> bool:
    if not strict:
        try: ip_network(item); return True
        except: return False
    else:
        if is_string_a_valid_ip_network(item) and not is_string_a_valid_ip_address(item):
            return True
        else: return False

def exclude_addresses(
        target_network:       Union[IPv4Network, IPv6Network],
        addresses_to_exclude: Union[List[IPv4Network], List[IPv6Network]]
)    -> Union[Iterator[IPv4Network], Iterator[IPv6Network]]:
    '''This function solves the following problem:

    https://stackoverflow.com/questions/66204457/how-can-i-remove-two-or-more-subnet-from-a-network
    https://codereview.stackexchange.com/questions/245922/ip-address-exclusion-algorithm

    Since the last answer is technically correct:
        - Use sets!
        - Lists are O(N), while sets are O(1)!
        - Secondly it's quite easy to subtract sets simply use set(c) = set(a) - set(b)

    try to execute::

        a = ipaddress.ip_network('0.0.0.0/1')
        b = ipaddress.ip_network('1.1.1.1')
        c = ipaddress.ip_network('1.3.1.2')
        res = set(a) - set(b) - set(c)

    and see how long it takes. (:
    '''
    addresses_to_exclude = sorted(collapse_addresses(addresses_to_exclude))
    # Process addresses.
    networks = []
    for address in addresses_to_exclude:
        if address.subnet_of(target_network):
            networks.extend(target_network.address_exclude(address))
    networks = sorted(set(networks))
    # Post-process resulting network list.
    networks_to_remove = []
    for network in networks:
        for address in addresses_to_exclude:
            if address.subnet_of(network) or address.supernet_of(network):
                networks_to_remove.append(network)
    for network in networks_to_remove:
        if network in networks:
            networks.remove(network)
    return collapse_addresses(networks)
