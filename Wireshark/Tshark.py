import os
import subprocess
import io
import csv
import json
from typing import Any, Callable, Dict, List, Literal, Set, Tuple, Union
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from copy import copy
from dataclasses import dataclass, asdict, field
from ipaddress import ip_address, IPv4Address, IPv6Address

# `tshark` binary must be in your $PATH, overwise change it.
#TODO: validate binary.
TSHARK_BINARY = 'tshark'

PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS = {
    "bluetooth", "bpv7", "dccp", "eth", "fc", "fddi", "ip", "ipv6",
    "ipx", "jxta", "ltp", "mptcp", "ncp", "opensafety", "rsvp", "sctp",
    "sll", "tcp", "tr", "udp", "usb", "wlan", "wpan", "zbee_nwk"
}

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        print(f"Error getting file size: {e}")
        return 0

def cast_value(value, target_type) -> Union[
           int, float, str, IPv4Address, IPv6Address]:
    if target_type == Union[IPv4Address, IPv6Address]: return ip_address(value)
    elif target_type == int:
        if isinstance(value, int): return value
        else: return int(value.replace(',', ''))
    elif target_type == float: return float(value)
    elif target_type == str:   return str(value)


class Item_Processor:

    @classmethod
    def parse_str(cls, obj_str: str):
        obj_list = obj_str.split()
        if '<->' in obj_list: obj_list.remove('<->')
        resulting_obj_list = []
        fields = list(cls.__annotations__.values())
        def _has_transport_conversation_superclass(cls) -> bool:
            for base in cls.__bases__:
                if base.__name__ == 'Transport_Conversation':
                    return True
            return False
        if _has_transport_conversation_superclass(cls):
            # Processing `IPv*Address:port` entry
            for _ in range(2):
                address, port = obj_list.pop(0).rsplit(':', 1)
                resulting_obj_list.append(
                    cast_value(address, Union[IPv4Address, IPv6Address]))
                resulting_obj_list.append(cast_value(port, int))
            fields = fields[4:]
        for field_type in fields:
            resulting_obj_list.append(cast_value(obj_list.pop(0), field_type))
        resulting_obj = cls(*resulting_obj_list)
        return resulting_obj

    @property
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        obj = copy(self.as_dict)
        for k, v in self.as_dict.items():
            if isinstance(v, (IPv4Address, IPv6Address)):
                obj[k] = str(v)
        return json.dumps(obj)

@dataclass
class Base_Endpoint(Item_Processor):
    address: str
    packets: int
    bytes: int
    tx_packets: int
    tx_bytes: int
    rx_packets: int
    rx_bytes: int
class Ethernet_Endpoint(Base_Endpoint):
    __annotations__ = Base_Endpoint.__annotations__
class IEEE_802_11_Endpoint(Base_Endpoint):
    __annotations__ = Base_Endpoint.__annotations__
class ZigBee_Endpoint(Base_Endpoint):
    __annotations__ = Base_Endpoint.__annotations__

@dataclass
class Network_Endpoint(Item_Processor):
    address: Union[IPv4Address, IPv6Address]
    packets: int
    bytes: int
    tx_packets: int
    tx_bytes: int
    rx_packets: int
    rx_bytes: int
class IPv4_Endpoint(Network_Endpoint):
    __annotations__ = Network_Endpoint.__annotations__
class IPv6_Endpoint(Network_Endpoint):
    __annotations__ = Network_Endpoint.__annotations__

@dataclass
class Transport_Endpoint(Item_Processor):
    address: Union[IPv4Address, IPv6Address]
    port: int
    packets: int
    bytes: int
    tx_packets: int
    tx_bytes: int
    rx_packets: int
    rx_bytes: int
class TCP_Endpoint(Transport_Endpoint):
    __annotations__ = Transport_Endpoint.__annotations__
class UDP_Endpoint(Transport_Endpoint):
    __annotations__ = Transport_Endpoint.__annotations__
class SCTP_Endpoint(Transport_Endpoint):
    __annotations__ = Transport_Endpoint.__annotations__

@dataclass
class Base_Conversation(Item_Processor):
    address_A: str
    address_B: str
    frames_to_A: int
    bytes_to_A: int
    units_to_A: str
    frames_to_B: int
    bytes_to_B: int
    units_to_B: str
    total_frames: int
    total_bytes: int
    total_units: str
    relative_start: float
    duration: float
class Ethernet_Conversation(Base_Conversation):
    __annotations__ = Base_Conversation.__annotations__
class IEEE_802_11_Conversation(Base_Conversation):
    __annotations__ = Base_Conversation.__annotations__
class ZigBee_Conversation(Base_Conversation):
    __annotations__ = Base_Conversation.__annotations__

@dataclass
class Network_Conversation(Item_Processor):
    address_A: Union[IPv4Address, IPv6Address]
    address_B: Union[IPv4Address, IPv6Address]
    frames_to_A: int
    bytes_to_A: int
    units_to_A: str
    frames_to_B: int
    bytes_to_B: int
    units_to_B: str
    total_frames: int
    total_bytes: int
    total_units: str
    relative_start: float
    duration: float
class IPv4_Conversation(Network_Conversation):
    __annotations__ = Network_Conversation.__annotations__
class IPv6_Conversation(Network_Conversation):
    __annotations__ = Network_Conversation.__annotations__

@dataclass
class Transport_Conversation(Item_Processor):
    address_A: Union[IPv4Address, IPv6Address]
    port_A: int
    address_B: Union[IPv4Address, IPv6Address]
    port_B: int
    frames_to_A: int
    bytes_to_A: int
    units_to_A: str
    frames_to_B: int
    bytes_to_B: int
    units_to_B: str
    total_frames: int
    total_bytes: int
    total_units: str
    relative_start: float
    duration: float
class TCP_Conversation(Transport_Conversation):
    __annotations__ = Transport_Conversation.__annotations__
class UDP_Conversation(Transport_Conversation):
    __annotations__ = Transport_Conversation.__annotations__
class SCTP_Conversation(Transport_Conversation):
    __annotations__ = Transport_Conversation.__annotations__


# Satisfy type-hinting
class Conversation_Report: ...
class Endpoint_Report: ...


class Report_Processor:

    Classes_dict = {
        'Ethernet Endpoints': Ethernet_Endpoint,
        'IPv4 Endpoints': IPv4_Endpoint,
        'IPv6 Endpoints': IPv6_Endpoint,
        'TCP Endpoints': TCP_Endpoint,
        'UDP Endpoints': UDP_Endpoint,
        'SCTP Endpoints': SCTP_Endpoint,
        'IEEE 802.11 Endpoints': IEEE_802_11_Endpoint,
        'ZigBee Endpoints': ZigBee_Endpoint,

        'Ethernet Conversations': Ethernet_Conversation,
        'IPv4 Conversations': IPv4_Conversation,
        'IPv6 Conversations': IPv6_Conversation,
        'TCP Conversations': TCP_Conversation,
        'UDP Conversations': UDP_Conversation,
        'SCTP Conversations': SCTP_Conversation,
        'IEEE 802.11 Conversations': IEEE_802_11_Conversation,
        'ZigBee Conversations': ZigBee_Conversation,
    }

    @classmethod
    def parse_report_str(cls, report_str: str):
        for protocol, Report_class in cls.Classes_dict.items():
            if report_str.startswith(protocol):
                report_lines = report_str.splitlines()
                report_header = report_lines.pop(0).strip()
                if '<No Filter>' in report_lines[0]:
                    report_filter = ''
                    report_lines.pop(0)
                else:
                    report_filter = report_lines.pop(0).split(':', 1)[-1]
                # remove column headers -- conversation headers span two rows
                if cls.__name__.startswith('Endpoint'):
                    report_lines.pop(0)
                elif cls.__name__.startswith('Conversation'):
                    report_lines.pop(0)
                    report_lines.pop(0)
                report_content = report_lines
                objs_list = [Report_class.parse_str(c) for c in report_content]
                init_args = [report_header, report_filter, objs_list]
                resulting_report = cls(*init_args)
                return resulting_report

    def sort_entries(self, key, reverse=False) -> None:
        if key in self.entries[0].as_dict.keys():
            if   isinstance(self, Endpoint_Report):     list_item = 'endpoints'
            elif isinstance(self, Conversation_Report): list_item = 'conversations'
            #TODO: a little hacky. Find a conventional way.
            eval(f"self.{list_item}.sort(key=lambda entry: entry.{key}, reverse={reverse})")
        # else:
        #     raise Exception(f"Sort key must be one of: {', '.join(self.entries[0].as_dict.keys())}")

    @property
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def calculate_column_widths(self):
        column_widths = defaultdict(list)
        for k in self.entries[0].__annotations__.keys():
            column_widths[k].append(len(str(k)))
        for e in self.entries:
            for k, v in e.as_dict.items():
                column_widths[k].append(len(str(v)))
        for k in column_widths.keys():
            column_widths[k] = max(column_widths[k])
        return column_widths

    def as_pretty_table(
            self, separator: str = ' ',
            merge_unit_columns: bool = False, #TODO join columns
            align: Union[None,
                         Literal['left'], Literal['center'], Literal['right']
                        ] = None,
    ) -> str:
        column_widths = self.calculate_column_widths()

        def _get_alignment_func(key) -> Callable:
            if not align:
                if "port" in key.lower() or "units" in key.lower(): return str.ljust
                else: return str.rjust
            else:
                if align == 'right': return str.rjust
                elif align == 'center': return str.center
                else: return str.ljust

        header_row = separator.join(str.ljust(k, column_widths[k])
                                    for k in self.entries[0].as_dict.keys())
        # header_row = separator.join(
        #     _get_alignment_func(k)(k, column_widths[k])
        #     for k in self.entries[0].as_dict.keys())
        entry_rows = []
        for entry in self.entries:
            entry_rows.append(separator.join(
                _get_alignment_func(k)(str(v), column_widths[k])
                for k, v in entry.as_dict.items()))
        return '\n'.join([header_row, *entry_rows])

    @classmethod
    def from_csv(cls, csv_str: str) -> Union[Conversation_Report, Endpoint_Report]:
        input_stream = io.StringIO(csv_str)
        reader = csv.reader(input_stream)
        header = next(reader)[0]
        if header.lower().endswith('endpoints'):
            resulting_class = Endpoint_Report
            list_key = 'endpoints'
        elif header.lower().endswith('conversations'):
            list_key = 'conversations'
            resulting_class = Conversation_Report
        else:
            raise ValueError("Unknown report type")
        filter_line = next(reader)[0]
        filter_value = '' if filter_line.startswith('Filter:<No Filter>') else filter_line.split(':', 1)[1]
        field_names = next(reader)
        items = []
        for row in reader:
            item_data = {field: row[i] for i, field in enumerate(field_names)}
            item_class = cls.Classes_dict[header]
            item = item_class(**{
                k: cast_value(v, item_class.__annotations__[k])
                for k, v in item_data.items()
            })
            items.append(item)
        return resulting_class(header=header, filter=filter_value, **{list_key: items})

    def to_csv(self, dialect='excel') -> str:
        output = io.StringIO()
        writer = csv.writer(output, dialect)
        writer.writerow([self.header])
        writer.writerow([f"Filter:{self.filter if self.filter != '' else '<No Filter>'}"])
        if self.entries:
            writer.writerow(self.entries[0].__annotations__.keys())
        for entry in self.entries:
            writer.writerow([
                str(getattr(entry, k))
                if isinstance(getattr(entry, k), (IPv4Address, IPv6Address)) 
                else getattr(entry, k)
                for k in entry.__annotations__.keys()
            ])
        return output.getvalue()

    @classmethod
    def from_json(cls, json_str: str) -> Union[Conversation_Report, Endpoint_Report]:
        data = json.loads(json_str)
        if isinstance(data, dict) and 'endpoints' in data:
            list_key = 'endpoints'
            resulting_class = Endpoint_Report
        elif isinstance(data, dict) and 'conversations' in data:
            list_key = 'conversations'
            resulting_class = Conversation_Report
        else: raise ValueError("Invalid JSON structure")
        items = []
        for item_data in data[list_key]:
            item_class = cls.Classes_dict[data['header']]
            item = item_class(**{
                k: cast_value(v, item_class.__annotations__[k])
                for k, v in item_data.items()
            })
            items.append(item)
        return resulting_class(header=data['header'] , filter=data['filter'], **{list_key: items})

    def to_json(self, indent=None) -> str:
        obj = copy(self.as_dict)
        if   isinstance(self, Endpoint_Report):     list_key = 'endpoints'
        elif isinstance(self, Conversation_Report): list_key = 'conversations'
        else: raise ValueError("Unknown report type")
        for entry in obj[list_key]:
            for k, v in entry.items():
                if isinstance(v, (IPv4Address, IPv6Address)):
                    entry[k] = str(v)
        return json.dumps(obj, indent=indent, ensure_ascii=False)


@dataclass
class Endpoint_Report(Report_Processor):
    header: str
    filter: str = ''
    endpoints: list = field(default_factory=list)
    Classes_dict = {
        Name: Class for Name, Class in Report_Processor.Classes_dict.items()
        if Name.endswith('Endpoints')
    }

    @property
    def entries(self):
        return self.endpoints


@dataclass
class Conversation_Report(Report_Processor):
    header: str
    filter: str = ''
    conversations: list = field(default_factory=list)
    Classes_dict = {
        Name: Class for Name, Class in Report_Processor.Classes_dict.items()
        if Name.endswith('Conversations')
    }

    @property
    def entries(self):
        return self.conversations


class Tshark:

    @staticmethod
    def get_timestamp_of_first_frame_in_pcap_file(pcap_file_path) -> datetime:
        command = [TSHARK_BINARY, "-n", "-r", pcap_file_path, "-c", "1",
                   "-T", "fields", "-e", "frame.time_epoch"]
        timestamp = subprocess.run(command,
            capture_output=True, text=True, encoding='utf-8'
        ).stdout.strip()
        timestamp = datetime.fromtimestamp(float(timestamp))
        return timestamp

    @staticmethod
    def return_pcap_dict(pcap_file_path) -> Dict[str, Any]:
        pcap_dict = {
            'path': pcap_file_path,
            'size': get_file_size(pcap_file_path),
            'timestamp': Tshark.get_timestamp_of_first_frame_in_pcap_file(pcap_file_path),
        }
        return pcap_dict

    @staticmethod
    def get_ipaddr_tls_server_name_pairs(
            pcap_file_path_str,
            filter: str = None,
            get_address_to_server_names: bool = False,
            get_server_name_to_addresses: bool = False
    ):
        if get_address_to_server_names is False and get_server_name_to_addresses is False:
            get_address_to_server_names = True
            get_server_name_to_addresses = True
        server_name_field = 'tls.handshake.extensions_server_name'
        if filter is None: preview_filter = server_name_field
        else: preview_filter = f"{server_name_field} and {filter}"
        command = [TSHARK_BINARY, "-n", "-r", pcap_file_path_str, "-Y", preview_filter,
                   "-T", "fields", "-E", "separator=,",
                   "-e", "ip.dst", "-e", server_name_field]
        try:
            pairs = subprocess.run(command,
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.splitlines()
        except Exception as e:
            raise e
        pairs = set(p for p in [tuple(p.split(',')) for p in pairs if len(p.split(',')) == 2])
        if get_address_to_server_names:  address_to_server_names = defaultdict(list)
        if get_server_name_to_addresses: server_name_to_addresses = defaultdict(list)
        for address, server_name in pairs:
            if get_address_to_server_names:  address_to_server_names[address].append(server_name)
            if get_server_name_to_addresses: server_name_to_addresses[server_name].append(address)
        if get_address_to_server_names:
            for address in address_to_server_names: address_to_server_names[address].sort()
            sorted_address_to_server_names = dict(
                sorted(address_to_server_names.items(), key=lambda item: ip_address(item[0]))
            )
        if get_server_name_to_addresses:
            for server_name in server_name_to_addresses:
                server_name_to_addresses[server_name].sort(key=lambda ip: ip_address(ip))
            # sorted_server_name_to_addresses = dict(sorted(server_name_to_addresses.items()))
            sorted_server_name_to_addresses = dict(
                sorted(
                    server_name_to_addresses.items(),
                    key=lambda k: k[0].split('.')[::-1]
                )
            )
        if get_address_to_server_names and get_server_name_to_addresses:
            resulting_dict = {
                'address_to_server_names': sorted_address_to_server_names,
                'server_name_to_addresses': sorted_server_name_to_addresses
            }
        elif get_address_to_server_names:
            resulting_dict = {'address_to_server_names': sorted_address_to_server_names}
        elif get_server_name_to_addresses:
            resulting_dict = {'server_name_to_addresses': sorted_server_name_to_addresses}
        return resulting_dict

    @staticmethod
    def get_endpoints_statistics_strings(
            pcap_file_path,
            proto: Union[str, List[str], Set[str], Tuple[str]] = PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS,
            preview_filter: str = None
    ) -> Union[None, List[str]]:
        def _parse_proto_arg(proto):
            if isinstance(proto, (str, list, set, tuple)):
                if   isinstance(proto, str): protos = [p.strip() for p in proto.split(',')]
                elif isinstance(proto, (list,set,tuple)): protos = proto
            else:
                raise ValueError("The 'proto' argument must be a string or a list, set, or tuple.")
            unsupported_protos = [p for p in protos if p not in 
                PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS]
            if unsupported_protos:
                raise ValueError(f"Unsupported protocols specified: {', '.join(unsupported_protos)}")
            else:
                return protos

        protos = _parse_proto_arg(proto)

        def create_expression(prefix, protos, preview_filter=None) -> str:
            if preview_filter is None:
                return " ".join(f"-z {prefix},{proto}" for proto in protos)
            else:
                return " ".join(f"-z {prefix},{proto},'{preview_filter}'"
                                for proto in protos)

        endpoints_expression = create_expression("endpoints", protos, preview_filter)
        conversations_expression = create_expression("conv", protos, preview_filter)
        command = (
            f"{TSHARK_BINARY} -n -r {pcap_file_path} -q"
            f" {endpoints_expression}"
            f" {conversations_expression}"
        )
        dump_stats = subprocess.run(command, shell=True, text=True, capture_output=True)
        if dump_stats.returncode != 0:
            print(dump_stats.stderr)
            return None
        else:
            conversation_reports = [
                stat for stat in dump_stats.stdout.split('='*80+'\n')
                if stat != '']
            return conversation_reports

    @staticmethod
    def parse_conversations_reports(conversation_reports) -> list:
        parsed_reports = []
        report_classes = [
            (Conversation_Report, 'conversations', 'address_A'),
            (Endpoint_Report, 'endpoints', 'address')
        ]
        for report in conversation_reports:
            for ReportClass, entry_key, sort_key in report_classes:
                parsed_report = ReportClass.parse_report_str(report)
                if parsed_report and len(parsed_report.entries) > 0:
                    getattr(parsed_report, entry_key).sort(key=lambda r: getattr(r, sort_key))
                    parsed_reports.append(parsed_report)
        return parsed_reports

def collect_reports(
        pcap_file_path,
        proto=PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS,
        preview_filter=None
) -> List[Union[Conversation_Report, Endpoint_Report]]:
    reports = Tshark.parse_conversations_reports(
        Tshark.get_endpoints_statistics_strings(
            pcap_file_path,
            proto,
            preview_filter
        ))
    return reports

def dump_sni_to_json(
        pcap_file_path_str,
        filter: str = None,
        verbose: bool = True,
        overwrite: bool = False,
        save_to_file: bool = True,
        path_to_file: str = None,
        get_server_name_to_addresses: bool = False,
        get_address_to_server_names: bool = False,
        indent = None,
) -> None:
    pcap_file_path_obj = Path(pcap_file_path_str)
    if not Path.exists(pcap_file_path_obj):
        raise Exception(f"File {pcap_file_path_str} does not exist.")
    try:
        pcap_file_type = subprocess.run(
            ['file', pcap_file_path_str], text=True, capture_output=True
        ).stdout.strip()
    except Exception as e:
        raise e
    if not 'pcap capture file' in pcap_file_type and not 'pcapng capture file' in pcap_file_type:
        raise Exception(f"File {pcap_file_path_str} is not packet capture file.")
    if save_to_file:
        if not path_to_file:
            data_json_path_obj = pcap_file_path_obj.with_suffix('.sni.json')
        elif isinstance(path_to_file, str):
            data_json_path_obj = Path(path_to_file)
        if not overwrite:
            if Path.exists(data_json_path_obj):
                raise Exception(f"File {data_json_path_obj} exists.")
    if verbose: print(f"Collecting SNIs from handshakes of {pcap_file_path_str}")
    data = Tshark.get_ipaddr_tls_server_name_pairs(
        pcap_file_path_str,
        filter = filter,
        get_address_to_server_names = get_address_to_server_names,
        get_server_name_to_addresses = get_server_name_to_addresses
    )
    if save_to_file:
        if verbose: print(f"Saving server names as JSON to: {data_json_path_obj}")
        with open(data_json_path_obj, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        if verbose: print("Saved successfully.\n")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=indent))


def test_reports_export_import(pcap_file_path):
    reports = collect_reports(pcap_file_path)
    for report in reports:
        print(
    f"{report.header} ({len(report.entries)}):"
    f"\n  json [ex|im]port works correctly: {report == Report_Processor.from_json(report.to_json())}"
    f"\n  csv  [ex|im]port works correctly: {report == Report_Processor.from_csv(report.to_csv())}"
        )

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pcap', type=str, help='Path to pcap or pcapng file to be processed.')
    args = parser.parse_args()

    test_reports_export_import(args.pcap)