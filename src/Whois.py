#!/usr/bin/env python3
'''
Draft: whois reports processing utility.
The purpose of this module is to provide methods
for obtaining, storing, and processing whois reports.
'''
import os, re
from typing import List, Tuple, Dict
from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from ipaddress import IPv4Address, IPv4Network

comment_chars = ('%', '#')

@dataclass
class Report:
    path: str
    content: str = None #TODO: raw content should be removed after processing
    sections: List[List[str]] = None #TODO: for now content is divided into lists of lists of strings.
                                        # Should process them into dictionaries with `_process_sections`.
    ip_ranges: List[Tuple[IPv4Address]] = None
    ip_networks: List[IPv4Network] = None

    def __post_init__(self) -> None:
        self.content_lines = self._process_content()
        self.sections = self._split_to_sections()
        self.ip_ranges = self.find_ipv4_objects('range')
        self.ip_networks = self.find_ipv4_objects('network')
        delattr(self, 'content')

    def _process_content(self) -> List[str]:
        content_lines = [line for line in self.content.splitlines()]
        return content_lines

    def _split_to_sections(self) -> List[List[str]]:
        sections = []
        current_section = []
        
        for line in self.content_lines:
            if line.strip():
                current_section.append(line)
            elif current_section:
                sections.append(current_section)
                current_section = []
        if current_section:
            sections.append(current_section)
        return sections

    def _process_sections(self) -> Dict:
        #TODO: not really implemented yet.
        # We should iterate over sections to concatenate values
        # dictionary into entities.
        for section in self.sections:
            section_dict = {}
            for line in section:
                if not line.startswith(comment_chars):
                    key = line.split(':')[0].strip()
                    value = ''.join(line.split(':')[1:]).strip()
                    if key not in section_dict.keys():
                        section_dict.update({ key: [value] })
                    else:
                        section_dict[key].append(value)
            return section_dict

    def find_ipv4_objects(self, object_type) -> List[Tuple[IPv4Address]|IPv4Network]:
        ipv4_address_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        range_pattern = rf'\b({ipv4_address_pattern})\s*-\s*({ipv4_address_pattern})\b'
        network_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})\b'
        object_regex_map = {
            'range': re.compile(range_pattern),
            'network': re.compile(network_pattern),
        }
        object_regex = object_regex_map[object_type]
        object_list = []

        for line in self.content_lines:
            if not line.startswith(comment_chars):
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

def collect_reports(directory) -> List[Report]:
    reports = []
    for r in os.listdir(directory):
        path = os.path.join(directory, r)
        # now `errors='ignore'` is set to mitigate encoding errors.
        with open(path, 'r', errors='ignore') as file:
            content = file.read()
            r = Report(path, content)
            reports.append(r)
    return reports

def print_reports_as_indented_sections(reports) -> None:
    # how often do you think about the Roman Empire?
    # https://t.me/profunctor_io/9592
    for i, report in enumerate(reports, 1):
        print(f"{i}. {report.path}")
        for ii, section in enumerate(report.sections, 1):
            print(f"  {ii}.{' '+section[0] if len(section)==1 else ''}")
            if len(section) > 1:
                for iii, line in enumerate(section, 1):
                    print(f"    {iii}. {line}")
        print()

def main() -> None:
    default_directory = os.path.expanduser('~/data/net/ipv4')
    reports = collect_reports(default_directory)
    print_reports_as_indented_sections(reports)

if __name__ == '__main__':
    main()
