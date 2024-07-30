#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from argparse import ArgumentParser, Namespace

from src.tools import die

class ArgHelp:
    pcap   = "path to the packet capture file"
    test   = "test to run (conversion, gathering)"
    # filter = "filter expression for packet capture file processing (wireshark `preview` syntax)"
    # json   = "return stats as json (default)"
    # csv    = "return stats as csv"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('pcap', type=str, help=ArgHelp.pcap)
    parser.add_argument('-t', '--test', type=str, help=ArgHelp.test)
    #TODO: implement corresponding selectors:
    # parser.add_argument('-f', '--filter', type=str, help=ArgHelp.filter)
    # parser.add_argument('-j', '--json', action='store_true', help=ArgHelp.json)
    # parser.add_argument('-c', '--csv', action='store_true', help=ArgHelp.csv)
    return parser.parse_args()

def test_reports_module(pcap_file_path):
    if not Path(pcap_file_path).exists():
        die(1, f"File {pcap_file_path} does not exist.")
    from src.Wireshark.Tshark.functions import test_reports_export_import
    test_reports_export_import(pcap_file_path)

def test_data_gathering(pcap_file_path):
    if not Path(pcap_file_path).exists():
        die(1, f"File {pcap_file_path} does not exist.")
    from src.Wireshark.Tshark.functions import gather_all_pcap_data
    gather_all_pcap_data(pcap_file_path)

def main():
    args = parse_arguments()
    if args.test == 'gathering':
        test_data_gathering(args.pcap)
    elif args.test == 'conversion':
        test_reports_module(args.pcap)

if __name__ == '__main__':
    main()
