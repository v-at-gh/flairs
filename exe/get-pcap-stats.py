#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('pcap', type=str, help="path to the packet capture file")
    parser.add_argument('-f', '--filter', type=str, help="filter expression for packet capture file processing (wireshark `preview` syntax)")
    parser.add_argument('-j', '--json', action='store_true', help="return stats as json (default)")
    parser.add_argument('-c', '--csv', action='store_true', help="return stats as csv")

    return parser.parse_args()

def test_reports_module(pcap_file_path):
    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    if Path(pcap_file_path).exists():
        from src.Wireshark.Tshark import test_reports_export_import
        test_reports_export_import(pcap_file_path)
    else:
        from sys import exit, stderr
        print(f"File {pcap_file_path} does not exist.", file=stderr)
        exit(1)

def main() -> None:
    args = parse_arguments()

    from json import dumps
    print(dumps(args.__dict__, indent=2, ensure_ascii=False))

    test_reports_module(args.pcap)

if __name__ == '__main__':
    main()
