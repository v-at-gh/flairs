from typing import Iterator, List, Tuple, Union
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
) -> Union[Iterator[IPv4Network], Iterator[IPv6Network]]:

    target_network, addresses_to_exclude = _validate_network_args(target_network, addresses_to_exclude)

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

def _validate_network_args(
        target_network:       Union[IPv4Network, IPv6Network],
        addresses_to_exclude: Union[List[IPv4Network], List[IPv6Network]]
) -> Union[Tuple[IPv4Network, List[IPv4Network]],
           Tuple[IPv6Network, List[IPv6Network]]]:
    if not isinstance(target_network, (IPv4Network, IPv6Network)):
        raise TypeError("target_network '%s' is not a network object" % target_network)
    net_family = type(target_network)
    invalid_addresses_to_exclude = set()
    not_related_addresses_to_exclude = set()
    addresses_to_exclude_net_objs = set()
    for a in addresses_to_exclude:
        if not isinstance(a, net_family):
            invalid_addresses_to_exclude.add(a)
        elif not a.subnet_of(target_network) and \
             not a.supernet_of(target_network):
                not_related_addresses_to_exclude.add(a)
        else:
            addresses_to_exclude_net_objs.add(a)
    if invalid_addresses_to_exclude:
        raise TypeError(
            f"{' '.join(invalid_addresses_to_exclude)} "
            f"are not {net_family.__name__} addresses"
        )
    if not_related_addresses_to_exclude:
        raise ValueError(
            f"{' '.join(str(a) for a in not_related_addresses_to_exclude)} "
            f"are not related to target network {target_network}"
        )
    addresses_to_exclude = addresses_to_exclude_net_objs
    return target_network, addresses_to_exclude
