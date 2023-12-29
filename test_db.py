#!/usr/bin/env python3

from src.Snapshot import SnapshotDatabase

def compare_snapshots():
    db = SnapshotDatabase()
    db.take_snapshot()

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save current connetions to DB and print what's changed")
    parser.add_argument('-v', help="Print the last snapshot also.")
    args = parser.parse_args()

    compare_snapshots()