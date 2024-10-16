#!/usr/bin/env bash

show_help() {
    cat <<EOF
Usage: ${0##*/} [-i INTERFACE] [-c PACKET_COUNT] [-p PROTOCOL] [-f FILTER] [-o OUTPUT_FILE]
Capture, preview and seve network packets to file using tcpdump.

    -i INTERFACE      Specify the network interface to capture packets from (required).
    -c PACKET_COUNT   Number of packets to capture (default is 100000).
    -p PROTOCOL       Specify a protocol to capture (e.g., tcp, udp) (optional).
    -f FILTER         Provide an additional tcpdump filter (optional).
    -o OUTPUT_FILE    Specify an output file path to save the capture (optional).
                      If not provided, the file will be named using the current date and time.

Example:
    ${0##*/} -i eth0 -c 1000 -p tcp -f "port 80" -o mycapture.pcap
EOF
}

PACKET_COUNT=100000
OUTPUT_FILE=""

while getopts ":i:c:p:f:o:h" opt; do
	case $opt in
		i) IFACE="$OPTARG"
	;;
		c) PACKET_COUNT="$OPTARG"
	;;
		p) PROTOCOL="$OPTARG"
	;;
		f) FILTER="$OPTARG"
	;;
		o) OUTPUT_FILE="$OPTARG"
	;;
		h) show_help; exit 0
	;;
		\?) echo "Invalid option -$OPTARG" >&2; show_help; exit 1
	;;
		:) echo "Option -$OPTARG requires an argument." >&2; show_help; exit 1
	;;
	esac
done

if [ -z "$IFACE" ]; then
	echo "Error: Network interface is required."
	show_help
	exit 1
fi

TCPDUMP_CMD="tcpdump -c $PACKET_COUNT --packet-buffered --immediate-mode -i $IFACE -w -"
if [ -n "$PROTOCOL" ]; then TCPDUMP_CMD="$TCPDUMP_CMD $PROTOCOL"; fi
if [ -n "$FILTER" ];   then TCPDUMP_CMD="$TCPDUMP_CMD $FILTER"; fi

if [ -z "$OUTPUT_FILE" ]; then OUTPUT_FILE="$(date +%F.%T | tr ':' '-').${IFACE}.pcap"; fi

$TCPDUMP_CMD | tee "$OUTPUT_FILE" | tcpdump --packet-buffered --immediate-mode -nvvvA -r -
