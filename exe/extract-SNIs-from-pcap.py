#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser(description='Process a pcap or pcapng file and save SNIs as a JSON file.')
    parser.add_argument('pcap', type=str, help='Path to the pcap or pcapng file.')
    parser.add_argument('-f', '--filter', type=str, help='Filter expression for pcapng file traffic.')
    parser.add_argument('-i', '--indent', type=int, help='Set indentation value for resulting json.')
    parser.add_argument('-N', '--ntoa', action='store_true', help='Returns a json of server names and their addresses.')
    parser.add_argument('-S', '--aton', action='store_true', help='Returns a json of addresses and their server names.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
    parser.add_argument('-o', '--outfile', type=str,
                        help=('The path where the JSON file will be saved. '
                              'By default, it is saved next to the packet capture file with the suffix `.sni.json`.'))
    parser.add_argument('-w', '--overwrite', action='store_true', help='Overwrite existing json.')
    parser.add_argument('-s', '--stdout', action='store_true', help='Print the resulting json to stdout.')

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    from sys import exit

    args = parse_arguments()

    if not Path(args.pcap).exists():
        print(f"Error: The file {args.pcap} does not exist.")
        exit(1)

    from src.Wireshark.Tshark import dump_sni_to_json

    dump_sni_to_json(
        args.pcap,
        filter = args.filter,
        get_server_name_to_addresses = args.ntoa,
        get_address_to_server_names = args.aton,
    )

if __name__ == '__main__':
    main()

    # verbose: bool = True,
    # overwrite: bool = False,
    # save_to_file: bool = True,
    # file_suffix: Optional[str] = None,
    # path_to_file: Optional[str] = None,

    # #TODO: move the file saving logic to the executable script
    # if save_to_file:
    #     if not path_to_file:
    #         if not file_suffix:
    #             file_suffix = '.sni.json'
    #         elif not file_suffix.startswith('.') or file_suffix == '.':
    #             file_suffix = f'.{file_suffix}'
    #         data_json_path_obj = pcap_file_path_obj.with_suffix(file_suffix)
    #     elif isinstance(path_to_file, str):
    #         data_json_path_obj = Path(path_to_file)
    #     if not overwrite:
    #         if Path.exists(data_json_path_obj):
    #             raise Exception(f"File {data_json_path_obj} exists.")
    # if verbose: print(f"Collecting SNIs from handshakes of {pcap_file_path_str}")

    # #TODO: move the file saving logic to the executable script
    # if save_to_file:
    #     if verbose: print(f"Saving server names as JSON to: {data_json_path_obj}")
    #     with open(data_json_path_obj, 'w', encoding='utf-8') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=indent)
    #     if verbose: print("Saved successfully.\n")
    # else:
    #     print(json.dumps(data, ensure_ascii=False, indent=indent))
