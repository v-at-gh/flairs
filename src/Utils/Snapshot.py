import json
import sqlite3
from dataclasses import dataclass
from typing import List, Union
from time import time

from ..Utils.Connection import Net_Connection
from ..Utils.Netstat import Netstat

@dataclass
class Snapshot:
    timestamp: float
    connections: List[Net_Connection]

class SnapshotDatabase:

    def __init__(self, db_file='snapshots.db') -> None:
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                connections TEXT
            )
        ''')
        self.connection.commit()

    def save_snapshot(self, snapshot: Snapshot) -> None:
        cursor = self.connection.cursor()
        #TODO 0: use csv representation of connection instead of json
        cursor.execute('''
            INSERT INTO snapshots (timestamp, connections)
            VALUES (?, ?)
        ''', (snapshot.timestamp, json.dumps(snapshot.connections)))
        self.connection.commit()

    def take_snapshot(self) -> None:
        snapshot = Snapshot(
            timestamp=time(),
            connections=[
                {
                    'hash': connection.hash,
                    #TODO 0: ...
                    'dict': connection.to_dict()
                } for connection in Netstat.get_connections()
            ]
        )
        self.save_snapshot(snapshot)

    def get_snapshots(self) -> List[Snapshot]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT timestamp, connections FROM snapshots ORDER BY timestamp')
        rows = cursor.fetchall()
        snapshots = []
        for row in rows:
            timestamp, connections_json = row
            #TODO 0: ...
            connections = json.loads(connections_json)
            snapshots.append(Snapshot(timestamp, connections))
        return snapshots

    def compare_snapshots(
            self,
            snapshot_prev: Snapshot,
            snapshot_curr: Snapshot
        ) -> List[Net_Connection]:
        def _get_connections_by_hash(snapshot: Snapshot, connection_hash: str) -> List[Net_Connection]:
            return [
                connection for connection in snapshot.connections
                if connection['hash'] == connection_hash
            ]
        hashes_of_conns_in_prev = set(connection['hash'] for connection in snapshot_prev.connections)
        hashes_of_conns_in_curr = set(connection['hash'] for connection in snapshot_curr.connections)
        diff_hashes = hashes_of_conns_in_prev ^ hashes_of_conns_in_curr
        diff = {'previous': [], 'current': []}
        for connection_hash in diff_hashes:
            connections_in_prev = _get_connections_by_hash(snapshot_prev, connection_hash)
            connections_in_curr = _get_connections_by_hash(snapshot_curr, connection_hash)
            diff['previous'].extend(connections_in_prev)
            diff['current'].extend(connections_in_curr)
        return diff

    def close_connection(self) -> None:
        self.connection.close()
