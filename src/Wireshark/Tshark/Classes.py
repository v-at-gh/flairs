import io
import json
import csv

from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Dict, Literal, Optional, Union
from collections import defaultdict
from ipaddress import IPv4Address, IPv6Address, ip_address
from copy import copy

from ...tools import cast_value, obj_to_stringified_dict

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
    def as_dict(self)-> dict[str, Union[int, float, str, IPv4Address, IPv6Address]]:
        return asdict(self)

    def to_stringified_dict(self) -> dict[str, Union[int, float, str]]:
        return obj_to_stringified_dict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_stringified_dict())

@dataclass
class _Base_Endpoint(Item_Processor):
    address: str
    packets:    int;    bytes: int
    tx_packets: int; tx_bytes: int
    rx_packets: int; rx_bytes: int
class Ethernet_Endpoint(_Base_Endpoint):    __annotations__ = _Base_Endpoint.__annotations__
class IEEE_802_11_Endpoint(_Base_Endpoint): __annotations__ = _Base_Endpoint.__annotations__
class ZigBee_Endpoint(_Base_Endpoint):      __annotations__ = _Base_Endpoint.__annotations__

@dataclass
class Network_Endpoint(Item_Processor):
    address: Union[IPv4Address, IPv6Address]
    packets:    int;    bytes: int
    tx_packets: int; tx_bytes: int
    rx_packets: int; rx_bytes: int
class IPv4_Endpoint(Network_Endpoint): __annotations__ = Network_Endpoint.__annotations__
class IPv6_Endpoint(Network_Endpoint): __annotations__ = Network_Endpoint.__annotations__

@dataclass
class Transport_Endpoint(Item_Processor):
    address: Union[IPv4Address, IPv6Address]; port: int
    packets:    int;    bytes: int
    tx_packets: int; tx_bytes: int
    rx_packets: int; rx_bytes: int
class TCP_Endpoint(Transport_Endpoint):  __annotations__ = Transport_Endpoint.__annotations__
class UDP_Endpoint(Transport_Endpoint):  __annotations__ = Transport_Endpoint.__annotations__
class SCTP_Endpoint(Transport_Endpoint): __annotations__ = Transport_Endpoint.__annotations__

@dataclass
class _Base_Conversation(Item_Processor):
    address_A:   str;  address_B: str
    frames_to_A:  int;  bytes_to_A: int;  units_to_A: str
    frames_to_B:  int;  bytes_to_B: int;  units_to_B: str
    total_frames: int; total_bytes: int; total_units: str
    relative_start: float; duration: float
class Ethernet_Conversation(_Base_Conversation):    __annotations__ = _Base_Conversation.__annotations__
class IEEE_802_11_Conversation(_Base_Conversation): __annotations__ = _Base_Conversation.__annotations__
class ZigBee_Conversation(_Base_Conversation):      __annotations__ = _Base_Conversation.__annotations__

@dataclass
class Network_Conversation(Item_Processor):
    address_A: Union[IPv4Address, IPv6Address]
    address_B: Union[IPv4Address, IPv6Address]
    frames_to_A:  int;  bytes_to_A: int;  units_to_A: str
    frames_to_B:  int;  bytes_to_B: int;  units_to_B: str
    total_frames: int; total_bytes: int; total_units: str
    relative_start: float; duration: float
class IPv4_Conversation(Network_Conversation): __annotations__ = Network_Conversation.__annotations__
class IPv6_Conversation(Network_Conversation): __annotations__ = Network_Conversation.__annotations__

@dataclass
class Transport_Conversation(Item_Processor):
    address_A: Union[IPv4Address, IPv6Address]; port_A: int
    address_B: Union[IPv4Address, IPv6Address]; port_B: int
    frames_to_A: int; bytes_to_A: int; units_to_A: str
    frames_to_B: int; bytes_to_B: int; units_to_B: str
    total_frames: int; total_bytes: int; total_units: str
    relative_start: float; duration: float
class TCP_Conversation(Transport_Conversation):  __annotations__ = Transport_Conversation.__annotations__
class UDP_Conversation(Transport_Conversation):  __annotations__ = Transport_Conversation.__annotations__
class SCTP_Conversation(Transport_Conversation): __annotations__ = Transport_Conversation.__annotations__


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
        'ZigBee Conversations': ZigBee_Conversation
    }

    @classmethod
    def parse_report_page(cls, report_str: str):
        for protocol, Report_class in cls.Classes_dict.items():
            if report_str.startswith(protocol):
                report_lines = report_str.splitlines()
                report_header = report_lines.pop(0).strip()
                if '<No Filter>' in report_lines[0]:
                    report_filter = ''; report_lines.pop(0)
                else:
                    report_filter = report_lines.pop(0).split(':', 1)[-1]
                # remove column headers--conversation headers span two rows
                if cls.__name__.startswith('Endpoint'):
                    report_lines.pop(0)
                elif cls.__name__.startswith('Conversation'):
                    report_lines.pop(0); report_lines.pop(0)
                report_content = report_lines
                objs_list = [Report_class.parse_str(c) for c in report_content]
                init_args = [report_header, report_filter, objs_list]
                resulting_report = cls(*init_args)
                return resulting_report

    def sort_entries(self, key, reverse: bool = False) -> None:
        if key in self.entries[0].as_dict.keys():
            if   isinstance(self, Endpoint_Report):     list_item = 'endpoints'
            elif isinstance(self, Conversation_Report): list_item = 'conversations'
            #TODO: a little hacky. Find a conventional way.
            eval(f"self.{list_item}.sort(key=lambda entry: entry.{key}, reverse={reverse})")
        # else:
        #     raise Exception(f"Sort key must be one of: {', '.join(self.entries[0].as_dict.keys())}")

    #TODO 0: make these methods universal for every instance
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

    #TODO 0: make these methods universal for every instance
    def to_pretty_table(
            self, separator: str = ' ',
            print_report_header: bool = True,
            merge_unit_columns: bool = False, #TODO join columns
            align: Union[None,
                Literal['left'],
                Literal['center'],
                Literal['right']
                ] = None,
    ) -> str:
        #TODO: recreate `tshark's` statistics output
        # (like in `-q -z [endpoints|conv],{proto}`)
        column_widths = self.calculate_column_widths()

        def _get_alignment_func(key) -> Callable:
            if not align:
                if "port" in key.lower() or "units" in key.lower(): return str.ljust
                else: return str.rjust
            else:
                if   align == 'right':  return str.rjust
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
        if print_report_header:
            table_list = [self.header, self.filter, header_row, *entry_rows]
        else:
            table_list = [header_row, *entry_rows]
        return '\n'.join(table_list)

    @classmethod
    def from_csv(cls, csv_str: str) -> Union[Conversation_Report, Endpoint_Report]:
        input_stream = io.StringIO(csv_str)
        reader = csv.reader(input_stream)
        header = next(reader)[0]
        if header.lower().endswith('endpoints'):
            resulting_class = Endpoint_Report; list_key = 'endpoints'
        elif header.lower().endswith('conversations'):
            resulting_class = Conversation_Report; list_key = 'conversations'
        else: raise ValueError("Unknown report type")
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

    @property
    def as_dict(self) -> Dict[str, Any]: return asdict(self)
    def to_stringified_dict(self): return obj_to_stringified_dict(self)
    def to_json(self, indent: Optional[int] = None) -> str:
        # if   isinstance(self, Endpoint_Report):     list_key = 'endpoints'
        # elif isinstance(self, Conversation_Report): list_key = 'conversations'
        # else: raise ValueError("Unknown report type")
        obj = self.to_stringified_dict()
        return json.dumps(obj, indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> Union[Conversation_Report, Endpoint_Report]:
        data = json.loads(json_str)
        if isinstance(data, dict) and 'endpoints' in data:
            list_key = 'endpoints'; init_class = Endpoint_Report
        elif isinstance(data, dict) and 'conversations' in data:
            list_key = 'conversations'; init_class = Conversation_Report
        else: raise ValueError("Invalid JSON structure")
        items = []
        for item_data in data[list_key]:
            item_class = cls.Classes_dict[data['header']]
            item = item_class(**{
                k: cast_value(v, item_class.__annotations__[k])
                for k, v in item_data.items()
            })
            items.append(item)
        return init_class(header=data['header'], filter=data['filter'], **{list_key: items})


@dataclass
class Endpoint_Report(Report_Processor):
    header: str; filter: str = ''
    endpoints: list = field(default_factory=list)
    Classes_dict = {
        Name: Class for Name, Class
        in Report_Processor.Classes_dict.items()
        if Name.endswith('Endpoints')
    }
    @property
    def entries(self): return self.endpoints


@dataclass
class Conversation_Report(Report_Processor):
    header: str; filter: str = ''
    conversations: list = field(default_factory=list)
    Classes_dict = {
        Name: Class for Name, Class
        in Report_Processor.Classes_dict.items()
        if Name.endswith('Conversations')
    }
    @property
    def entries(self): return self.conversations
