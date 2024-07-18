#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

class Arg_help:
    filter    = 'Filter expression for pcapng file traffic.'
    indent    = 'Set indentation value for resulting json.'
    ntoa      = 'Returns a json of server names and their addresses.'
    aton      = 'Returns a json of addresses and their server names.'
    verbose   = 'Enable verbose output.'
    outfile   = ('The path where the JSON file will be saved. '
                 'By default, it is saved next to the packet capture file with the suffix `.sni.json`.')
    overwrite = 'Overwrite existing json.'
    stdout    = 'Print the resulting json to stdout.'

def parse_arguments() -> Namespace:
    parser = ArgumentParser(description='Process a pcap or pcapng file and save SNIs as a JSON file.')
    parser.add_argument('pcap', type=str, help='Path to the pcap or pcapng file.')
    parser.add_argument('-f', '--filter', type=str, help=Arg_help.filter)
    parser.add_argument('-i', '--indent', type=int, help=Arg_help.indent)
    parser.add_argument('-N', '--ntoa', action='store_true', help=Arg_help.ntoa)
    parser.add_argument('-S', '--aton', action='store_true', help=Arg_help.aton)
    parser.add_argument('-v', '--verbose', action='store_true', help=Arg_help.verbose)
    parser.add_argument('-o', '--outfile', type=str, help=Arg_help.outfile)
    parser.add_argument('-w', '--overwrite', action='store_true', help=Arg_help.overwrite)
    parser.add_argument('-s', '--stdout', action='store_true', help=Arg_help.stdout)
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    if not Path(args.pcap).exists():
        from sys import exit
        print(f"Error: The file {args.pcap} does not exist.")
        exit(1)

    from Wireshark.Tshark.functions import dump_sni_to_json

    #TODO: all of the declared arguments and error handling
    dump_sni_to_json(
        args.pcap,
        filter = args.filter,
        get_server_name_to_addresses = args.ntoa,
        get_address_to_server_names = args.aton,
    )

if __name__ == '__main__':
    main()
