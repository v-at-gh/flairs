import subprocess
from typing import Dict, List, Optional, Union


def run_lsof() -> str:
    open_files_lines_stdout = subprocess.run(
        ['lsof', '-nP'], capture_output=True, text=True, encoding='utf-8'
    ).stdout
    return open_files_lines_stdout

def get_open_pcap_files(
        lsof_stdout: Optional[str]  = None,
        finished:    bool = False,
        capturing:   bool = False
) -> Dict[str, List[str]]:

    # If none of options are set, then return both.
    if capturing is False and finished is False:
        capturing = True
        finished = True

    if lsof_stdout is None:
        open_files_lines_stdout = run_lsof().splitlines()
    else:
        open_files_lines_stdout = lsof_stdout.splitlines()

    open_pcap_files_lines = [
        line for line in open_files_lines_stdout
        if line.endswith(('.pcap', '.pcapng'))]

    # Under Linux, we don't get file descriptors of dumpcap process,
    # so we don't get the expected result.
    #TODO: find a solution to this problem
    open_pcap_files_captuing = set(
        '/'+line.split('/',maxsplit=1)[-1]
        for line in open_pcap_files_lines
        if line.startswith('dumpcap'))
    open_pcap_files = set(
        '/'+line.split('/',maxsplit=1)[-1]
        for line in open_pcap_files_lines)

    open_pcap_files_finished = open_pcap_files.difference(
        open_pcap_files_captuing)

    if capturing is True and finished is True:
        return {'finished': list(open_pcap_files_finished),
                'capturing': list(open_pcap_files_captuing)}
    elif capturing is True:
        return {'capturing': list(open_pcap_files_captuing)}
    elif finished is True:
        return {'finished': list(open_pcap_files_finished)}
