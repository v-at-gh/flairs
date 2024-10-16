#/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))


CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from argparse import ArgumentParser, Namespace

from src.tools import die
from src.connectivity.proxy.shadowsocks import (
    gen_server_config, gen_client_config,
    transport_modes, supported_encryption_methods,
    gen_client_url_from_config
)

encryption_methods = [
    m for m in supported_encryption_methods if not m.startswith('2022-blake3')
]

class ArgHelp:
    endpoint = "endpoints' host:port"
    mode     = f"transport mode. One of: {', '.join(transport_modes)}"
    method   = f"encryption method. One of: {', '.join(encryption_methods)} "
    server_config = "path to server config"

def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('endpoint', type=str, help=ArgHelp.endpoint)
    parser.add_argument('-m', '--mode', type=str, help=ArgHelp.mode)
    parser.add_argument('-M', '--method', type=str, help=ArgHelp.method)
    parser.add_argument('-S', '--server-config', type=str, help=ArgHelp.server_config)

    return parser.parse_args()

import json

def main():
    args = parse_args()
    addr, port = args.endpoint.rsplit(':', 1)
    #TODO: implement port casting to `int`
    port = int(port)
    if args.mode:
        if args.mode in transport_modes: mode = args.mode
        else: die(1, f"Mode must be one of: {', '.join(transport_modes)}")
    else: mode = None

    if args.method:
        if args.method in encryption_methods: method = args.method
        else: die(1, f"method must be one of: {', '.join(encryption_methods)}")
    else: method = None

    if args.server_config:
        server_config = Path(args.server_config)
        with open(server_config, 'r', encoding='utf-8') as f:
            server_config = json.loads(f.read())
    else:
        server_config = gen_server_config(
            server=addr,
            server_port=port,
            mode=mode,
            method=method
        )
    client_config = gen_client_config(
        server_config=server_config
    )
    print(gen_client_url_from_config(client_config))
    # server_config_json = json.dumps(server_config, indent=4, ensure_ascii=False)
    # client_config_json = json.dumps(client_config, indent=4, ensure_ascii=False)
    # print('server_config_json')
    # print(server_config_json)
    # print()
    # print('client_config_json')
    # print(client_config_json)

if __name__ == '__main__':
    main()
