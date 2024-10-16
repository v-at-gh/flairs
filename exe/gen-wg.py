#/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

import subprocess, random, json, base64
from typing import Optional, Union
from dataclasses import dataclass, field, asdict
from ipaddress import (
    IPv4Address, IPv4Interface, IPv4Network,
    IPv6Address, IPv6Interface, IPv6Network,
    ip_address, ip_interface, ip_network,
    collapse_addresses
)

from src.tools import die, obj_to_stringified_dict
from src.net_tools import IPv4_Internet, IPv6_Internet, is_string_a_valid_ip_address, is_string_a_valid_ip_network

#TODO: for this (and other constants for paths to binary executables)
# implement an algorithm to find a realpath to binary to make this project portable

WG_BIN_PATH = '/opt/homebrew/bin/wg'
OPENSSL_BIN_PATH = '/opt/homebrew/bin/openssl'

# some mock names
names = 'Alice Bob Charlie Dan Eva Fiona Gary Hank Ian Jane Kate Lance Mike Nino Oscar Paul Quinn Rita Steve Tom Uri Vik William Xena Yulia Zack'.split()
devices = 'PC Mac Archlinux Manjaro Gentoo Fedora Ubuntu Debian Android iPhone Nokia Samsung Xiaomi'.split()

#TODO: implement user layer abstraction
@dataclass
class User:
    name: str
    devices: list = field(default_factory=list)


class X25519:
    @staticmethod
    def gen_private_key() -> str:
        private_key = subprocess.run([WG_BIN_PATH, 'genkey'], capture_output=True, encoding='utf-8', text=True).stdout.strip()
        return private_key

    @staticmethod
    def gen_public_key(private_key: str) -> str:
        public_key = subprocess.run([WG_BIN_PATH, 'pubkey'], input=private_key, capture_output=True, encoding='utf-8', text=True).stdout.strip()
        return public_key

    @staticmethod
    def gen_preshared_key() -> str:
        return X25519.gen_private_key()

class OpenVPN:
    @staticmethod
    def gen_certificate():
        return base64.b64encode(random.randbytes(128)).decode()

    @staticmethod
    def gen_private_key():
        return base64.b64encode(random.randbytes(128)).decode()

@dataclass
class Peer:
    name: str
    virtual_network: Union[IPv4Network, IPv6Network]
    address: Union[IPv4Address, IPv6Address]
    endpoint_socket: Optional[str] = None

    @property
    def as_dict(self): return asdict(self)
    def to_stringified_dict(self): return obj_to_stringified_dict(self)
    def to_json(self) -> str: return json.dumps(self.to_stringified_dict())

    @property
    def private_address(self) -> Union[IPv4Interface, IPv6Interface]:
        return ip_interface(self.address.compressed+'/'+str(self.virtual_network.prefixlen))

    @property
    def client_address(self) -> Union[IPv4Network, IPv6Network]:
        return ip_network(self.address)

@dataclass
class Peer_WG(Peer):
    # __annotations__ = Peer.__annotations__
    name: str
    virtual_network: Union[IPv4Network, IPv6Network]
    address: Union[IPv4Address, IPv6Address]
    endpoint_socket: Optional[str] = None

    private_key: str = ''
    public_key:  str = ''
    preshared_key: Optional[str] = None

    def __post_init__(self):
        self.private_key = X25519.gen_private_key()
        self.public_key  = X25519.gen_public_key(self.private_key)
        if self.preshared_key:
            self.preshared_key = X25519.gen_preshared_key()

@dataclass
class Peer_OpenVPN(Peer):
    # __annotations__ = Peer.__annotations__
    name: str
    virtual_network: Union[IPv4Network, IPv6Network]
    address: Union[IPv4Address, IPv6Address]
    endpoint_socket: Optional[str] = None

    certificate: str = ''
    private_key: str = ''

    def __post_init__(self):
        self.certificate = OpenVPN.gen_certificate()
        self.private_key = OpenVPN.gen_private_key()

# class Peer_IPsec(Peer): pass

class VPN_Processor:
    def add_peer(self, name=None, address=None, endpoint=None, gen_psk: bool = True):
        #TODO: move `name` logic to `User` layer
        if not name: name = random.choice(names)+'_'+random.choice(devices)
        address = self.allocate_address(address)
        if not address: raise Exception("VPN address pool exhausted")
        if self.__class__.__name__ == 'VPN_OpenVPN':
            peer = Peer_OpenVPN(name = name, virtual_network = self.virtual_network, address = address, endpoint_socket = endpoint)
        elif self.__class__.__name__ == 'VPN_WG':
            peer = Peer_WG(name = name, virtual_network = self.virtual_network, address = address, endpoint_socket = endpoint, preshared_key = gen_psk)
        else:
            peer = Peer(name = name, virtual_network = self.virtual_network, address = address, endpoint_socket = endpoint)
        if endpoint: self.server_peers.append(peer)
        else:        self.client_peers.append(peer)

    def add_peers(self, amount: int):
        free_addrs = self.max_clients - len(self.peers)
        if amount > free_addrs:
            raise Exception("No free addresses left for allocation to new peers.")
        else:
            for _ in range(amount): self.add_peer()

    def del_client_peer(self: 'VPN', peer: Peer):
        try:
            self.client_peers.remove(peer)
            self.unallocate_address(peer.address)
        except ValueError as e:
            raise e

    def del_server_peer(self: 'VPN', peer: Peer):
        try:
            self.server_peers.remove(peer)
            self.unallocate_address(peer.address)
        except ValueError as e:
            raise e

    def allocate_address(self, address=None) -> Union[IPv4Address, IPv6Address, None]:
        if address:
            address = ip_address(address)
            if address in self.allocated_addresses: print(f"Address {address} is already allocated"); return
            else: self.allocated_addresses.add(address); return address
        else:
            for address in self.virtual_network.hosts():
                if address not in self.allocated_addresses:
                    self.allocated_addresses.add(address); return address

    def unallocate_address(self: 'VPN', address) -> Union[IPv4Address, IPv6Address, None]:
        address = ip_address(address)
        if address in self.allocated_addresses:
            self.allocated_addresses.remove(address)
        else:
            print(f"Address {address} is not allocated"); return

@dataclass
class VPN(VPN_Processor):
    name: str
    endpoint_socket: str
    virtual_network: Union[IPv4Network, IPv6Network]
    initial_clients_count: int = 0
    server_peers: list[Peer] = field(default_factory=list)
    client_peers: list[Peer] = field(default_factory=list)
    routes: list[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    #TODO: implement proxification flag
    proxify: bool = True

    @property
    def clients_count(self) -> int: return len(self.client_peers)
    @property
    def peers(self) -> list[Peer]: return self.server_peers + self.client_peers
    @property
    def enpoint_port(self) -> int: return int(self.endpoint_socket.rsplit(':', 1)[-1])
    @property
    def main_endpoint_peer(self) -> Peer:return self.server_peers[0]
    @property
    def as_dict(self): return asdict(self)
    def to_stringified_dict(self): return obj_to_stringified_dict(self)
    def to_json(self) -> str: return json.dumps(self.to_stringified_dict())

    def __post_init__(self) -> None:
        self.endpoint_ip_address = ip_address(self.endpoint_socket.rsplit(':', 1)[0])
        self.virtual_network     = ip_network(self.virtual_network)

        if   not self.routes and self.proxify:     self.routes = [IPv4_Internet]
        elif not self.routes and not self.proxify: self.routes = [self.virtual_network]
        elif self.routes: self.routes = list(collapse_addresses(self.routes + [self.virtual_network]))

        for route in self.routes:
            if route not in (IPv4_Internet, IPv6_Internet) \
                     and self.endpoint_ip_address in route \
                     and self.proxify:
                raise Exception(f"Endpoint address {self.endpoint_ip_address} is in {route}.")

        if    self.virtual_network.num_addresses == 1: self.max_clients = 0
        elif  self.virtual_network.num_addresses <= 2: self.max_clients = self.virtual_network.num_addresses - 1 
        else: self.max_clients = self.virtual_network.num_addresses - 3

        self.allocated_addresses = set()
        self.add_peer(name=self.name, endpoint=self.endpoint_socket)
        if self.initial_clients_count:
            if self.initial_clients_count <= self.max_clients:
                for _ in range(self.initial_clients_count): self.add_peer()
            else:
                raise Exception(
                    f"There are not enough addresses in "
                    f"the network to create {self.initial_clients_count} clients. "
                    f"Total available {self.max_clients}."
                )

@dataclass
class VPN_WG(VPN):
    __annotations__ == VPN.__annotations__
    # name: str
    # endpoint_socket: str
    # virtual_network: Union[IPv4Network, IPv6Network]
    # initial_clients_count: int = 0
    # server_peers: list[Peer] = field(default_factory=list)
    # client_peers: list[Peer] = field(default_factory=list)
    # routes: list[Union[IPv4Network, IPv6Network]] = field(default_factory=list)
    # #TODO: implement proxification flag
    # proxify: bool = True

    def __post_init__(self):
        return super().__post_init__()

    def render_server_config_for_wg(self):
        interface_section = []
        interface_section.append('[Interface]')
        interface_section.append(f'ListenPort = {self.enpoint_port}')
        interface_section.append(f'PrivateKey = {self.main_endpoint_peer.private_key}')
        interface_section = '\n'.join(interface_section)
        peers_sections = []
        for peer in self.client_peers:
            peer_section = []
            peer_section.append(f"[Peer]")
            peer_section.append(f"AllowedIPs = {peer.client_address}")
            peer_section.append(f"PublicKey = {peer.public_key}")
            if peer.preshared_key:
                peer_section.append(f"PresharedKey = {peer.preshared_key}")
            peer_section = '\n'.join(peer_section)
            peers_sections.append(peer_section)
        server_config = '\n\n'.join([interface_section] + peers_sections)
        return server_config

    def render_client_config_for_wg(self, peer: Peer):
        interface_section = []
        interface_section.append('[Interface]')
        interface_section.append(f"Address = {peer.private_address}")
        interface_section.append(f"PrivateKey = {peer.private_key}")
        #TODO: implement DNS selector
        interface_section.append(f"DNS = 1.0.0.1, 1.1.1.1, 8.8.8.8, 9.9.9.9") 
        interface_section = '\n'.join(interface_section)
        endpoints_sections = []
        for endpoint in self.server_peers:
            endpoint_section = []
            endpoint_section.append("[Peer]")
            endpoint_section.append(f"Endpoint = {endpoint.endpoint_socket}")
            endpoint_section.append(f"AllowedIPs = {', '.join(str(route) for route in self.routes)}")
            endpoint_section.append(f"PublicKey = {endpoint.public_key}")
            if peer.preshared_key:
                endpoint_section.append(f"PresharedKey = {peer.preshared_key}")
            endpoint_section.append(f"PersistentKeepalive = 25")
            endpoint_section = '\n'.join(endpoint_section)
            endpoints_sections.append(endpoint_section)
        client_config = '\n\n'.join([interface_section] + endpoints_sections)
        return client_config

@dataclass
class VPN_OpenVPN(VPN):
    __annotations__ == VPN.__annotations__

# class VPN_IPsec(VPN): pass

def print_vpn_configs(vpn):
    many_sharps = '#'*64
    print(f"{many_sharps} {vpn.name}.wg.server.conf {many_sharps}")
    print(vpn.render_server_config_for_wg())
    print('\n\n')
    for peer in vpn.client_peers:
        print(f"{many_sharps} {peer.name}.wg.client.conf {many_sharps}")
        print(f"# BEGIN_PEER {peer.name}")
        print(vpn.render_client_config_for_wg(peer))
        print(f"# END_PEER {peer.name}")
        print('\n\n')

from argparse import ArgumentParser, Namespace

class ArgHelp:

    # server-related args
    endpoint       = "endpoint's ip address and port"
    port           = "endpoint's port (default is 51280)"
    Name           = "name for VPN"
    network        = "virtual private network for private addresses allocation"
    routes         = "comma separated routes for clients via endpoint"
    peers          = "comma separated peer names"
    peers_count    = "initial amount of vpn peers"

    # client-related args
    users          = "comma separated user names"
    peers_per_user = "initial amount of vpn peers per user"
    dns            = "comma separated DNS servers for clients"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    # server-related args
    parser.add_argument('endpoint', type=str, help=ArgHelp.endpoint)
    parser.add_argument('-p', '--port',           type=int, help=ArgHelp.port)
    parser.add_argument('-N', '--Name',           type=str, help=ArgHelp.Name)
    parser.add_argument('-n', '--network',        type=str, help=ArgHelp.network)
    parser.add_argument('-r', '--routes',         type=str, help=ArgHelp.routes)
    parser.add_argument('-P', '--peers',          type=str, help=ArgHelp.peers)
    parser.add_argument('-c', '--peers-count',    type=int, help=ArgHelp.peers_count)

    # client-related args
    parser.add_argument('-u', '--users',          type=str, help=ArgHelp.users)
    parser.add_argument('-U', '--peers-per-user', type=int, help=ArgHelp.peers_per_user)
    parser.add_argument('-d', '--dns',            type=str, help=ArgHelp.dns)

    # test
    parser.add_argument('-j', '--json', action='store_true')
    parser.add_argument('-W', '--WG', action='store_true')
    parser.add_argument('-O', '--OVPN', action='store_true')

    return parser.parse_args()

def validate_args(args: Namespace):
    #TODO: improve validation
    if not args.endpoint:
        die(1, "You must specify vpn endpoint.")

    esocket = str(args.endpoint)
    #TODO: validate IPv6 addresses
    if ':' in esocket:
        host, port = esocket.rsplit(':', 1)
        if port:
            try:
                port = int(port)
                if port < 1 or port > 65535:
                    die(1, "Port must be a number from 1 to 65535.")
            except Exception as e:
                die(1, e)
        else:
            if not is_string_a_valid_ip_address(host):
                die(1, f"{host} is not a valid ip address.")

    return args

def process_args(args: Namespace) -> Namespace:
    args = args
    return args

def main():
    args = parse_arguments()

    validate_args(args)

    if not args.Name:
        vpn_name = 'wg0'
    else:
        #TODO: sanitize name
        vpn_name = args.Name

    #TODO: implement vpn validation
    if args.network:
        virtual_network = args.network
    else:
        #TODO: implement algorithm for default network selector based on peers count
        virtual_network = '10.7.0.0/24'

    #TODO: implement routes validation
    if args.routes:
        routes = [ip_network(r.strip()) for r in args.routes.split(',')]
    else:
        routes = [ip_network('0.0.0.0/0')]

    #TODO: implement peer names processing
    if args.peers:
        names_for_peers = [str(name).strip() for name in args.peers.split(',')]

    if args.peers_count:
        initial_clients_count = args.peers_count
    else:
        initial_clients_count = 1

    if args.WG:
        v = VPN_WG(
            name = vpn_name,
            endpoint_socket = args.endpoint,
            virtual_network = virtual_network,
            initial_clients_count = initial_clients_count,
            routes = routes
        )
    elif args.OVPN:
        v = VPN_OpenVPN(
            name = vpn_name,
            endpoint_socket = args.endpoint,
            virtual_network = virtual_network,
            initial_clients_count = initial_clients_count,
            routes = routes
        )
    else:
        v = VPN(
            name = vpn_name,
            endpoint_socket = args.endpoint,
            virtual_network = virtual_network,
            initial_clients_count = initial_clients_count,
            routes = routes
        )

    if args.json:
        print(v.to_json())
    else:
        print_vpn_configs(v)

if __name__ == '__main__':
    main()
