#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

class ArgHelp: ...

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('file', help='path to json file containing domain names and addresses dicts')
    parser.add_argument('-a', '--addresses', type=str, help='filter expression for host and/or network addresses')
    parser.add_argument('-n', '--domains', type=str, help='filter expression for domain names')
    parser.add_argument('-i', '--indent', type=int)

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from sys import path as sys_path
    from pathlib import Path
    sys_path.append(str(Path(__file__).resolve().parents[1]))

    from json import dumps
    print(dumps(args.__dict__))

if __name__ == '__main__':
    main()

