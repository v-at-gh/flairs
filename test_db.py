#!/usr/bin/env python3
# from json import dumps

from src.Netstat import Netstat
from src.Snapshot import Snapshot, SnapshotDatabase

# Example usage:
if __name__ == "__main__":
    # from pprint import pprint
    from time import time
    db = SnapshotDatabase()

    snapshot = Snapshot(
        timestamp=time(),
        connections=[
            connection.to_dict() for connection in Netstat.get_connections()
        ]
    )
    db.save_snapshot(snapshot)

    snapshots = db.get_snapshots()
    for s in snapshots:
        print(f"Timestamp: {s.timestamp}, Connections: {s.connections}")

    #TODO: implement coomparison function `compare_snapshots` in `Snapshot.py`
    if len(snapshots) >= 2:
        diff_connections = db.compare_snapshots(snapshots[-2], snapshots[-1])
        print("Differences between the last two snapshots:", diff_connections)

    db.close_connection()
