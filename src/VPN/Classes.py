import json
from pprint import pprint
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Union
from ipaddress import (
    IPv4Address, IPv4Network,
    IPv6Address, IPv6Network,
    ip_address, ip_network
)
from random import choice as random_choice

from ..tools import obj_to_stringified_dict

names = 'Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lambda Mu Nu Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega'.split()

@dataclass
class Peer:
    name:    str
    address: IPv4Address

    @property
    def as_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class Server(Peer):
    name:     str
    address:  IPv4Address
    endpoint: IPv4Address

@dataclass
class Client(Peer):
    name:    str
    address: IPv4Address

@dataclass
class VPN:
    name:      str
    network:       IPv4Network
    endpoints: set[IPv4Address] = field(default_factory=set)
    server_peers:    list[Peer] = field(default_factory=list)
    client_peers:    list[Peer] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.network.num_addresses < 2:
            raise ValueError(f"{str(self.network)} is unusable for VPN")
        elif  self.network.num_addresses == 2: self.max_peers = 2
        else: self.max_peers = self.network.num_addresses - 2
        self.allocated_addresses = set()

    @classmethod
    def create_vpn(
        cls,
        name: str,
        endpoint: str,
        network: str
    ):
        vpn = cls(name=name, network=network)
        #TODO: handle server creation a better way
        vpn.add_peer(name='server_1', endpoint=endpoint)
        return vpn

    @property
    def peers(self) -> list[Peer]:    return self.server_peers + self.client_peers
    @property
    def addrs_left(self) -> int:      return self.max_peers - len(self.peers)
    @property
    def peer_names(self) -> set[str]: return set(peer.name for peer in self.peers)

    @property
    def as_dict(self) -> dict[str, Any]: return asdict(self)
    def to_stringified_dict(self) -> dict[str, Union[int, str]]: return obj_to_stringified_dict(self)
    def to_json(self, **kwargs) -> str: return json.dumps(self.to_stringified_dict(), **kwargs)

    @classmethod
    def from_json(cls, json_str: str):
        raise NotImplementedError()

    def _allocate_address(self, address: Optional[IPv4Address] = None
    ) -> IPv4Address:
        #TODO: implement multiple addresses allocation
        if self.addrs_left:
            if address:
                if address in self.network and address not in self.allocated_addresses:
                    self.allocated_addresses.add(address)
                    return address
                elif address in self.network and address in self.allocated_addresses:
                    raise ValueError(f"Address {address} is already allocated.")
                else:
                    raise ValueError(f"Address {address} is not related to network {self.network}.")
            else:
                for address in self.network.hosts():
                    if address not in self.allocated_addresses:
                        self.allocated_addresses.add(address)
                        return address
        else:
            raise ValueError("Network pool exhausted.")

    def _unallocate_address(self, address: IPv4Address
    ) -> None:
        #TODO: implement multiple addresses unallocation
        self.allocated_addresses.remove(address)

    def add_peer(self,
                 name:     Optional[str]         = None,
                 address:  Optional[IPv4Address] = None,
                 endpoint: Optional[IPv4Address] = None
    ) -> None:
        #TODO: implement multiple peer creation
        if endpoint in self.endpoints: raise ValueError(f"Endpoint {endpoint} is already registered in this VPN.")
        address = self._allocate_address(address)
        if endpoint:
            peer = Server(name, address, endpoint); self.server_peers.append(peer)
            self.endpoints.add(endpoint)
        else:
            peer = Client(name, address); self.client_peers.append(peer)

    def del_server(self, peer: Server) -> None:
        self.server_peers.remove(peer)
        self._unallocate_address(peer.address)
        self.endpoints.remove(peer.endpoint)

    def del_client(self, peer: Client) -> None:
        self.client_peers.remove(peer)
        self._unallocate_address(peer.address)

    def del_peer(self,
                 name:     Optional[str]         = None,
                 address:  Optional[IPv4Address] = None,
                 endpoint: Optional[IPv4Address] = None
    ) -> None:
        peer = self.select_peer(name, address, endpoint)
        e = hasattr(peer, 'endpoint')
        if e: self.del_server(peer)
        else: self.del_client(peer)

    def select_peer(self,
                    name:     Optional[str]         = None,
                    address:  Optional[IPv4Address] = None,
                    endpoint: Optional[IPv4Address] = None
    ) -> Peer:
        if  endpoint and not (name and address):
            try:   return list(filter(lambda p: p.endpoint == endpoint, self.server_peers))[0]
            except IndexError: raise ValueError(f"No peer with {endpoint} endpoint")
        elif address and not (name and endpoint):
            try:   return list(filter(lambda p: p.address == address, self.peers))[0]
            except IndexError: raise ValueError(f"No peer with {address} address")
        elif name and not (address and endpoint):
            try:   return list(filter(lambda p: p.name == name, self.peers))[0]
            except IndexError: raise ValueError(f"No peer with {name} name")
        else:
            raise ValueError("Choose one of peer's attributes: name, private address or endpoint.")
