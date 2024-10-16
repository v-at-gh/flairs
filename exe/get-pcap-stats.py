#!/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from argparse import ArgumentParser, Namespace

from src.tools import die

class ArgHelp:
    pcap   = "path to the packet capture file"
    test   = "test to run (conversion, gathering)"
    json   = "return stats as json (default)"
    csv    = "return stats as csv"
    table  = "return stats as a pretty table"
    # filter = "filter expression for packet capture file processing (wireshark `display` syntax)"

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('pcap', type=str, help=ArgHelp.pcap)
    parser.add_argument('-j', '--json', action='store_true', help=ArgHelp.json)
    parser.add_argument('-c', '--csv',  action='store_true', help=ArgHelp.csv)
    parser.add_argument('-T', '--table',  action='store_true', help=ArgHelp.table)
    parser.add_argument('-t', '--test', type=str, help=ArgHelp.test)
    #TODO: implement corresponding selectors:
    # parser.add_argument('-f', '--filter', type=str, help=ArgHelp.filter)
    return parser.parse_args()

def test_reports_module(pcap_file_path):
    if not Path(pcap_file_path).exists():
        die(1, f"File {pcap_file_path} does not exist.")
    from src.Wireshark.Tshark.functions import test_reports_export_import
    test_reports_export_import(pcap_file_path)

def test_data_gathering(pcap_file_path):
    if not Path(pcap_file_path).exists():
        die(1, f"File {pcap_file_path} does not exist.")
    from src.Wireshark.Tshark.functions import gather_all_pcap_data_and_print_as_table
    gather_all_pcap_data_and_print_as_table(pcap_file_path)
    # from src.Wireshark.Tshark.functions import gather_all_pcap_data_as_json
    # gather_all_pcap_data_as_json(pcap_file_path)

def return_conversations_report():
    raise NotImplementedError

def return_endpoints_report():
    raise NotImplementedError

from src.Wireshark.Tshark.functions import gather_all_pcap_data_as_json


def main():
    args = parse_arguments()
    pcap = Path(args.pcap)
    if pcap.exists() and pcap.is_file():
        result = gather_all_pcap_data_as_json(pcap)
        die(0, result)
    elif not pcap.exists():
        die(1, f"File {pcap} does not exist")
    elif not pcap.is_file():
        die(1, f"{pcap} is not a regular file")

    # if args.test:
    #     if   args.test == 'gathering':  test_data_gathering(args.pcap)
    #     elif args.test == 'conversion': test_reports_module(args.pcap)
    #     else: die(2, 'choose one of -t args: gathering or conversion')
    # else:
    #     if  args.json:
    #     elif args.csv:

if __name__ == '__main__':
    main()
