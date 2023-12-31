from dataclasses import dataclass
from subprocess import run
from typing import Any

from .Common import subprocess_run_kwargs
from .Netstat import Netstat

@dataclass
class Process:
    pid: int
    executable: str = ''

    def __post_init__(self) -> None:
        #TODO 0: when `shell=True` is removed from `Common.py`, implement a command splitter
        executable = run(f"ps -p {self.pid} -o comm", **subprocess_run_kwargs).stdout.splitlines()
        if len(executable) > 1:
            self.executable = executable[1]
            executable_with_args = run(f"ps -p {self.pid} -o command", **subprocess_run_kwargs).stdout.splitlines()
            self.executable_with_args = executable_with_args[1]
        elif len(executable) <= 1:
            self.executable = ''
            self.executable_with_args = ''

    @property
    def as_dict(self) -> dict[str, Any]:
        return self.__dict__

    @staticmethod
    def get_dict_of_the_process_with_connections(process, connections=None) -> dict:
        #TODO 1: this method should not return a dictionary representation of the `Process` object,
        # but the `Process` object itself with its associated `Connections`
        if connections is None:
            connections = Netstat.get_connections()
        connections_of_process = [
            connection for connection in connections
            if connection.pid == process.pid
        ]
        dict_of_process_with_connections = {
            'process': process.as_dict,
            'connections_count': len(connections_of_process),
            'connections': [connection.to_dict() for connection in connections_of_process]
        }
        return dict_of_process_with_connections

    def get_connections_of_process(self) -> dict:
        dict_of_process_with_connections = Process.get_dict_of_the_process_with_connections(self)
        return dict_of_process_with_connections
