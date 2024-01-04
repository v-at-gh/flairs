# Netstat Class Documentation

## Class: Netstat

The `Netstat` class provides a set of methods for retrieving network-related information, specifically focused on network interfaces and connections using the `netstat` command. This class encapsulates functionality related to parsing the output of the `netstat` command and organizing the information into a more structured format.

### Methods:

#### 1. `get_interfaces() -> list[dict]`:

This static method retrieves information about network interfaces and their associated addresses. It utilizes the `netstat -inl` command to obtain a list of network interfaces along with relevant details such as their names and addresses. The method returns a list of dictionaries, each representing a network interface with its name and associated addresses.

#### 2. `_get_connections(proto: protos = None, family: families = None) -> list[str]`:

This private method is responsible for executing the `netstat` command to retrieve information about network connections. It takes optional parameters `proto` (protocol) and `family` (address family) to filter the results. The method returns a list of strings, where each string represents a line from the `netstat` command output.
```
#TODO: add support for linux and windows.
#  Windows implementation of `netstat` has a `-b` argument,
#    which returns a path to each binary for a connetion.
#  Linux version is invoked like `netstat (or `ss`) -tunap`
#    for all connections and process IDs.
#------------------------------------------------------------------------------------
#  Elevation of privileges is required to obtain complete information
#    about connections and their corresponding processes on both non-macos systems.
```

#### 3. `_parse_netstat_connection(netstat_connection_line: str) -> TCP_Connection | UDP_Connection`:

This private method parses a single line of `netstat` command output representing a network connection. It determines the protocol (TCP or UDP) and creates an instance of the corresponding connection class (`TCP_Connection` or `UDP_Connection`). The method returns the parsed connection object.

#### 4. `get_connections(proto: protos = None, family: families = None, netstat_lines: str = None) -> list[TCP_Connection | UDP_Connection]`:

This static method retrieves a list of network connections. It can optionally take parameters `proto` and `family` to filter the results. If `netstat_lines` is not provided, it internally calls the `_get_connections` method to obtain the necessary information. The method returns a list of connection objects, where each object is an instance of either `TCP_Connection` or `UDP_Connection`.

#### 5. `get_pids_of_processes_with_connections(connections=None) -> list[int]`:

This static method retrieves a list of unique process IDs (PIDs) associated with network connections. If the `connections` parameter is not provided, it internally calls the `get_connections` method to obtain the necessary information. The method returns a sorted list of unique PIDs.

### Usage:

```python
# Example usage of the Netstat class
interfaces = Netstat.get_interfaces()
print("Network Interfaces:", interfaces)

connections = Netstat.get_connections(proto="tcp")
print("TCP Connections:", connections)

pids = Netstat.get_pids_of_processes_with_connections(connections)
print("Unique PIDs:", pids)
```

### Notes:

- The class assumes the presence of external dependencies such as the `netstat` command.
- The code includes placeholders (`#TODO`) for future enhancements or improvements.
- The class relies on certain external types (`protos`, `families`, `TCP_Connection`, `UDP_Connection`) that are not explicitly defined in the provided code snippet. These types need to be defined elsewhere in the codebase.