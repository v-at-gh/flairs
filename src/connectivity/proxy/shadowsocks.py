import base64
import json
import subprocess
import urllib.parse
from typing import Literal, Optional

method_type = Literal[
    'plain', 'none', 'aes-128-gcm', 'aes-256-gcm', 'chacha20-ietf-poly1305',
    '2022-blake3-aes-128-gcm', '2022-blake3-aes-256-gcm', '2022-blake3-chacha20-poly1305'
]
#TODO: find out which applications support which encryption methods
# for example, `outline` (on apple platforms AFAIK) does not support 2022-blake3-* ciphers
supported_encryption_methods = method_type.__dict__['__args__']

transport_mode = Literal['tcp_only', 'tcp_and_udp', 'udp_only']
transport_modes = transport_mode.__dict__['__args__']

def gen_key(method: method_type = 'aes-256-gcm'):
    command = ['ssservice', 'genkey', '--encrypt-method', method]
    password = subprocess.run(command, text=True, capture_output=True).stdout.strip().rstrip('=')
    return password

from dataclasses import dataclass, field, asdict
from ipaddress import IPv4Address, IPv4Interface, IPv4Network

@dataclass
class Config:
    #TODO: implement other functions as methods
    server: IPv4Address
    server_port: int
    method: method_type
    password: str
    plugin: Optional[str] = None
    plugin_opts: Optional[str] = None
    plugin_args: list[str] = field(default_factory=list)
    plugin_mode: Optional[transport_mode] = None
    timeout: Optional[int] = None
    tcp_weight: Optional[float] = None
    udp_weight: Optional[float] = None
    acl: Optional[str] = None

def gen_server_config(
        server: str, server_port: int,
        local_address: str = '127.0.0.1',
        local_port: int = 1080,
        mode: Optional[transport_mode] = None,
        method: method_type = 'aes-256-gcm', password: Optional[str] = None,
        timeout: int = 300, fast_open: bool = False
) -> dict:
    if (server_port < 1 or server_port > 65535) or (local_port < 1 or local_port > 65535):
        raise ValueError("Port must be a number between 1 and 65535.")
    server_config = {}
    server_config['server'] = server
    server_config['server_port'] = server_port
    server_config['local_address'] = local_address
    server_config['local_port'] = local_port
    server_config['method'] = method
    if not password:
        server_config['password'] = gen_key(method)
    else:
        server_config['password'] = str(password) #TODO sanitize password
    server_config['timeout'] = timeout
    server_config['fast_open'] = fast_open
    if mode:
        if mode in transport_modes:
            server_config['mode'] = mode
        else:
            raise ValueError(f"Supportes transport modes are: {', '.join(transport_modes)}")
    return server_config

def process_server_config(server_config: dict) -> dict:

    return server_config

def gen_client_config(
        server_config: dict,
        local_address: str = '127.0.0.1',
        local_port: int = 1080
) -> dict:
    client_config = {}
    server_config_section = {
        'server': server_config['server'],
        'server_port': server_config['server_port'],
        'method': server_config['method'],
        'password': server_config['password'],
    }
    if 'mode' in server_config.keys():
        server_config_section.update({'mode': server_config['mode']})
        client_config['mode'] = server_config['mode']
    client_config['servers'] = [server_config_section]
    client_config['local_address'] = local_address
    client_config['local_port'] = local_port

    return client_config

def gen_client_url(
        server_addr: str,
        server_port: int,
        method: method_type = 'aes-256-gcm',
        password: Optional[str] = None,
        tag: Optional[str] = None
) -> str:
    if server_port < 1 or server_port > 65535:
        raise ValueError("Port must be a number between 1 and 65535.")
    if not password:
        password = gen_key(method)
    else:
        password = str(password) #TODO sanitize password
    credentials = f"{method}:{password}"
    encoded_credentials = base64.urlsafe_b64encode(credentials.encode()).decode().rstrip("=")
    uri = f"ss://{encoded_credentials}@{server_addr}:{server_port}"
    if tag:
        uri += f"#{urllib.parse.quote(tag)}"
    return uri

def gen_client_url_from_config(
        client_config,
        tag: Optional[str] = None
) -> str:
    server = client_config['servers'][0]['server']
    server_port = client_config['servers'][0]['server_port']
    method = client_config['servers'][0]['method']
    password = client_config['servers'][0]['password']
    credentials = f"{method}:{password}"
    encoded_credentials = base64.urlsafe_b64encode(credentials.encode()).decode().rstrip("=")
    uri = f"ss://{encoded_credentials}@{server}:{server_port}"
    if tag:
        uri += f"#{urllib.parse.quote(tag)}"
    return uri

#TODO: implement `save_config` as a single function which processes both types
def save_server_config(server_config: dict, dir_path: Optional[str] = None):
    server_endpoint = f"_{server_config['server']}-{server_config['server_port']}_"
    method = server_config['method']
    mode = server_config['mode']
    if dir_path:
        dir_path = f"{dir_path}/"
    else:
        dir_path = ''
    file_name = f"{dir_path}ss_server.{server_endpoint}.{mode}.{method}.test.json"
    # file_name = f"/Users/v/data/conf.d/ss_server.{server_config['method']}.test.json"
    with open(file_name, 'w', encoding='utf-8') as file:
        json_content = json.dumps(server_config, indent=4)
        file.write(json_content)
    print(f"Contents of: {file_name}")
    print(json_content)

def save_client_config(client_config: dict, dir_path: Optional[str] = None):
    if 'servers' in client_config.keys():
        if len(client_config['servers']) == 1:
            fields = {'server', 'server_port', 'method', 'mode'}
            if not fields.difference(set(client_config['servers'][0].keys())):
                print('HERE')
                server = client_config['servers'][0]['server']
                server_port = client_config['servers'][0]['server_port']
                method = client_config['servers'][0]['method']
                mode = client_config['servers'][0]['mode']
                server_endpoint = f"_{server}-{server_port}_"
            #TODO: implement else-case
        #TODO: implement else-case
    #TODO: implement else-case
    if dir_path:
        dir_path = f"{dir_path}/"
    else:
        dir_path = '' # save in pwd
    file_name = f"{dir_path}ss_client.{server_endpoint}.{mode}.{method}.test.json"
    with open(file_name, 'w', encoding='utf-8') as file:
        json_content = json.dumps(client_config, indent=4)
        file.write(json_content)
    print(f"Contents of: {file_name}")
    print(json_content)
    print('URI:')
    print(gen_client_url_from_config(client_config))

# test everything
server_config = gen_server_config('1.3.1.2', 443, method='chacha20-ietf-poly1305', mode='tcp_and_udp')
save_server_config(server_config)
print()
client_config = gen_client_config(server_config)
save_client_config(client_config)
print()