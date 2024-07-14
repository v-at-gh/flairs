#!/usr/bin/env python3

import argparse
import json
from collections import defaultdict
from ipaddress import ip_address
from pathlib import Path

def parse_paths_to_jsons(json_paths_list):
    if isinstance(json_paths_list, str):
        if Path(json_paths_list).exists():
            with open(json_paths_list, 'r', encoding='utf-8') as f:
                file_paths = list(set(path.strip() for path in f.readlines()))
        elif ',' in json_paths_list:
            file_paths = list(set(path.strip() for path in json_paths_list.split(',')))

    for path in file_paths:
        if not Path(path).exists():
            file_paths.remove(path)
            print(f"File {path} does not exist.")
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except:
                file_paths.remove(path)
                print(f"File {path} is not a valid json.")
    return file_paths

def parse_jsons_from_files(file_paths):
    snis = []
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            snis.append(json.load(f))
    return snis

def merge_ip_addresses(dicts):
    merged_dict = defaultdict(set)
    for d in dicts:
        for key, values in d.items():
            merged_dict[key].update(values)
    merged_dict = {
        key: sorted(list(values), key=lambda a: ip_address(a))
        for key, values in merged_dict.items()
    }
    return merged_dict

def merge_server_names(dicts):
    merged_dict = defaultdict(set)
    for d in dicts:
        for key, values in d.items():
            merged_dict[key].update(values)
    merged_dict = {
        key: sorted(list(values), key=lambda a: a.split('.')[::-1])
        for key, values in merged_dict.items()
    }
    return merged_dict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('jsons', type=str)
    args = parser.parse_args()

    json_paths_list = args.jsons

    file_paths = parse_paths_to_jsons(json_paths_list)
    snis = parse_jsons_from_files(file_paths)

    dict_type = 'server_name_to_addresses'
    with open(f'{dict_type}.merged.json', 'w', encoding='utf-8') as f:
        try:
            json.dump(merge_ip_addresses(i[dict_type] for i in snis), f, ensure_ascii=False)
        except Exception as e:
            print(e)

    dict_type = 'address_to_server_names'
    with open(f'{dict_type}.merged.json', 'w', encoding='utf-8') as f:
        try:
            json.dump(merge_server_names(i[dict_type] for i in snis), f, ensure_ascii=False)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()
