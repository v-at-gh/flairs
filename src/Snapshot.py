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
                    #TODO: think out the way to store objects
                    #  in a shorter text representation, ex:
                    #    123.tcp://127.1:22-127.2:1234
                    #  and save the full object representation
                    #    (into a separate table of a DB maybe)
                    #  (with `conn.as_dict`) as a blob.
                    #  Optianal: save files open by a process and it's env variables.
                    'dict': connection.to_dict()
                } for connection in Netstat.get_connections()
            ]
        )
        #TODO: we should not save every snapshot every time.
        # Instead we must implement some ware to compare a fresh
        # snapshot with the previous one, and if it differs, then save it,
        # otherwise make some note that the state of network connections has not changed.
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
    def compare_snapshots(
            self,
            snapshot_prev: Snapshot,
            snapshot_curr: Snapshot
        ) -> List[Network_Connection]:
        #TODO: reduce code repetition
        hashes_of_conns_in_prev = set([connection['hash'] for connection in snapshot_prev.connections])
        hashes_of_conns_in_curr = set([connection['hash'] for connection in snapshot_curr.connections])
        diff = hashes_of_conns_in_prev ^ hashes_of_conns_in_curr

        list_diff = list(diff)
        diff = {'previous': [], 'current': []}
        if len(list_diff) > 0:
            #TODO: improve logic for connections collecting
            for connection_hash in list_diff:
                #TODO: we're iterating over hashes of connections already
                #  so there's no need in list comprehensions. Think out some other way.
                connections_in_1 = [connection for connection in snapshot_prev.connections
                                    if connection['hash'] == connection_hash]
                if len(connections_in_1) > 0:
                    diff['previous'].append(connections_in_1)
                connections_in_2 = [connection for connection in snapshot_curr.connections
                                    if connection['hash'] == connection_hash]
                if len(connections_in_2) > 0:
                    diff['current'].append(connections_in_2)
        
        return diff

    def close_connection(self):
        self.connection.close()
