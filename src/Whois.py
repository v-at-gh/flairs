import os, sys, re
import subprocess
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
from ipaddress import ip_address, ip_network

from ipaddress import IPv4Address, IPv4Network

from pathlib import Path

def is_valid_ip_address(address: str) -> bool:
    try: ip_address(address); return True
    except ValueError: return False

def report_file_exists(path: str) -> bool:
    return Path(path).exists()

def invoke_whois_request(address: str):
    if is_valid_ip_address(address):
        try:
            result = subprocess.run(['whois', address], capture_output=True, text=True, encoding='utf-8')
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            sys.exit(2)
        return result.stdout
    else:
        print(f"Address {address} is not valid", file=sys.stderr)
        sys.exit(1)

COMMENT_CHARS = ('%', '#')


@dataclass
class Whois_report:
    path: str
    ip_ranges: list = field(default_factory=list)
    ip_networks: list = field(default_factory=list)

    @classmethod
    def parse_report_strings(cls, path_to_report: str):
        sections = []
        current_section = []
        for line in [l.strip() for l in path_to_report.splitlines()]:
            if line.strip():
                current_section.append(line)
            elif current_section:
                sections.append(current_section)
                current_section = []
        if current_section:
            sections.append(current_section)
        return cls(
            path = path_to_report
        )

    @staticmethod
    def find_ipv4_objects(self, object_type) -> List[Tuple[IPv4Address]|IPv4Network]:
        ipv4_address_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        ipv4_network_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})\b'
        ipv4_range_pattern = rf'\b({ipv4_address_pattern})\s*-\s*({ipv4_address_pattern})\b'

        object_regex_map = {
            'address': re.compile(ipv4_address_pattern),
            'network': re.compile(ipv4_network_pattern),
            'range': re.compile(ipv4_range_pattern),
        }
        object_regex = object_regex_map[object_type]
        object_list = []

        for line in self.content_lines:
            if not line.startswith(COMMENT_CHARS):
                matches = object_regex.findall(line)
                if matches:
                    try:
                        if object_type == 'network':
                            obj = ip_network(matches[0])
                        elif object_type == 'range':
                            first = ip_address(matches[0][0])
                            last = ip_address(matches[0][1])
                            obj = (first, last)
                        object_list.append((line.split(':')[0], obj))
                    except ValueError:
                        pass
        return object_list


# @dataclass
# class Report:
#     path: str
#     sections: List[List[str]] = None
#     ip_ranges: List[Tuple[IPv4Address]] = None
#     ip_networks: List[IPv4Network] = None

#     def __post_init__(self) -> None:
#         self.content_lines = self._process_content()
#         self.sections = self._split_to_sections()
#         self.ip_ranges = self.find_ipv4_objects('range')
#         self.ip_networks = self.find_ipv4_objects('network')
#         delattr(self, 'content')

#     def _process_content(self) -> List[str]:
#         content_lines = [line for line in self.content.splitlines()]
#         return content_lines

#     def _split_to_sections(self) -> List[List[str]]:
#         sections = []
#         current_section = []
        
#         for line in self.content_lines:
#             if line.strip():
#                 current_section.append(line)
#             elif current_section:
#                 sections.append(current_section)
#                 current_section = []
#         if current_section:
#             sections.append(current_section)
#         return sections

#     def _process_sections(self) -> Dict:
#         for section in self.sections:
#             section_dict = {}
#             for line in section:
#                 if not line.startswith(COMMENT_CHARS):
#                     key = line.split(':')[0].strip()
#                     value = ''.join(line.split(':')[1:]).strip()
#                     if key not in section_dict.keys():
#                         section_dict.update({ key: [value] })
#                     else:
#                         section_dict[key].append(value)
#             return section_dict

#     def find_ipv4_objects(self, object_type) -> List[Tuple[IPv4Address]|IPv4Network]:
#         ipv4_address_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

#         network_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})\b'
#         range_pattern = rf'\b({ipv4_address_pattern})\s*-\s*({ipv4_address_pattern})\b'
#         object_regex_map = {
#             'range': re.compile(range_pattern),
#             'network': re.compile(network_pattern),
#         }
#         object_regex = object_regex_map[object_type]
#         object_list = []

#         for line in self.content_lines:
#             if not line.startswith(COMMENT_CHARS):
#                 matches = object_regex.findall(line)
#                 if matches:
#                     try:
#                         if object_type == 'network':
#                             obj = ip_network(matches[0])
#                         elif object_type == 'range':
#                             first = ip_address(matches[0][0])
#                             last = ip_address(matches[0][1])
#                             obj = (first, last)
#                         object_list.append((line.split(':')[0], obj))
#                     except ValueError:
#                         pass
#         return object_list

# def collect_reports(directory) -> List[Report]:
#     reports = []
#     for r in os.listdir(directory):
#         path = os.path.join(directory, r)
#         # now `errors='ignore'` is set to mitigate encoding errors.
#         with open(path, 'r', errors='ignore') as file:
#             content = file.read()
#             r = Report(path, content)
#             reports.append(r)
#     return reports

# def print_reports_as_indented_sections(reports) -> None:
#     for i, report in enumerate(reports, 1):
#         print(f"{i}. {report.path}")
#         for ii, section in enumerate(report.sections, 1):
#             section_length = len(section)
#             print(f"  {ii}.{f' {section[0]}' if section_length == 1 else ''}")
#             if section_length > 1:
#                 for iii, line in enumerate(section, 1):
#                     print(f"    {iii}. {line}")
#         print()

# def main() -> None:
#     default_directory = os.path.expanduser('~/data/net/ipv4')
#     reports = collect_reports(default_directory)
#     print_reports_as_indented_sections(reports)

# if __name__ == '__main__':
#     main()
