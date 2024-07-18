#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from argparse import ArgumentParser, Namespace

#TODO: implement configuration file processing logic for, say `$HOME/.config/flairs/stuff.{conf|ini|yml|json}`
#TODO: and maybe even caching for, say `$HOME/.cache/flairs/{data,reports,statistics,etc}'
whois_data_dir = '/Users/v/data/net/ipv4'

class ArgHelp:
    address =  "address to get info about"
    outfile = f"path to save a report (default is {whois_data_dir}/IPv*.whois.txt)"
    force   =  "overwrite whois report if it exists"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('address', type=str, help=ArgHelp.address)
    parser.add_argument('-o', '--outfile', type=str, help=ArgHelp.outfile)
    parser.add_argument('-f', '--force', action='store_true', help=ArgHelp.force)

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from src.Whois import is_valid_ip_address

    print(is_valid_ip_address(args.address))

if __name__ == '__main__':
    main()