#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-c', '--capturing', action='store_true')
    parser.add_argument('-f', '--finished', action='store_true')
    parser.add_argument('-j', '--json', action='store_true')
    parser.add_argument('-q', '--no-headers', action='store_true')

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    from src.Utils.Lsof import get_open_pcap_files

    #TODO: find a way to get files open by dumpcap
    result = get_open_pcap_files(
        capturing=args.capturing,
        finished=args.finished,
    )
    if args.json:
        from json import dumps
        print(dumps(result, indent=4))
    else:
        for k in result.keys():
            if not args.no_headers: print(f"{k}:")
            for v in result[k]:
                print(v)

if __name__ == '__main__':
    main()
