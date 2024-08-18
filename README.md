# flairs

Some network-related stuff.

## usage

```sh
./flairs one-of-the-scripts [script_args]
```

## scripts

- exclude-addresses
- get-open-pcaps
- get-pcap-stats
- merge-SNI-jsons
- netstat
- extract-SNI-from-pcap
- filter-SNI-json
- whois-this
- gen-vpn

## requirements

- MacOS
- python >= 3.9.6
- netstat
- whois
- Wireshark (tshark and capinfos) >= 4.2.5

## optional requirements

- ncurses (for console tui)
- flask (for web-interface)
