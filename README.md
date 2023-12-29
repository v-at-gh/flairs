# Flairs Project

Network Connections Recorder and Analyzer

This project provides the ability to record the state of network connections and perform analysis by comparing snapshots with traffic dumps. It includes several Python scripts and modules for data retrieval, processing, and a web-based interface for visualization.

## Contents

- [test_db.py](./test_db.py): Script to compare snapshots of network connections.
- [get_data.py](./get_data.py): Script to retrieve and print current network connection state in different formats.
- [app.py](./app.py): Flask web application for displaying current network connections and additional features.
- [test_cli.py](./test_cli.py): Command-line interface script to print current network connection state in JSON format.
- [src/Connection.py](./src/Connection.py): Module defining classes for representing network connections.
- [src/Netstat.py](./src/Netstat.py): Module for retrieving network connection information using the `netstat` command.
- [src/Common.py](./src/Common.py): Common module containing shared utilities and configurations.
- [src/Filter.py](./src/Filter.py): Module (not implemented yet) for creating capture/preview filters for tcpdump/wireshark.
- [src/Process.py](./src/Process.py): Module defining a class for representing processes and their associated network connections.
- [src/Snapshot.py](./src/Snapshot.py): Module for capturing, storing, and comparing snapshots of network connection states.

## Usage

### `test_db.py`

This script compares snapshots of network connections and prints the differences between the last two snapshots. It utilizes the `SnapshotDatabase` class from `Snapshot.py`. Run the script as follows:

```bash
./test_db.py -v
```

The `-v` option prints the last snapshot along with the timestamp and connections.

### `get_data.py`

This script retrieves the current state of network connections and prints it in either dictionary or JSON format. It utilizes the `Netstat` and `Process` classes from the respective modules. Run the script with the desired format:

```bash
./get_data.py --format json
```

### `app.py`

This Flask web application provides three routes:

- `/`: Displays the current network connection state.
- `/test`: Similar to the main route for testing purposes.
- `/filters`: Not implemented yet, intended for rendering a page with tcpdump/wireshark capture/preview filters.

Run the application using:

```bash
./app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your web browser to interact with the web interface.

### `test_cli.py`

This command-line interface script retrieves the current state of network connections and prints it in JSON format. Run the script as follows:

```bash
./test_cli.py
```

## Modules

### `src/Connection.py`

Defines classes (`BaseConnection`, `TCP_State`, `Common_Connection_properties_and_metrics`, `TCP_Connection`, `UDP_Connection`) representing network connections.

### `src/Netstat.py`

Module for retrieving network connection information using the `netstat` command. Contains the `Netstat` class with methods to get interfaces, connections, and associated process IDs.

### `src/Common.py`

Common module with shared utilities and configurations. It currently includes configurations for subprocess run arguments.

### `src/Filter.py`

Not implemented yet. Intended for creating capture/preview filters for tcpdump/wireshark.

### `src/Process.py`

Defines a `Process` class representing processes and their associated network connections.

### `src/Snapshot.py`

Module for capturing, storing, and comparing snapshots of network connection states. Contains the `Snapshot` and `SnapshotDatabase` classes.

## Notes

- The project utilizes the `flask` library for the web application.
- Certain functionalities are marked as not implemented (`#TODO`) and are intended for future development.
- The project involves capturing snapshots of network connections and storing them in an SQLite database.
- The code includes comments and docstrings for better understanding and maintainability.

Feel free to explore and modify the code according to your project requirements.

## License

This project is licensed under the GNU GPL License - see the [LICENSE](LICENSE) file for details.
