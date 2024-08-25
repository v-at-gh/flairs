import subprocess
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple, Optional, Union
from datetime import datetime
from ipaddress import ip_address

from .common import TSHARK_BINARY, PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS
from .Tshark.Classes import Endpoint_Report, Conversation_Report
from ..tools import get_file_size
from src.tools import die

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
            filter: Optional[str] = None,
            get_address_to_server_names: bool = False,
            get_server_name_to_addresses: bool = False
    ) -> Dict[str, Union[Dict[str, List[str]], Any]]:
        # If none of these options are set--get both dictionaries.
        if get_address_to_server_names is False and get_server_name_to_addresses is False:
            get_address_to_server_names = True
            get_server_name_to_addresses = True
        server_name_field = 'tls.handshake.extensions_server_name'
        if filter is None: display_filter = server_name_field
        #TODO: implement filter expression validation
        # (Why? tshark will not run if filter is not valid!)
        # And here we are...
        else: display_filter = f"{server_name_field} and {filter}"
        command = [TSHARK_BINARY, "-n", "-r", pcap_file_path_str, "-Y", display_filter,
                   "-T", "fields", "-E", "separator=,",
                   "-e", "ip.dst", "-e", server_name_field]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0: die(result.returncode, f"Error: {result.stderr}")
            else:
                pairs = result.stdout.splitlines()
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
            sorted_address_to_server_names = dict(sorted(address_to_server_names.items(), key=lambda item: ip_address(item[0])))
        if get_server_name_to_addresses:
            for server_name in server_name_to_addresses:
                server_name_to_addresses[server_name].sort(key=lambda ip: ip_address(ip))
            # sorted_server_name_to_addresses = dict(sorted(server_name_to_addresses.items()))
            sorted_server_name_to_addresses = dict(
                sorted(
                    server_name_to_addresses.items(),
                    key=lambda k: k[0].split('.')[::-1]
            ))
        if get_address_to_server_names and get_server_name_to_addresses:
            resulting_dict = {
                'address_to_server_names': sorted_address_to_server_names,
                'server_name_to_addresses': sorted_server_name_to_addresses
            }
        elif get_address_to_server_names:  resulting_dict = {'address_to_server_names':  sorted_address_to_server_names}
        elif get_server_name_to_addresses: resulting_dict = {'server_name_to_addresses': sorted_server_name_to_addresses}
        return resulting_dict

    @staticmethod
    def get_endpoints_statistics_strings(
            pcap_file_path,
            proto: Union[str, List[str], Set[str], Tuple[str]]
            = PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS,
            display_filter: Optional[str] = None
    ) -> Optional[List[str]]:

        def _parse_proto_arg(proto):
            if isinstance(proto, (str, list, set, tuple)):
                if   isinstance(proto, str): protos = [p.strip() for p in proto.split(',')]
                elif isinstance(proto, (list,set,tuple)): protos = proto
            else: raise ValueError("The 'proto' argument must be a string or a list, set, or tuple.")
            unsupported_protos = [p for p in protos if p not in PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS]
            if unsupported_protos: raise ValueError(f"Unsupported protocols specified: {', '.join(unsupported_protos)}")
            else: return protos

        protos = _parse_proto_arg(proto)

        def create_expression(prefix, protos, display_filter=None) -> str:
            if display_filter is None: return " ".join(f"-z {prefix},{proto}" for proto in protos)
            else: return " ".join(f"-z {prefix},{proto},'{display_filter}'" for proto in protos)

        endpoints_expression = create_expression("endpoints", protos, display_filter)
        conversations_expression = create_expression("conv", protos, display_filter)
        command = (
            f"{TSHARK_BINARY} -n -r {pcap_file_path} -q"
            f" {endpoints_expression}"
            f" {conversations_expression}"
        )
        dump_stats = subprocess.run(command, shell=True, text=True, capture_output=True)
        if dump_stats.returncode != 0: print(dump_stats.stderr); return None
        else: conversation_reports = [stat for stat in dump_stats.stdout.split('='*80+'\n') if stat != '']; return conversation_reports

    @staticmethod
    def parse_conversations_reports(conversation_reports) -> list:
        parsed_reports = []
        report_classes = [
            (Conversation_Report, 'conversations', 'address_A'),
            (Endpoint_Report, 'endpoints', 'address')
        ]
        for report in conversation_reports:
            # for ReportClass, entry_key, sort_key in report_classes:
            for ReportClass, _, _ in report_classes:
                parsed_report = ReportClass.parse_report_page(report)
                if parsed_report and len(parsed_report.entries) > 0:
                    #TODO: fix sorting for IPv4 and IPv6 addresses
                    # getattr(parsed_report, entry_key).sort(key=lambda r: getattr(r, sort_key))
                    parsed_reports.append(parsed_report)
        return parsed_reports
