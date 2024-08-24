#!/usr/bin/env bash

#TODO: implement selectior for utility
# TCPDUMP_BINARY="/usr/sbin/tcpdump"
# TSHARK_BINARY="/Applications/Wireshark.app/Contents/MacOS/tshark"
WIRESHARK_BINARY="/Applications/Wireshark.app/Contents/MacOS/Wireshark"

verbose=false

# Default IP address if not provided
: "${IP_ADDRESS:=127.0.0.1}"

usage() {
    echo "Usage: $0 [-i IP_ADDRESS] [-f FILTER] [-F ADDITIONAL_FILTER] [-v]"
    echo "  -i IP_ADDRESS        Specify the IP address to search for (default: ${IP_ADDRESS})"
    echo "  -f FILTER            Specify the capture filter expression"
    echo "  -F ADDITIONAL_FILTER Append an additional filter expression to the default filter:"
    echo "  -v                   Enable verbose output"
    exit 1
}

while getopts "i:f:F:v" opt; do
    case ${opt} in
        i)
            IP_ADDRESS=$OPTARG
            ;;
        f)
            NEW_FILTER=$OPTARG
            ;;
        F)
            ADDITIONAL_FILTER=$OPTARG
            ;;
        v)
            verbose=true
            ;;
        *)
            usage
            ;;
    esac
done

# List of default connections combinations:
NETS="127.0.0.0/8,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
PORTS="22,1194"
#TODO: implement udp version as well
if [ -z "$NEW_FILTER" ]; then
    FILTER="not (tcp and "
    FILTER+="(src host ${IP_ADDRESS} and (dst net ${NETS//,/ or } and dst port ${PORTS//,/ or }))"
    FILTER+=" or "
    FILTER+="(dst host ${IP_ADDRESS} and (src net ${NETS//,/ or } and src port ${PORTS//,/ or }))"
    FILTER+=")"
else
    FILTER="$NEW_FILTER"
fi

if [ -n "$ADDITIONAL_FILTER" ]; then
    FILTER+=" and $ADDITIONAL_FILTER"
fi

#TODO change `verbose` to `dry-run` maybe, just to construct bidirectional filter
if [ "$verbose" = true ]; then
    echo "IP Address: $IP_ADDRESS"
    echo "Filter: $FILTER"
fi

find_iface_name() {
    IFS=$'\n'
    current_interface=""
    for line in $(ifconfig); do
        if [[ $line =~ ^[a-zA-Z0-9] ]]; then
            current_interface=${line}
        elif [[ $line =~ "inet " ]]; then
            if [[ $line =~ $IP_ADDRESS ]]; then
                current_interface="${current_interface%% *}"
                current_interface="${current_interface%:}"
                echo "$current_interface"
                return 0
            fi
        fi
    done
    return 1
}

trap "echo 'Script interrupted. Exiting...'; exit 1" SIGINT

while true; do
    IFACE=$(find_iface_name)
    if [[ -n "$IFACE" ]]; then
        echo "Gotcha! Interface: ${IFACE}"
        break
    fi
    $verbose && echo "Waiting for interface with IP ${IP_ADDRESS}..."
    sleep 0.05
done

$WIRESHARK_BINARY -f "${FILTER}" -i "${IFACE}" -k &
echo "Wireshark launched on interface ${IFACE}. You can now close this terminal."

exit 0
