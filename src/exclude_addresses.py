from sys import exit
from typing import Iterator, Union
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from ipaddress import ip_address, ip_network, collapse_addresses

#TODO: fix the case, when all of the addresses to exclude
# are not in the target network.

def is_valid_ip_address(address: str) -> bool:
    try: ip_network(address); return True
    except ValueError: return False

def _exclude_addresses(
        target_network,
        addresses_to_exclude
) -> Iterator[Union[IPv4Network, IPv6Network]]:

    # Pre-process `addresses_to_exclude`.
    invalid_addrs = set()
    for a in addresses_to_exclude:
        if not is_valid_ip_address(a):
            invalid_addrs.add(a)
    if invalid_addrs:
        error_message = (
            f"Invalid address{'es:' if len(invalid_addrs) > 1 else ':'}"
            f" {', '.join(invalid_addrs)}"
        )
        print(error_message)
        exit(1)

    addresses_to_exclude = sorted(collapse_addresses(
        [ip_network(a) for a in addresses_to_exclude]))
    # if all(ip_network(address_to_exclude) not in target_network for address_to_exclude in ip_network(addresses_to_exclude)):
    #     return target_network
    # else:
    #     addresses_to_exclude = sorted(collapse_addresses(
    #         [ip_network(a) for a in addresses_to_exclude]))

    # if not all(ip_network(a).subnet_of(target_network) for a in addresses_to_exclude):
    #     return collapse_addresses(target_network)

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
        target_network:       Union[IPv4Network, IPv6Network, str],
        addresses_to_exclude: Union[IPv4Address, IPv4Network,
                                    IPv6Address, IPv6Network,
                                    str, list, set, tuple]
):
# ) -> list[IPv4Network | IPv6Network] | IPv4Network | IPv6Network | None:
# ) -> Union[Iterator[IPv4Network], Iterator[IPv6Network]]:

    if isinstance(target_network, str):
        try:
            target_network = ip_network(target_network.strip())
        except Exception as e:
            print(e)
            exit(1)

    # # Pass arguments to built-in network method `address_exclude`,
    # if isinstance(addresses_to_exclude, (IPv4Network, IPv6Network)):
    #     return target_network.address_exclude(addresses_to_exclude)
    # or convert IPv*Address object to IPv*Network before passing.
    if isinstance(addresses_to_exclude, (IPv4Address, IPv6Address, IPv4Network, IPv6Network)):
        if addresses_to_exclude in target_network:
            return list(target_network.address_exclude(ip_network(addresses_to_exclude)))
        else:
            return target_network
    # Parse `addresses_to_exclude` to iterable object
    # and pass to `_exclude_addresses` helper-function.
    elif isinstance(addresses_to_exclude, str) and any(c for c in addresses_to_exclude if c == ','):
        addresses_to_exclude = [a.strip() for a in addresses_to_exclude.split(',') if a.strip() != '']
        return list(_exclude_addresses(target_network, addresses_to_exclude))

    elif isinstance(addresses_to_exclude, str) and any(c for c in addresses_to_exclude if c == ' '):
        addresses_to_exclude = [a.strip() for a in addresses_to_exclude.split()  if a.strip() != '']
        return list(_exclude_addresses(target_network, addresses_to_exclude))
    elif isinstance(addresses_to_exclude, (list, set, tuple)):
        return list(_exclude_addresses(target_network, addresses_to_exclude))
    elif isinstance(addresses_to_exclude, str):
        try:
            ip_network(addresses_to_exclude.strip())
            if ip_network(addresses_to_exclude).subnet_of(target_network):
                return list(_exclude_addresses(target_network, [addresses_to_exclude]))
            else:
                return target_network
        except:
            pass
