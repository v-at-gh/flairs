#!/usr/bin/env python3

import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace


prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# class ArgHelp:
#     ...


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-c', '--capturing', action='store_true')
    parser.add_argument('-f', '--finished', action='store_true')
    parser.add_argument('-j', '--json', action='store_true')
    parser.add_argument('-q', '--no-headers', action='store_true')

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    from src.System.Lsof import get_open_pcap_files

    #TODO: in Linux, find a way for an unprivileged user to get files open by dumpcap
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
