#!/usr/bin/env python3

import sys
import os
import hashlib
import subprocess
import time
import datetime
from argparse import ArgumentParser, Namespace
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
from src.tools import die


C_COMPILER = '/usr/bin/cc'


def get_project_directory() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


SOURCES_SRCDIR_PATH = get_project_directory() / 'src/System/MacOS'
SOURCES_BINDIR_PATH = get_project_directory() / 'bin/System/MacOS'

Path.mkdir(SOURCES_BINDIR_PATH, parents=True, exist_ok=True)

PATH_TO_DAEMON_SRC     = SOURCES_SRCDIR_PATH / 'inet_daemon.c'
PATH_TO_DAEMON_SRC_MD5 = SOURCES_SRCDIR_PATH / 'inet_daemon.c.md5sum'
PATH_TO_DAEMON_BIN     = SOURCES_BINDIR_PATH / 'inet_daemon'


def compile_daemon() -> subprocess.CompletedProcess[str]:
    COMPILER_ARGS= [C_COMPILER, PATH_TO_DAEMON_SRC, '-o', PATH_TO_DAEMON_BIN]
    result = subprocess.run(COMPILER_ARGS, capture_output=True, text=True)
    if result.returncode:
        err_msg = '\n'.join([
            'EXIT CODE: ' + str(result.returncode),
            'STDOUT:\n' + result.stdout,
            'STDERR:\n' + result.stderr,
            'Try to compile it yourself:\n',
            '# ' + ' '.join(str(a) for a in COMPILER_ARGS)+'\n'
        ])
        die(254, err_msg)
    return result


if not Path(PATH_TO_DAEMON_SRC).exists():
    die(255, f"Sources file {PATH_TO_DAEMON_SRC} is missing. Exiting...")


with open(PATH_TO_DAEMON_SRC, 'rb') as f:
    SOURCE_MD5_CURRENT = hashlib.md5(f.read()).hexdigest()

if not Path(PATH_TO_DAEMON_BIN).exists():
    print(f"Binary file {PATH_TO_DAEMON_BIN} is missing. Compiling...", file=sys.stdout)
    result = compile_daemon() #TODO: handle this case (min priority)

with open(PATH_TO_DAEMON_BIN, 'rb') as f:
    BINARY_MD5_CURRENT = hashlib.md5(f.read()).hexdigest()

if not Path(PATH_TO_DAEMON_SRC_MD5).exists():
    with open(PATH_TO_DAEMON_SRC_MD5, 'w') as file:
        file.write(SOURCE_MD5_CURRENT)
else:
    with open(PATH_TO_DAEMON_SRC_MD5, 'r') as file:
        SOURCE_MD5_PREVIOUS = str(file.read())
    if SOURCE_MD5_PREVIOUS != SOURCE_MD5_CURRENT:
        print(f"Sources file {PATH_TO_DAEMON_SRC} has changed. Recompiling...",
              file=sys.stdout)
        result = compile_daemon()
        with open(PATH_TO_DAEMON_SRC_MD5, 'w') as file:
            file.write(SOURCE_MD5_CURRENT)

connections_big_list = []


def process_data_and_print_to_stdout(data):
    now = time.time()
    connections_list = []
    connections = data.strip().split('\t')
    for conn in connections:
        connections_list.append(tuple(conn.split(',')))
    connections_big_list.append((now, connections_list))
    print(datetime.datetime.now(), len(connections_list), file=sys.stdout)
    sys.stdout.flush()


ArgHelp = Namespace(
    interval=("interval for fetching a snapshot of the system's"
              " network connections at the moment in seconds"),
    pipe_path=("path to the named pipe through which the daemon"
               " transmits snapshots of network connections")
)


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-i', '--interval', type=float, help=ArgHelp.interval)
    parser.add_argument('-p', '--pipe-path', type=str, help=ArgHelp.pipe_path)
    args = parser.parse_args()

    return args


def main():
    default_interval = 100000  # time to sleep in microseconds
    default_pipe_path = "/tmp/inet_daemon.pipe"

    args = parse_arguments()
    if args.interval:
        try:
            float(args.interval)
            if args.interval > 0:
                interval = float(args.interval*(10**6))
            else:
                die(254, "Interval must be a number more than zero")
        except Exception as e:
            die(253, e)
    else:
        interval = default_interval

    if args.pipe_path:
        pipe_path = args.pipe_path
    else:
        pipe_path = default_pipe_path

    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)

    daemon_pid = subprocess.Popen(
        [PATH_TO_DAEMON_BIN, "-i", str(interval), "-p", pipe_path]).pid

    with open(pipe_path, mode='r', encoding='utf-8') as pipe_fd:
        try:
            while True:
                for line in pipe_fd:
                    if line:
                        process_data_and_print_to_stdout(line)
                time.sleep(interval)
        except KeyboardInterrupt:
            os.kill(daemon_pid, 2)
            os.remove(pipe_path)
            print(file=sys.stdout)
            for i, s in enumerate(connections_big_list, 1):
                print(f"{i}. {datetime.datetime.fromtimestamp(s[0])}",
                      file=sys.stdout)
                for j, c in enumerate(s[1], 1):
                    print(f"  {j}. {c}", file=sys.stdout)
                print(file=sys.stdout)


if __name__ == "__main__":
    main()
