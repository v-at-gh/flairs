#!/usr/bin/env python3

from src.Netstat import Netstat
from src.Snapshot import Snapshot, SnapshotDatabase

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save current connetions to DB and print what's changed")
    parser.add_argument('-v', help="Print the last snapshot also.")
    args = parser.parse_args()

    from time import time
    db = SnapshotDatabase()

    #TODO: every connection is now hashed here.
    #  Figure out how to make the code more convenient and universal
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
    if args.v:
        s = snapshots[-1]
        print(f"Timestamp: {s.timestamp}, Connections: {s.connections}")

    #TODO: improve comparison function `compare_snapshots` in `Snapshot.py`
    if len(snapshots) >= 2:
        diff_connections = db.compare_snapshots(snapshots[-2], snapshots[-1])
        if len(diff_connections) > 0:
            from pprint import pprint
            print("Differences between the last two snapshots:")
            pprint(diff_connections)
        else:
            print('No connections changed')

    db.close_connection()
