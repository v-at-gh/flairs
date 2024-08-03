#!/usr/bin/env python3

import sys

from argparse import ArgumentParser, Namespace, REMAINDER
from typing import NoReturn
from subprocess import run, Popen
from pathlib import Path

from src.tools import die

def get_script_directory() -> Path:
    return Path(__file__).resolve().parent / 'exe'

def list_available_scripts() -> list:
    script_dir = get_script_directory()
    scripts = [f.stem for f in script_dir.glob('*.py')]
    return scripts

def select_script(script_name: str) -> Path:
    script_dir = get_script_directory()
    script_path = script_dir / f"{script_name}.py"
    return script_path

class ArgHelp:
    description = "Run a specified script with arguments."
    script      = "Script to run (e.g., exclude-addresses)"
    script_args = "Arguments to pass to the script"

def parse_arguments() -> Namespace:
    available_scripts = list_available_scripts()
    script_list_str = ', '.join(script for script in available_scripts)

    parser = ArgumentParser(
        description=ArgHelp.description,
        epilog=f"Available scripts: {script_list_str}"
    )
    parser.add_argument('script', help=ArgHelp.script)
    parser.add_argument('script_args', nargs=REMAINDER, help=ArgHelp.script_args)
    return parser.parse_args()

def main() -> NoReturn:
    args = parse_arguments()
    script_name = args.script
    script_path = select_script(script_name)
    if script_path.exists():
        if script_path.stem == 'wireshark':
            try:
                Popen([sys.executable, script_path] + args.script_args)
            except Exception as e:
                die(255, f"An error occurred: {e}")
        else:
            try:
                result = run(
                    [sys.executable, script_path] + args.script_args,
                    capture_output=True, text=True
                )
                if not result.stderr:
                    die(result.returncode, result.stdout.strip())
                else:
                    die(result.returncode, result.stderr.strip())
            except Exception as e:
                die(result.returncode, f"An error occurred: {e}")
    else:
        available_scripts = list_available_scripts()
        print(f"Script '{script_name}' not found.", file=sys.stderr)
        print("Available scripts:")
        for script in available_scripts:
            print(f" - {script}")
        die(255)

if __name__ == '__main__':
    main()
