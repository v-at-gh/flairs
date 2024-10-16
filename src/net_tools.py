from typing import Iterator, List, Literal, Union
from collections import defaultdict
from ipaddress import (
    IPv4Network, IPv6Network,
    ip_address, ip_network, collapse_addresses
)

IPv4_Internet = IPv4Network('0.0.0.0/0')
IPv6_Internet = IPv6Network('::/0')

def is_string_a_valid_ip_address(item: str) -> bool:
    try: ip_address(item); return True
    except: return False

def is_string_a_valid_ip_network(item: str, strict: bool = False) -> bool:
    if not strict:
        try: ip_network(item); return True
        except: return False
    else:
        if is_string_a_valid_ip_network(item) and not is_string_a_valid_ip_address(item): return True
        else: return False

def exclude_addresses(
        target_network:       Union[IPv4Network, IPv6Network],
        addresses_to_exclude: Union[List[IPv4Network], List[IPv6Network]]
)    -> Union[Iterator[IPv4Network], Iterator[IPv6Network]]:
    '''This function solves the following problem:

    - https://stackoverflow.com/questions/66204457/how-can-i-remove-two-or-more-subnet-from-a-network
    - https://codereview.stackexchange.com/questions/245922/ip-address-exclusion-algorithm

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
    ... (the author does not bear any responsibility for the OOM killer of your operating system)
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

def construct_capture_filter_for_endpoint(
        address,
        protocol,
        port
) -> str:
    '''Old version to construct filter expression to exclude endpoint traffic from capture'''
    try: address = ip_address(address)
    except ValueError: address = ip_network(address)
    parts = [
        f"""({direction} {
                'net' if isinstance(address, (IPv4Network, IPv6Network)) else 'host'
            } {address} and {protocol} {direction} port {port})"""
        for direction in ('dst', 'src')
    ]
    expression = "not (" + " or ".join(parts) + ")"
    return expression

GOAL = Literal['exclude', 'include']

def construct_filters(
        csv_content,
        capture: bool = True,
        display: bool = True,
        goal: GOAL = 'include'
) -> Union[str, tuple[str, str]]:
    '''New version to construct capture and display filters for multiple endpoints from csv data'''
    if capture: filters_capture = defaultdict(lambda: {'src': [], 'dst': []})
    if display: filters_display = defaultdict(lambda: {'src': [], 'dst': []})

    for row in csv_content.splitlines():
        ip, protocol, port = row.split(',')
        if capture:
            filters_capture[ip]['src'].append(f"{protocol} src port {port}")
            filters_capture[ip]['dst'].append(f"{protocol} dst port {port}")
        if display:
            filters_display[ip]['src'].append(f"{protocol}.srcport == {port}")
            filters_display[ip]['dst'].append(f"{protocol}.dstport == {port}")

    if capture:
        combined_capture_filters = []
        filters_list = filters_capture
    if display:
        combined_display_filters = []
        filters_list = filters_display

    for ip in filters_list:
        # the following assignment does not matter for display filter but wgaf
        if is_string_a_valid_ip_network(ip, strict=True): ip_type = 'net'
        elif is_string_a_valid_ip_address(ip): ip_type = 'host'
        else: raise ValueError(f"{ip} is not valid ip address of host or network")

        if capture:
            src_filter_capture = ' or '.join(filters_capture[ip]['src'])
            dst_filter_capture = ' or '.join(filters_capture[ip]['dst'])
        if display:
            src_filter_display = ' or '.join(filters_display[ip]['src'])
            dst_filter_display = ' or '.join(filters_display[ip]['dst'])
        
        if capture:
            combined_capture_filters.append(
            (f"{'not ' if goal == 'exclude' else ''}" "("
                f"(src {ip_type} {ip} and ({src_filter_capture}))"
                " or "
                f"(dst {ip_type} {ip} and ({dst_filter_capture}))"
            ")"))
        if display: combined_display_filters.append(
            (f"{'not ' if goal == 'exclude' else ''}" "("
                f"(ip.src == {ip} and ({src_filter_display}))"
                " or "
                f"(ip.dst == {ip} and ({dst_filter_display}))"
            ")"))
    
    if goal == 'include':
        if capture: capture_filter = " or ".join(combined_capture_filters)
        if display: display_filter = " or ".join(combined_display_filters)
    elif goal == 'exclude':
        if capture: capture_filter = " and ".join(combined_capture_filters)
        if display: display_filter = " and ".join(combined_display_filters)

    if capture and display: return capture_filter, display_filter
    elif capture: return capture_filter
    elif display: return display_filter

def construct_capture_filter(
        csv_content,
        goal: GOAL = 'include'
) -> str:
    return construct_filters(
        csv_content = csv_content,
        capture = True,
        display = False,
        goal = goal
    )

def construct_display_filter(
        csv_content,
        goal: GOAL = 'include'
) -> str:
    return construct_filters(
        csv_content = csv_content,
        capture = False,
        display = True,
        goal = goal
    )
