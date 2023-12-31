#!/usr/bin/env python3

from src.Snapshot import SnapshotDatabase

def compare_snapshots() -> None:
    db = SnapshotDatabase()
    db.take_snapshot()

    snapshots = db.get_snapshots()
    if args.v:
        s = snapshots[-1]
        print(f"Timestamp: {s.timestamp}, Connections: {s.connections}")

    #TODO 0: improve comparison function `compare_snapshots` in `Snapshot.py`
    if len(snapshots) >= 2:
        previous = snapshots[-2]
        current = snapshots[-1]
        diff_connections = db.compare_snapshots(previous, current)
        if len(diff_connections['previous']) > 0 or len(diff_connections['current']) > 0:
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