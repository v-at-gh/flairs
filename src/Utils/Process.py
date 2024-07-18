from dataclasses import dataclass
from subprocess import run
from typing import Any, Dict, List, Optional

from .Common import subprocess_run_kwargs
from .Connection import Net_Connection
from .Netstat_old import Netstat

@dataclass
class Process:
    pid: int
    executable: str = ''

    def __post_init__(self) -> None:
        executable_path = run(f"ps -p {self.pid} -o comm", **subprocess_run_kwargs).stdout.splitlines()
        if len(executable_path) > 1:
            self.executable_path = executable_path[1]
            self.executable = self.executable_path.split('/')[-1]
            executable_path_with_args = run(f"ps -p {self.pid} -o command", **subprocess_run_kwargs).stdout.splitlines()
            self.executable_path_with_args = executable_path_with_args[1]
        elif len(executable_path) <= 1:
            self.executable = ''
            self.executable_path = ''
            self.executable_path_with_args = ''

    @property
    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__

    #TODO 0: implement method for representation process as csv

    @staticmethod
    def get_dict_of_the_process_with_connections(
        process,
        connections: Optional[List[Net_Connection]] = None
    ) -> Dict:
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

    def get_connections_of_this_process(self) -> Dict:
        dict_of_process_with_connections = Process.get_dict_of_the_process_with_connections(self)
        return dict_of_process_with_connections
