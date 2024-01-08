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
        '''
        Process and initialize connection attributes after dataclass initialization.

        This method processes and initializes various connection attributes,
        such as converting specified attributes to integers, determining the address family,
        processing socket information, and setting the connection state for UDP connections.
        '''
        self._convert_to_int('recvQ', 'sendQ', 'pid', 'epid', 'rhiwat', 'shiwat')
        self.family = 4 if self.proto.endswith('4') else 6
        self.proto = ''.join(char for char in self.proto if char.isalpha())
        self._process_socket("localSocket", self.localSocket, "local")
        self._process_socket("remoteSocket", self.remoteSocket, "remote")
        if self.proto == 'udp':
            if self.localPort == 0:
                self.state = 'NONE'
            elif self.localPort != 0 and self.remotePort == 0:
                self.state = 'LISTEN'
            elif self.localPort != 0 and self.remotePort != 0:
                self.state = 'ESTABLISHED'

    def _convert_to_int(self, *attributes) -> None:
        '''
        Convert specified attributes to integers.

        Args:
            *attributes: Variable number of attribute names to be converted to integers.
        '''
        for attribute in attributes:
            setattr(self, attribute, int(getattr(self, attribute)))

    def _process_socket(self, socket_attr, socket_str, socket_location) -> None:
        '''
        Process socket information and set related attributes.

        Args:
            socket_attr (str): The attribute name to be set.
            socket_str (str): The socket information string.
            socket_location (str): The location indicator, either "local" or "remote".
        '''
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
        '''
        Return connection attributes as a CSV string.

        Returns:
            str: CSV-formatted string containing connection attributes.
        '''
        return (
            f"{self.pid},{self.proto},{self.family},"
            f"{self.localSocket},{self.remoteSocket},"
            f"{self.state_bits},"
            f"{self.state}"
        )

    def to_dict(self) -> Dict:
        '''
        Return connection attributes as a dictionary.

        Returns:
            Dict: Dictionary containing connection attributes.
        '''
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
        '''
        Return connection attributes as a dictionary.

        Returns:
            Dict: Dictionary containing connection attributes.
        '''
        return self.__dict__

    @property
    def hash(self) -> str:
        '''
        Return SHA-1 hash of connection attributes.

        Returns:
            str: SHA-1 hash of connection attributes.
        '''
        hash_obj = sha1()
        hash_obj.update(str(self.to_dict()).encode('utf-8'))
        return hash_obj.hexdigest()

@dataclass
class BaseConnection:
    '''
    Base class for network connections.

    Attributes:
        proto (str): Protocol of the connection.
        recvQ (int): Receive queue size.
        sendQ (int): Send queue size.
        localSocket (str): Local socket information.
        remoteSocket (str): Remote socket information.
    '''
    proto: str
    recvQ: int
    sendQ: int
    localSocket: str
    remoteSocket: str

@dataclass
class TCP_State:
    '''
    Class representing TCP connection state.

    Attributes:
        state (str): TCP connection state.
    '''
    state: str

@dataclass
class UDP_State:
    '''
    Class representing UDP connection state.

    Attributes:
        state (str, optional): UDP connection state. Defaults to None.
    '''
    state: str = None

@dataclass
class Common_Connection_attrs_and_metrics:
    '''
    Common attributes and metrics for network connections.

    Attributes:
        rhiwat (int): High-water mark for received data.
        shiwat (int): High-water mark for sent data.
        pid (int): Process ID associated with the connection.
        epid (int): Effective process ID associated with the connection.
        state_bits (str): State bits of the connection.
        options (str): Connection options.
        gencnt (str): Generation count.
        flags (str): Connection flags.
        flags1 (str): Additional connection flags.
        usscnt (int): User space send count.
        rtncnt (int): Return count.
        fltrs (int): Filters count.
        family (int, optional): Address family. Defaults to None.
        localAddr (str, optional): Local address. Defaults to None.
        localPort (int, optional): Local port. Defaults to None.
        remoteAddr (str, optional): Remote address. Defaults to None.
        remotePort (int, optional): Remote port. Defaults to None.
    '''
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
):
    '''
    Class representing a TCP network connection.

    Inherits attributes and methods from Common_Connection_attrs_and_metrics,
    TCP_State, BaseConnection, and _ConnectionProcessor.

    Example:
        tcp_connection = TCP_Connection(
            rhiwat=100, shiwat=200, pid=1234, epid=5678,
            state_bits='0001', options='-', gencnt='1234',
            flags='00000002', flags1='-', usscnt=0, rtncnt=0,
            fltrs=0, proto='tcp', recvQ=0, sendQ=0,
            localSocket='0.0.0.0:22', remoteSocket='0.0.0.0:0',
            state='LISTEN'
        )
    '''
    ...

@dataclass
class UDP_Connection(
    UDP_State,
    Common_Connection_attrs_and_metrics,
    BaseConnection, _ConnectionProcessor
):
    '''
    Class representing a UDP network connection.

    Inherits attributes and methods from UDP_State,
    Common_Connection_attrs_and_metrics, BaseConnection, and _ConnectionProcessor.

    Example:
        udp_connection = UDP_Connection(
            rhiwat=100, shiwat=200, pid=1234, epid=5678,
            state_bits='0001', options='-', gencnt='1234',
            flags='00000002', flags1='-', usscnt=0, rtncnt=0,
            fltrs=0, proto='udp', recvQ=0, sendQ=0,
            localSocket='0.0.0.0:12345', remoteSocket='0.0.0.0:0',
            state='LISTEN'
        )
    '''
    ...

Net_Connection = Union[TCP_Connection, UDP_Connection]

@dataclass
class ICMP_Exchange(Common_Connection_attrs_and_metrics,
                     BaseConnection, _ConnectionProcessor):
    '''
    Class representing an ICMP network connection.

    To be implemented.

    Inherits attributes and methods from Common_Connection_attrs_and_metrics,
    BaseConnection, and _ConnectionProcessor.

    Example:
        icmp_exchange = ICMP_Exchange(
            rhiwat=100, shiwat=200, pid=1234, epid=5678,
            state_bits='0001', options='-', gencnt='1234',
            flags='00000002', flags1='-', usscnt=0, rtncnt=0,
            fltrs=0, proto='icmp', recvQ=0, sendQ=0,
            localSocket='0.0.0.0:0', remoteSocket='0.0.0.0:0'
        )
    '''
    ...
