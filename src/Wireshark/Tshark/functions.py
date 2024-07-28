import subprocess
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# from src.Wireshark.common import PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS
from ..common import PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS
from .Classes import Report_Processor, Endpoint_Report, Conversation_Report
from ..Main import Tshark

FILE_BINARY = '/usr/bin/file'

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

def get_sni_dict(
        pcap_file_path_str,
        filter: Optional[str] = None,
        get_server_name_to_addresses: bool = False,
        get_address_to_server_names:  bool = False,
) -> Dict[str, Union[Dict[str, List[str]], Any]]:
    pcap_file_path_obj = Path(pcap_file_path_str)
    if not Path.exists(pcap_file_path_obj):
        print(f"File {pcap_file_path_str} does not exist.")
        return
    try:
        pcap_file_type = subprocess.run(
            [FILE_BINARY, pcap_file_path_str], text=True, capture_output=True
        ).stdout.strip()
    except Exception as e: raise e
    if not 'pcap capture file' in pcap_file_type and \
       not 'pcapng capture file' in pcap_file_type:
        raise Exception(f"File {pcap_file_path_str} is not packet capture file.")
    data = Tshark.get_ipaddr_tls_server_name_pairs(
        pcap_file_path_str,
        filter = filter,
        get_address_to_server_names = get_address_to_server_names,
        get_server_name_to_addresses = get_server_name_to_addresses
    )
    return data

def print_reports_as_table(pcap_file_path, print_report_header: bool = False):
    reports = collect_reports(pcap_file_path)
    reports.sort(key=lambda r: len(r.entries))
    for report in reports:
        print(report.as_pretty_table(print_report_header=print_report_header))

def gather_all_pcap_data(pcap_file_path):
    #TODO 0: Append data gathering with `capinfos`
    #TODO 1: Check if `pcap file` exists.
    #TODO 1: If we're saving statistics data to a file,
    #TODO 1:   then check if `data file` exists.
    #TODO 1:     Check if `data file` is valid statistic file.
    #TODO 1:     Get checksum from `pcap file`
    #TODO 1:     and compare it with the checksum from `data file`.
    #TODO 1: If checksums differ, then to a new `data file` adding timestamp-suffix before extension.
    reports = collect_reports(pcap_file_path)
    #TODO -1: It's a mess. Refactor the following into `Statistics_Processor` class:
    conversation_reports_json = '"Conversation reports": ['+', '.join(report.to_json() for report in reports if 'conversation' in report.header.lower())+']'
    endpoint_reports_json     = '"Endpoint reports": ['+', '.join(report.to_json() for report in reports if 'endpoint' in report.header.lower())+']'
    obj_json_str = '{'+ ', '.join([conversation_reports_json, endpoint_reports_json]) +'}'
    print(obj_json_str)

def test_reports_export_import(pcap_file_path) -> None:
    reports = collect_reports(pcap_file_path)
    reports.sort(key=lambda r: len(r.entries))
    for report in reports:
        print(
    f"({len(report.entries)}) {report.header}:"
    f"\n  json [ex|im]port works correctly:"
    f" {report == Report_Processor.from_json(report.to_json())}"
    f"\n  csv  [ex|im]port works correctly:"
    f" {report == Report_Processor.from_csv(report.to_csv())}"
        )

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pcap', type=str, help='Path to pcap or pcapng file to be processed.')
    args = parser.parse_args()
    test_reports_export_import(args.pcap)
    # print_reports_as_table(args.pcap) 
