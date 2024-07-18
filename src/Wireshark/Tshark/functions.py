import subprocess
from typing import Any, Dict, List, Set, Tuple, Optional, Union
from pathlib import Path

# from src.Wireshark.common import PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS
from .common import PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS
from .Classes import Report_Processor, Endpoint_Report, Conversation_Report
from .Main import Tshark

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
        get_address_to_server_names: bool = False,
) -> Dict[str, Dict[str, List[str]] | Any]:

    pcap_file_path_obj = Path(pcap_file_path_str)
    if not Path.exists(pcap_file_path_obj):
        print(f"File {pcap_file_path_str} does not exist.")
        return
    try:
        pcap_file_type = subprocess.run(
            ['file', pcap_file_path_str], text=True, capture_output=True
        ).stdout.strip()
    except Exception as e:
        raise e
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

def test_reports_export_import(pcap_file_path):
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
