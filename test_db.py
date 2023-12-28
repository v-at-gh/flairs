#!/usr/bin/env python3

from src.Netstat import Netstat
from src.Snapshot import Snapshot, SnapshotDatabase

if __name__ == "__main__":
    from time import time
    from pprint import pprint
    db = SnapshotDatabase()

    snapshot = Snapshot(
        timestamp=time(),
        connections=[
            {
                'hash': connection.hash,
                'dict': connection.to_dict()
            } for connection in Netstat.get_connections()
        ]
    )
    db.save_snapshot(snapshot)

    snapshots = db.get_snapshots()
    for s in snapshots:
        print(f"Timestamp: {s.timestamp}, Connections: {s.connections}")

    #TODO: implement comparison function `compare_snapshots` in `Snapshot.py`
    if len(snapshots) >= 2:
        diff_connections = db.compare_snapshots(snapshots[-2], snapshots[-1])
        print("Differences between the last two snapshots:")
        pprint(diff_connections)

    db.close_connection()
