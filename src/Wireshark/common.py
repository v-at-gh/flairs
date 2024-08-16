#TODO: for this (and other constants for paths to binary executables)
# implement an algorithm to find a realpath to binary to make this project portable

WIRESHARK_BINARY = '/Applications/Wireshark.app/Contents/MacOS/Wireshark'
TSHARK_BINARY = '/opt/homebrew/bin/tshark'
CAPINFOS_BINARY = '/opt/homebrew/bin/capinfos'
PROTOS_SUPPORTED_BY_ENDPOINTS_AND_CONVERSATIONS = (
    "bluetooth", "bpv7", "dccp", "eth", "fc", "fddi", "ip", "ipv6",
    "ipx", "jxta", "ltp", "mptcp", "ncp", "opensafety", "rsvp", "sctp",
    "sll", "tcp", "tr", "udp", "usb", "wlan", "wpan", "zbee_nwk"
)
