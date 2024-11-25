#!/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from argparse import ArgumentParser, Namespace
from pathlib import Path

from src.tools import die
from src.net_tools import (
    construct_capture_filter, construct_display_filter,
    construct_filters
)


ArgHelp = Namespace(
    csv='path to csv file',
    exclude='construct filter to exclude packets from capture',
    capture='construct capture filter for tcpdump, tshark, or wireshark',
    display='construct display filter for tshark or wireshark'
)


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('csv', type=str, help=ArgHelp.csv)
    parser.add_argument('-e', '--exclude',
                        action='store_true', help=ArgHelp.exclude)
    parser.add_argument('-c', '--capture',
                        action='store_true', help=ArgHelp.capture)
    parser.add_argument('-d', '--display',
                        action='store_true', help=ArgHelp.display)
    return parser.parse_args()


def process_csv_path(csv_path_str: str) -> str:
    csv_path = Path(csv_path_str)
    if not csv_path.exists():
        die(1, f"File {csv_path} does not exist")
    if not csv_path.is_file():
        die(1, f"File {csv_path} is not a file")
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_content = file.read()
    return csv_content


def process_args(args: Namespace):
    #TODO: implement stdin processing
    csv_paths = []
    if ',' in args.csv:
        for csv_path in [p.strip() for p in args.csv.split(',')]:
            csv_content = process_csv_path(csv_path)
            csv_paths.append(csv_content.strip())
        csv_content = '\n'.join(p for p in csv_paths if p != '').strip()
    else:
        csv_path = args.csv
        csv_content = process_csv_path(csv_path)

    if args.exclude:
        goal = 'exclude'
    else:
        goal = 'include'

    if args.capture and not args.display:
        print(construct_capture_filter(csv_content, goal=goal))
    elif not args.capture and args.display:
        print(construct_display_filter(csv_content, goal=goal))
    else:
        filters = construct_filters(csv_content, goal=goal)
        for filter in filters:
            print(filter)


def main():
    args = parse_arguments()
    process_args(args)


if __name__ == '__main__':
    main()
