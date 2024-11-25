#!/usr/bin/python3

import sys
import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace
from typing import NoReturn, Optional

prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))
from src.net_tools import construct_capture_filter_for_endpoint
from src.Wireshark.common import WIRESHARK_BINARY


CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

endpoints_list_path = prj_path / CONF_DIR / 'default_endpoints_filter.en0.csv'

ArgHelp = Namespace(
    interface="Network interface to run Wireshark",
    outfile="set the output filename",
    filter="packet filter in libpcap filter syntax",
    custom_filter=("path to csv file with endpoints (`address,proto,port`)"
                   " list to construct exclusion filter."),
    default_filter=(f"default capture filter constructed"
                    f" from file {endpoints_list_path}")
)


def parse_arguments() -> Namespace:

    parser = ArgumentParser()
    parser.add_argument('-i', '--interface',
                        type=str, help=ArgHelp.interface)
    parser.add_argument('-w', '--outfile',
                        type=str, help=ArgHelp.outfile)

    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        '-f', '--filter',
        type=str, help=ArgHelp.filter)
    filter_group.add_argument(
        '-c', '--custom-filter',
        type=str, help=ArgHelp.custom_filter)
    filter_group.add_argument(
        '-d', '--default-filter',
        action='store_true', help=ArgHelp.default_filter)

    return parser.parse_args()


def spawn_wireshark(
        interface:      Optional[str] = None,
        capture_filter: Optional[str] = None,
        outfile:        Optional[str] = None
) -> None:
    command = [WIRESHARK_BINARY, '--no-promiscuous-mode']
    if interface:
        command.extend(['-i', interface])
    if capture_filter:
        command.extend(['-f', capture_filter])
    if outfile:
        command.extend(['-w', outfile])
    command.append('-k')
    subprocess.Popen(command)


def construct_capture_filter(
        endpoints_list_path: Path = endpoints_list_path
) -> str:
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


def main() -> None:
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

    #TODO: implement multiple csv files processing,
    # eg: `-c 'telegram.csv,vpn_rkn.csv,vpn_work.csv'`
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