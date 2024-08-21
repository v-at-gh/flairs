#!/usr/bin/env python3

import sys
from pathlib import Path
prj_path = Path(__file__).resolve().parents[1]
sys.path.append(str(prj_path))

CONF_DIR = prj_path / 'data/config'
CONF_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = prj_path / 'data/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

from argparse import ArgumentParser, Namespace

class ArgHelp: ...

def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    #TODO: implement stdin/stdout json piping
    parser.add_argument('jsons', type=str, help='paths to json files to be merged')
    parser.add_argument('-o', '--outfile', type=str, help='a path to new merged json file')

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    from json import dumps
    print(dumps(args.__dict__, indent=4))

if __name__ == '__main__':
    main()
