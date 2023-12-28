#WARNING! This file produced by ChatGPT mostly. Use it on your own risk

import json
import sqlite3
from dataclasses import dataclass
from typing import List, Union

from Connection import TCP_Connection, UDP_Connection

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
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO snapshots (timestamp, connections)
            VALUES (?, ?)
        ''', (snapshot.timestamp, json.dumps(snapshot.connections)))
        self.connection.commit()

    def get_snapshots(self) -> List[Snapshot]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT timestamp, connections FROM snapshots ORDER BY timestamp')
        rows = cursor.fetchall()

        snapshots = []
        for row in rows:
            timestamp, connections_json = row
            connections = json.loads(connections_json)
            snapshots.append(Snapshot(timestamp, connections))

        return snapshots

    def compare_snapshots(self, snapshot1: Snapshot, snapshot2: Snapshot) -> List[Network_Connection]:
        diff = set(snapshot1.connections) ^ set(snapshot2.connections)
        return list(diff)

    def close_connection(self):
        self.connection.close()

# Example usage:
if __name__ == "__main__":
    db = SnapshotDatabase()

    snapshot = Snapshot(
        timestamp=1639987621.123,
        connections=[
            Network_Connection(local_address='127.0.0.1:1234', remote_address='192.168.1.1:5678', status='ESTABLISHED'),
            Network_Connection(local_address='192.168.1.2:8080', remote_address='10.0.0.1:80', status='LISTENING')
        ]
    )
    db.save_snapshot(snapshot)

    snapshots = db.get_snapshots()
    for s in snapshots:
        print(f"Timestamp: {s.timestamp}, Connections: {s.connections}")

    if len(snapshots) >= 2:
        diff_connections = db.compare_snapshots(snapshots[-2], snapshots[-1])
        print("Differences between the last two snapshots:", diff_connections)

    db.close_connection()
