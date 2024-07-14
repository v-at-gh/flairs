from typing import Iterator, Union
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from ipaddress import ip_network, collapse_addresses

def _exclude_addresses(
        target_network,
        addresses_to_exclude
) -> Iterator[Union[IPv4Network, IPv6Network]]:

    # Pre-process `addresses_to_exclude`.
    addresses_to_exclude = sorted(collapse_addresses(
        [ip_network(a) for a in addresses_to_exclude]))

    # Process addresses.
    networks = []
    for address in addresses_to_exclude:
        if address.subnet_of(target_network):
            networks.extend(
                target_network.address_exclude(address))
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

def exclude_addresses(
        target_network:       Union[IPv4Network, IPv6Network],
        addresses_to_exclude: Union[IPv4Address, IPv4Network,
                                    IPv6Address, IPv6Network,
                                    str, list, set, tuple]
) -> Union[Iterator[IPv4Network], Iterator[IPv6Network], None]:

    # Pass arguments to built-in network method `address_exclude`,
    if isinstance(addresses_to_exclude, (IPv4Network, IPv6Network)):
        return target_network.address_exclude(addresses_to_exclude)
    # or convert IPv*Address object to IPv*Network before passing.
    elif isinstance(addresses_to_exclude, (IPv4Address, IPv6Address)):
        return target_network.address_exclude(ip_network(addresses_to_exclude))

	# Parse `addresses_to_exclude` to iterable object
	# and pass to `_exclude_addresses` helper-function.
    elif isinstance(addresses_to_exclude, str) and any(
            c for c in addresses_to_exclude if c == ','):
        addresses_to_exclude = [
            a.strip() for a in addresses_to_exclude.split(',')]
        return _exclude_addresses(target_network, addresses_to_exclude)
    elif isinstance(addresses_to_exclude, str) and any(
            c for c in addresses_to_exclude if c == ' '):
        addresses_to_exclude = [
            a.strip() for a in addresses_to_exclude.split()]
        return _exclude_addresses(target_network, addresses_to_exclude)
    elif isinstance(addresses_to_exclude, (list, set, tuple)):
        return _exclude_addresses(target_network, addresses_to_exclude)
