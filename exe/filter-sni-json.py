#!/usr/bin/env python3

import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace
from json import dumps

prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


ArgHelp = Namespace(
    file='path to json file containing domain names and addresses dicts',
    addresses='filter expression for host and/or network addresses',
    domains='filter expression for domain names',
    indent='set json indentation'
)


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('file', help=ArgHelp.file)
    parser.add_argument('-a', '--addresses', type=str, help=ArgHelp.addresses)
    parser.add_argument('-n', '--domains', type=str, help=ArgHelp.domains)
    parser.add_argument('-i', '--indent', type=int, help=ArgHelp.indent)

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    print(dumps(args.__dict__))


if __name__ == '__main__':
    main()
