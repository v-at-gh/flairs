#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from Wireshark.Tshark import dump_sni_to_json


def main():
    parser = argparse.ArgumentParser(description='Process a pcap or pcapng file and save SNIs as a JSON file.')
    parser.add_argument('pcap', type=str, help='Path to the pcap or pcapng file.')
    parser.add_argument('-f', '--filter', type=str, help='Filter expression for pcapng file traffic.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
    parser.add_argument('-s', '--stdout', action='store_true', help='Print the resulting json to stdout.')
    parser.add_argument('-o', '--outfile', type=str, help='The path where the JSON file will be saved. By default, it is saved next to the packet capture file with the suffix `.sni.json`.')
    parser.add_argument('-w', '--overwrite', action='store_true', help='Overwrite existing json.')
    parser.add_argument('-N', '--ntoa', action='store_true', help='Returns a json of server names and their addresses.')
    parser.add_argument('-S', '--aton', action='store_true', help='Returns a json of addresses and their server names.')
    parser.add_argument('-i', '--indent', type=int, help='Set indentation value.')

    args = parser.parse_args()

    pcap_file_path_obj = Path(args.pcap)

    if not pcap_file_path_obj.exists():
        print(f"Error: The file {pcap_file_path_obj} does not exist.")
        sys.exit(1)

    dump_sni_to_json(
        pcap_file_path_obj,
        filter=args.filter,
        verbose=args.verbose,
        overwrite=args.overwrite,
        save_to_file=not args.stdout,
        path_to_file=args.outfile,
        get_server_name_to_addresses=args.ntoa,
        get_address_to_server_names=args.aton,
        indent=args.indent,
    )

if __name__ == '__main__':
    main()
