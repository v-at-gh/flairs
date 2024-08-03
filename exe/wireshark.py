#!/usr/bin/python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

import subprocess
from argparse import ArgumentParser, Namespace
from typing import LiteralString, NoReturn

from src.net_tools import construct_capture_filter_for_endpoint
from src.Wireshark.common import WIRESHARK_BINARY

class ArgHelp:
    interface = "Network interface to run Wireshark"
    outfile   = "set the output filename"
    filter    = "packet filter in libpcap filter syntax"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-i', '--interface', type=str, help=ArgHelp.interface)
    parser.add_argument('-w', '--outfile',   type=str, help=ArgHelp.outfile)
    parser.add_argument('-f', '--filter',    type=str, help=ArgHelp.filter)
    return parser.parse_args()

def spawn_wireshark(interface=None, capture_filter=None):
    command = [WIRESHARK_BINARY]
    if interface:      command.extend(['-i', interface])
    if capture_filter: command.extend(['-f', capture_filter])
    command.append('-k')
    subprocess.Popen(command)

def construct_default_capture_filter() -> LiteralString:
    default_endpoints_filter_path = prj_path / CONF_DIR / 'default_endpoints_filter.en0.csv'
    if default_endpoints_filter_path.exists():
        endpoints_list = []
        with open(default_endpoints_filter_path, 'r') as file:
            for line in file.read().strip().splitlines():
                endpoints_list.append(line.split(','))
    endpoint_expressions = []
    for enpoint_args in endpoints_list:
        endpoint_expressions.append(construct_capture_filter_for_endpoint(*enpoint_args))
    return ' and '.join(e for e in endpoint_expressions)

def main() -> NoReturn:
    args = parse_arguments()
    if args.interface: iface = args.interface
    if args.outfile: pass #TODO: save packet capture files to cache directory
    if args.filter: capture_filter = args.filter
    else: capture_filter = construct_default_capture_filter()
    spawn_wireshark(interface=iface, capture_filter=capture_filter)

if __name__ == '__main__':
    main()