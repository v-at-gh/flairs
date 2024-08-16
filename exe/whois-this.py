#!/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

WHOIS_DIR = CACHE_DIR / 'whois/ipv4'
WHOIS_DIR.mkdir(parents=True, exist_ok=True)

from argparse import ArgumentParser, Namespace
from src.net_tools import is_string_a_valid_ip_address

class ArgHelp:
    address =  "address to get info about"
    outfile = f"path to save a report (default is {WHOIS_DIR}/IPv4Address.whois.txt)"
    force   =  "overwrite whois report if it exists"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('address', type=str, help=ArgHelp.address)
    parser.add_argument('-o', '--outfile', type=str, help=ArgHelp.outfile)
    parser.add_argument('-f', '--force', action='store_true', help=ArgHelp.force)

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    print(is_string_a_valid_ip_address(args.address))

if __name__ == '__main__':
    main()
