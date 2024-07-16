#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-r', '--resolve', action='store_true', help="resolve host names")
    parser.add_argument('-n', '--numeric', action='store_true', help="don't resolve service names")
    parser.add_argument('-a', '--all', action='store_true', help="display all sockets")
    parser.add_argument('-l', '--listening', action='store_true', help="display listening sockets")
    parser.add_argument('-p', '--processes', action='store_true', help="show process using socket")
    parser.add_argument('-t', '--tcp', action='store_true', help="display only TCP sockets")
    parser.add_argument('-u', '--udp', action='store_true', help="display only UDP sockets")

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    from json import dumps
    print(dumps(args.__dict__))

if __name__ == '__main__':
    main()



# import argparse
# import json
# from collections import defaultdict
# from typing import Any, List, Dict
# from ipaddress import ip_address

# def parse_paths_to_jsons(json_paths_list) -> list[str]:
#     if isinstance(json_paths_list, str):
#         if Path(json_paths_list).exists():
#             with open(json_paths_list, 'r', encoding='utf-8') as f:
#                 file_paths = list(set(path.strip() for path in f.readlines()))
#         elif ',' in json_paths_list:
#             file_paths = list(set(path.strip() for path in json_paths_list.split(',')))

#     for path in file_paths:
#         if not Path(path).exists():
#             file_paths.remove(path)
#             print(f"File {path} does not exist.")
#         else:
#             try:
#                 with open(path, 'r', encoding='utf-8') as f:
#                     json.load(f)
#             except:
#                 file_paths.remove(path)
#                 print(f"File {path} is not a valid json.")
#     return file_paths

# def parse_jsons_from_files(file_paths) -> List[Dict[str, Any]]:
#     snis = []
#     for path in file_paths:
#         with open(path, 'r', encoding='utf-8') as f:
#             snis.append(json.load(f))
#     return snis

# def merge_ip_addresses_dicts(dicts) -> Dict[Any, List]:
#     merged_dict = defaultdict(set)
#     for d in dicts:
#         for key, values in d.items():
#             merged_dict[key].update(values)
#     merged_dict = {
#         # Sorts addresses as objects, not strings.
#         # So if there are both IPv4 and IPv6 addresses,
#         # then it fails.
#         #TODO: mitigate error;
#         #TODO: implement a mechanism for selecting sorting criteria.
#         key: sorted(list(values), key=lambda a: ip_address(a))
#         for key, values in merged_dict.items()
#     }
#     return merged_dict

# def merge_server_names_dicts(dicts) -> Dict[Any, List]:
#     merged_dict = defaultdict(set)
#     for d in dicts:
#         for key, values in d.items():
#             merged_dict[key].update(values)
#     merged_dict = {
#         # Sorts domain names from top level to bottom;
#         # if there is no dot in domain name, this will fail, so
#         #TODO: mitigate error;
#         #TODO: implement a mechanism for selecting sorting criteria.
#         key: sorted(list(values), key=lambda a: a.split('.')[::-1])
#         for key, values in merged_dict.items()
#     }
#     return merged_dict

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('jsons', type=str)
#     #TODO: implement option to set output file path.
#     args = parser.parse_args()

#     json_paths_list = args.jsons

#     file_paths = parse_paths_to_jsons(json_paths_list)
#     snis = parse_jsons_from_files(file_paths)

#     dict_type = 'server_name_to_addresses'
#     with open(f'{dict_type}.merged.json', 'w', encoding='utf-8') as f:
#         try:
#             json.dump(merge_ip_addresses_dicts(i[dict_type] for i in snis), f, ensure_ascii=False)
#         except Exception as e:
#             print(e)

#     dict_type = 'address_to_server_names'
#     with open(f'{dict_type}.merged.json', 'w', encoding='utf-8') as f:
#         try:
#             json.dump(merge_server_names_dicts(i[dict_type] for i in snis), f, ensure_ascii=False)
#         except Exception as e:
#             print(e)

# if __name__ == '__main__':
#     main()
