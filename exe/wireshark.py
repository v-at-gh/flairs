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
from typing import LiteralString, NoReturn, Optional

from src.net_tools import construct_capture_filter_for_endpoint
from src.Wireshark.common import WIRESHARK_BINARY

endpoints_list_path = prj_path / CONF_DIR / 'default_endpoints_filter.en0.csv'

class ArgHelp:
    interface      = "Network interface to run Wireshark"
    outfile        = "set the output filename"
    filter         = "packet filter in libpcap filter syntax"
    custom_filter  = "path to csv file with endpoints (`address,proto,port`) list to construct exclusion filter."
    default_filter = f"default capture filter constructed from file {endpoints_list_path}"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-i', '--interface',      type=str, help=ArgHelp.interface)
    parser.add_argument('-w', '--outfile',        type=str, help=ArgHelp.outfile)
    parser.add_argument('-f', '--filter',         type=str, help=ArgHelp.filter)
    parser.add_argument('-c', '--custom-filter',  type=str, help=ArgHelp.custom_filter)
    parser.add_argument('-d', '--default-filter', action='store_true',
                        help=ArgHelp.default_filter)
    return parser.parse_args()

def spawn_wireshark(
        interface:      Optional[str] = None,
        capture_filter: Optional[str] = None,
        outfile:        Optional[str] = None
):
    command = [WIRESHARK_BINARY]
    if interface:      command.extend(['-i', interface])
    if capture_filter: command.extend(['-f', capture_filter])
    if outfile:        command.extend(['-f', outfile])
    command.append('-k')
    subprocess.Popen(command)

def construct_capture_filter(
        endpoints_list_path: Path = endpoints_list_path
) -> LiteralString:
    if endpoints_list_path.exists():
        endpoints_list = []
        with open(endpoints_list_path, 'r') as file:
            for line in file.read().strip().splitlines():
                endpoints_list.append(line.split(','))
    endpoint_expressions = []
    #TODO: reduce resulting filter expression by combining same values of endpoints
    # goto `construct_capture_filter_for_endpoint` definition
    for enpoint_args in endpoints_list:
        endpoint_expressions.append(construct_capture_filter_for_endpoint(*enpoint_args))
    return ' and '.join(e for e in endpoint_expressions)

def main() -> NoReturn:
    args = parse_arguments()
    if args.interface:
        iface = args.interface
    else:
        iface = None

    if args.outfile:
        #TODO: check if file exists
        #TODO: add overwrite arg
        outfile = args.outfile
    else:
        outfile = None

    if args.custom_filter:
        custom_filter_path = Path(args.custom_filter)
        capture_filter = construct_capture_filter(custom_filter_path)
    else:
        if args.default_filter and args.filter:
            capture_filter = construct_capture_filter() + ' and ' + args.filter
        elif args.default_filter and not args.filter:
            capture_filter = construct_capture_filter()
        elif not args.default_filter and args.filter:
            capture_filter = args.filter
        else:
            capture_filter = None

    spawn_wireshark(
        interface=iface,
        capture_filter=capture_filter,
        outfile=outfile
    )

if __name__ == '__main__':
    main()