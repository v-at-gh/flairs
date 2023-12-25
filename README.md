# Flairs Project

## Overview

The Flairs project provides a Python Flask web interface for visualizing process and network connection information on macOS using the `netstat` command.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/flairs.git
    ```

2. Navigate to the project directory:

    ```bash
    cd flairs
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the Flask application:

```bash
python3 app.py
```

Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your web browser to view the process information.

## Project Structure

- **app.py**: Flask application entry point.
- **templates/index.html**: HTML template for displaying process and connection information.
- **static/script.js**: JavaScript for handling collapsible sections and table sorting.
- **src/Netstat.py**: Module for retrieving network connection information using the `netstat` command.
- **src/Process.py**: Module for retrieving process information.
- **src/Connection.py**: Module containing data classes for representing network connections.
- **src/Common.py**: Module with common utility functions and configurations.

## Features

- Visualize process information including Process ID, Command Line, and Executable.
- Display network connection details including Family, Protocol, Local Address, Local Port, Remote Address, Remote Port, and State.
- Collapsible sections for easy navigation.
- Clickable headers for sorting network connections. #TODO

## License

This project is licensed under the GNU GPL License - see the [LICENSE](LICENSE) file for details.
