#!/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from typing import NoReturn
from argparse import ArgumentParser, Namespace

from src.tools import die
from src.Wireshark.Tshark.functions import get_sni_dict

class Arg_help:
    filter    = 'Filter expression for pcapng file traffic.'
    indent    = 'Set indentation value for resulting json.'
    ntoa      = 'Returns a json of server names and their addresses.'
    aton      = 'Returns a json of addresses and their server names.'
    # verbose   = 'Enable verbose output.'
    # outfile  = ('The path where the JSON file will be saved. '
    #             'By default, it is saved next to the packet '
    #             'capture file with the suffix `.sni.json`.')
    # overwrite = 'Overwrite existing json.'
    stdout    = 'Print the resulting json to stdout.'

def parse_arguments() -> Namespace:
    parser = ArgumentParser(description='Process a pcap or pcapng file and save SNIs as a JSON file.')
    parser.add_argument('pcap', type=str, help='Path to the pcap or pcapng file.')
    parser.add_argument('-f', '--filter', type=str, help=Arg_help.filter)
    parser.add_argument('-i', '--indent', type=int, help=Arg_help.indent)
    parser.add_argument('-N', '--ntoa', action='store_true', help=Arg_help.ntoa)
    parser.add_argument('-A', '--aton', action='store_true', help=Arg_help.aton)
    # parser.add_argument('-v', '--verbose', action='store_true', help=Arg_help.verbose)
    # parser.add_argument('-o', '--outfile', type=str, help=Arg_help.outfile)
    # parser.add_argument('-w', '--overwrite', action='store_true', help=Arg_help.overwrite)
    # parser.add_argument('-s', '--stdout', action='store_true', help=Arg_help.stdout)
    return parser.parse_args()

def main() -> NoReturn:
    args = parse_arguments()

    if not Path(args.pcap).exists():
        die(1, f"Error: The file {args.pcap} does not exist.")

    # if args.outfile and Path(args.outfile).exists() and not args.overwrite:
    #     die(2, f"Error: The file {args.outfile} does not exist. Add `-w` to overwrite.")

    sni_dict = get_sni_dict(
        args.pcap,
        filter = args.filter,
        get_server_name_to_addresses = args.ntoa,
        get_address_to_server_names = args.aton,
    )

    from json import dump
    try: dump(sni_dict, fp=sys.stdout, ensure_ascii=False, indent=args.indent)
    except Exception as e: die(3, e)
    # if args.stdout:
    #     try:
    #         dump(sni_dict, fp=sys.stdout, ensure_ascii=False, indent=args.indent)
    #     except Exception as e: die(3, e)
    # if args.outfile:
    #     try:
    #         with open(args.outfile, 'w', encoding='utf-8') as outfile:
    #             dump(sni_dict, fp=outfile, ensure_ascii=False, indent=args.indent)
    #     except Exception as e: die(4, e)

    die(0)

if __name__ == '__main__':
    main()
