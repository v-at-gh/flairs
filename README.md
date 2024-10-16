### Under development. Use at your own risk.

# flairs

Some network-related stuff.

## usage

```sh
./flairs one-of-the-scripts [script_args]
```

## scripts

- exclude-addresses
- extract-SNI-from-pcap
- filter-SNI-json
- gen-vpn
- get-open-pcaps
- get-pcap-stats
- merge-SNI-jsons
- netstat
- whois-this

## requirements

- macOS
- python >= 3.9.6
- Wireshark (tshark and capinfos) >= 4.2.5
- netstat
- whois

## optional requirements

- ncurses (for console tui)
- flask (for web-interface)
