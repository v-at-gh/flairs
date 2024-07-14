#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--capturing', action='store_true')
parser.add_argument('-f', '--finished', action='store_true')
parser.add_argument('-j', '--json', action='store_true')
parser.add_argument('-q', '--no-headers', action='store_true')

args = parser.parse_args()

from Utils.Lsof import get_open_pcap_files

result = get_open_pcap_files(
    capturing=args.capturing,
    finished=args.finished,
)

if args.json:
    from json import dumps
    print(dumps(result, indent=4))
else:
    for i in result.keys():
        if not args.no_headers: print(f"{i}:")
        for j in result[i]:
            print(j)