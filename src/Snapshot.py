import json
import sqlite3
from dataclasses import dataclass
from typing import List, Union
from time import time

from .Connection import TCP_Connection, UDP_Connection
from .Netstat import Netstat
Network_Connection = Union[TCP_Connection, UDP_Connection]

@dataclass
class Snapshot:
    timestamp: float
    connections: List[Network_Connection]

class SnapshotDatabase:
    def __init__(self, db_file='snapshots.db'):
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        #TODO: store connections in blobs -- jsons are too large
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                connections TEXT
            )
        ''')
        self.connection.commit()

    def save_snapshot(self, snapshot: Snapshot):
        #TODO: store connections in blobs -- jsons are too large
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO snapshots (timestamp, connections)
            VALUES (?, ?)
        ''', (snapshot.timestamp, json.dumps(snapshot.connections)))
        self.connection.commit()

    def take_snapshot(self):
        snapshot = Snapshot(
            timestamp=time(),
            connections=[
                {
                    'hash': connection.hash,
                    'dict': connection.to_dict()
                } for connection in Netstat.get_connections()
            ]
        )
        self.save_snapshot(snapshot)

    def get_snapshots(self) -> List[Snapshot]:
        #TODO: store connections in blobs -- jsons are too large
        cursor = self.connection.cursor()
        cursor.execute('SELECT timestamp, connections FROM snapshots ORDER BY timestamp')
        rows = cursor.fetchall()

        snapshots = []
        for row in rows:
            timestamp, connections_json = row
            connections = json.loads(connections_json)
            snapshots.append(Snapshot(timestamp, connections))
        return snapshots

    #TODO: reduce code repetition in the following method:
    def compare_snapshots(self, snapshot1: Snapshot, snapshot2: Snapshot) -> List[Network_Connection]:
        connections1 = set([connection['hash'] for connection in snapshot1.connections])
        connections2 = set([connection['hash'] for connection in snapshot2.connections])
        diff = connections1 ^ connections2
        list_diff = list(diff)
        diff = []
        if len(list_diff) > 0:
            for connection_hash in list_diff:
                connections_in_1 = [connection for connection in snapshot1.connections
                                    if connection['hash'] == connection_hash]
                if len(connections_in_1) > 0:
                    diff.append({'Connections in previous': connections_in_1})
                connections_in_2 = [connection for connection in snapshot2.connections
                                    if connection['hash'] == connection_hash]
                if len(connections_in_2) > 0:
                    diff.append({'Connections in current': connections_in_2})
        return diff

    def close_connection(self):
        self.connection.close()
