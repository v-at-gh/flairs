#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from argparse import ArgumentParser, Namespace

class ArgHelp:
    pcap   = "path to the packet capture file"
    filter = "filter expression for packet capture file processing (wireshark `preview` syntax)"
    json   = "return stats as json (default)"
    csv    = "return stats as csv"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('pcap', type=str, help=ArgHelp.pcap)
    parser.add_argument('-f', '--filter', type=str, help=ArgHelp.filter)
    parser.add_argument('-j', '--json', action='store_true', help=ArgHelp.json)
    parser.add_argument('-c', '--csv', action='store_true', help=ArgHelp.csv)

    return parser.parse_args()

def test_reports_module(pcap_file_path):

    if Path(pcap_file_path).exists():
        from src.Wireshark.Tshark.functions import test_reports_export_import
        test_reports_export_import(pcap_file_path)
    else:
        from sys import exit, stderr
        print(f"File {pcap_file_path} does not exist.", file=stderr)
        exit(1)

def main() -> None:
    args = parse_arguments()

    test_reports_module(args.pcap)

if __name__ == '__main__':
    main()
