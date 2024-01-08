# Connection Classes Documentation

The provided code defines a set of data classes representing network connections, with a focus on TCP and UDP protocols. These classes are designed to capture information about network connections, including various properties and metrics associated with them.

## BaseConnection Class

### Class: `BaseConnection`

The `BaseConnection` class serves as the foundational data class for network connections. It includes common attributes such as protocol type (`proto`), receive and send queues (`recvQ` and `sendQ`), local and remote socket information (`localSocket` and `remoteSocket`). The class provides methods for processing socket information, converting attributes to integers, and initializing the instance after data class construction.

#### Attributes:

- `proto`: The protocol type (e.g., 'tcp' or 'udp').
- `recvQ`: The receive queue size.
- `sendQ`: The send queue size.
- `localSocket`: The local socket information in the format 'address:port'.
- `remoteSocket`: The remote socket information in the format 'address:port'.

#### Methods:

- `_process_socket`: Processes socket information and updates relevant attributes.
- `_convert_to_int`: Converts specified attributes to integers.
- `__post_init__`: Initializes the instance after data class construction, converting certain attributes to integers and processing socket information.
- `as_dict`: Property that returns the instance as a dictionary.
- `to_dict`: Method that returns a dictionary representation of the connection, with additional details depending on the protocol.

## TCP_Connection and UDP_Connection Classes

### Class: `TCP_Connection` and `UDP_Connection`

The `TCP_Connection` and `UDP_Connection` classes extend the `BaseConnection` class and inherit attributes from the `Common_Connection_properties_and_metrics` class, representing additional properties specific to TCP or UDP connections.

#### Additional Attributes (Inherited):

- `rhiwat`: The high-water mark for the socket receive buffer.
- `shiwat`: The high-water mark for the socket send buffer.
- `pid`: Process ID associated with the connection.
- `epid`: Extended process ID associated with the connection.
- `state_bits`: State information for TCP connections.
- `options`: Connection options.
- `gencnt`: General count.
- `flags`: Connection flags.
- `flags1`: Additional connection flags.
- `usscnt`: User space socket count.
- `rtncnt`: Round-trip time count.
- `fltrs`: Filters count.

#### Additional Attributes (TCP_Connection):

- `state`: State information for TCP connections.

#### Additional Methods:

- `to_dict`: Overridden method in each class to return a dictionary representation of the connection, including protocol-specific details.

## Usage Example:

```python
# Example usage of the connection classes
tcp_connection = TCP_Connection(proto='tcp', recvQ=1024, sendQ=2048, localSocket='192.168.1.1:8080', remoteSocket='10.0.0.1:80', state='ESTABLISHED', rhiwat=4096, shiwat=8192, pid=1234, epid=5678, state_bits='ESTABLISHED', options='...', gencnt='...', flags='...', flags1='...', usscnt=42, rtncnt=10, fltrs=5)
udp_connection = UDP_Connection(proto='udp', recvQ=512, sendQ=1024, localSocket='192.168.1.1:1234', remoteSocket='0.0.0.0:0', rhiwat=2048, shiwat=4096, pid=5678, epid=9876, state_bits='...', options='...', gencnt='...', flags='...', flags1='...', usscnt=30, rtncnt=8, fltrs=3)

print("TCP Connection:", tcp_connection.to_dict())
print("UDP Connection:", udp_connection.to_dict())
```

### Notes:

- The classes utilize Python's `dataclass` decorator for concise definition and initialization of data classes.
- The structure encourages code reuse through inheritance, allowing for the extension of common connection properties and metrics in TCP and UDP-specific classes.
- The `to_dict` method provides a convenient way to obtain a dictionary representation of a connection, facilitating data serialization or other use cases.