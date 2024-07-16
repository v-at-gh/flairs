from typing import Dict, Union
from dataclasses import dataclass
from hashlib import sha1

TCP_States = (
    'ESTABLISHED',
    'SYN_SENT',
    'SYN_RECEIVED',
    'FIN_WAIT_1',
    'FIN_WAIT_2',
    'TIME_WAIT',
    'CLOSED',
    'CLOSE_WAIT',
    'LAST_ACK',
    'LISTEN',
    'CLOSING',
    'NONE'
)

UDP_States = (
    'ESTABLISHED', 'LISTEN', 'NONE'
)

class _ConnectionProcessor:
    def __post_init__(self) -> None:
        self._convert_to_int('recvQ', 'sendQ', 'pid', 'epid', 'rhiwat', 'shiwat')
        self.family = 4 if self.proto.endswith('4') else 6
        self.proto = ''.join(char for char in self.proto if char.isalpha())
        self._process_socket("localSocket", self.localSocket, "local")
        self._process_socket("remoteSocket", self.remoteSocket, "remote")

    def _convert_to_int(self, *attributes) -> None:
        for attribute in attributes:
            setattr(self, attribute, int(getattr(self, attribute)))

    def _process_socket(self, socket_attr, socket_str, socket_location) -> None:
        def _translate_and_set_addr_from_asterisk_to_zeros() -> None:
            setattr(self, f"{socket_location}Addr", f"{'0.0.0.0' if self.family == 4 else '::'}")

        address = '.'.join(socket_str.split('.')[:-1])
        port = socket_str.split('.')[-1]

        if socket_str == '*.*':
            setattr(self, socket_attr, f"{'0.0.0.0:0' if self.family == 4 else ':::0'}")
            _translate_and_set_addr_from_asterisk_to_zeros()
            setattr(self, f"{socket_location}Port", 0)
        else:
            if socket_str.startswith('*'):
                setattr(self, socket_attr, f"{'0.0.0.0' if self.family == 4 else '::'}:{port}")
                _translate_and_set_addr_from_asterisk_to_zeros()
            else:
                setattr(self, socket_attr, f"{address}:{port}")
                setattr(self, f"{socket_location}Addr", address)
            setattr(self, f"{socket_location}Port", int(port))

    def to_csv(self) -> str:
        return (
            f"{self.pid},{self.proto},{self.family},"
            f"{self.localSocket},{self.remoteSocket},"
            f"{self.state_bits},"
            f"{self.state}"
        )

    def to_dict(self) -> Dict:
        connection_dict = {
            'pid': self.pid,
            'family': self.family, 'proto': self.proto,
            'localAddr': self.localAddr, 'localPort': self.localPort,
            'remoteAddr': self.remoteAddr, 'remotePort': self.remotePort,
            'state': self.state, 'state_bits': self.state_bits
        }
        return connection_dict

    @property
    def as_dict(self) -> Dict:
        return self.__dict__

    @property
    def hash(self) -> str:
        hash_obj = sha1()
        hash_obj.update(str(self.to_dict()).encode('utf-8'))
        return hash_obj.hexdigest()

@dataclass
class BaseConnection:
    proto: str
    recvQ: int
    sendQ: int
    localSocket: str
    remoteSocket: str

@dataclass
class TCP_State:
    state: str

@dataclass
class UDP_State:
    state: str = None

@dataclass
class Common_Connection_attrs_and_metrics:
    rhiwat: int
    shiwat: int
    pid: int
    epid: int
    state_bits: str
    options: str
    gencnt: str
    flags: str
    flags1: str
    usscnt: int
    rtncnt: int
    fltrs: int
    family: int = None
    localAddr: str = None
    localPort: int = None
    remoteAddr: str = None
    remotePort: int = None

@dataclass
class TCP_Connection(
    Common_Connection_attrs_and_metrics,
    TCP_State,
    BaseConnection, _ConnectionProcessor
): ...

@dataclass
class UDP_Connection(
    UDP_State,
    Common_Connection_attrs_and_metrics,
    BaseConnection, _ConnectionProcessor
):
    def __post_init__(self) -> None:
        'Sets string values for udp socket state.'
        super().__post_init__()
        if self.localPort == 0:
            self.state = 'NONE'
        elif self.localPort != 0 and self.remotePort == 0:
            self.state = 'LISTEN'
        elif self.localPort != 0 and self.remotePort != 0:
            self.state = 'ESTABLISHED'


Net_Connection = Union[TCP_Connection, UDP_Connection]

@dataclass
class ICMP_Exchange(Common_Connection_attrs_and_metrics,
                     BaseConnection, _ConnectionProcessor): ...
