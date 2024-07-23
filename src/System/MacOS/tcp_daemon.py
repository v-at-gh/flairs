#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import sys
import hashlib
import subprocess
import time
import datetime
from pathlib import Path

C_COMPILER = '/usr/bin/cc'

def get_project_directory() -> Path:
    #TODO:... pretty self-explanatory
    return Path(__file__).resolve().parent.parent.parent.parent

SOURCES_SRCDIR_PATH = get_project_directory() / 'src/System/MacOS'
SOURCES_BINDIR_PATH = get_project_directory() / 'bin/System/MacOS'

Path.mkdir(SOURCES_BINDIR_PATH, parents=True, exist_ok=True)

PATH_TO_DAEMON_SRC     = SOURCES_SRCDIR_PATH / 'tcp_daemon.c'
PATH_TO_DAEMON_SRC_MD5 = SOURCES_SRCDIR_PATH / 'tcp_daemon.c.md5sum'
PATH_TO_DAEMON_BIN     = SOURCES_BINDIR_PATH / 'tcp_daemon'
# PATH_TO_DAEMON_BIN_MD5 = './tcp_daemon.md5sum'

def compile_daemon() -> subprocess.CompletedProcess[str]:
    COMPILER_ARGS= [C_COMPILER, PATH_TO_DAEMON_SRC, '-o', PATH_TO_DAEMON_BIN]
    result = subprocess.run(COMPILER_ARGS, capture_output=True, text=True)
    if result.returncode:
        print('EXIT CODE: '+str(result.returncode), file=sys.stderr)
        print('STDOUT:\n'+result.stdout, file=sys.stderr)
        print('STDERR:\n'+result.stderr, file=sys.stderr)
        print('Try to compile it yourself:', file=sys.stderr)
        print('# '+' '.join(str(a) for a in COMPILER_ARGS), file=sys.stderr)
        print(file=sys.stdout)
        sys.exit(254)
    return result

if not Path(PATH_TO_DAEMON_SRC).exists():
    print(f"Sources file {PATH_TO_DAEMON_SRC} is missing. Exiting...", file=sys.stderr)
    sys.exit(255)

SOURCE_MD5_CURRENT = hashlib.md5(open(PATH_TO_DAEMON_SRC, 'rb').read()).hexdigest()

if not Path(PATH_TO_DAEMON_BIN).exists():
    print(f"Binary file {PATH_TO_DAEMON_BIN} is missing. Compiling...", file=sys.stdout)
    result = compile_daemon()
BINARY_MD5_CURRENT = hashlib.md5(open(PATH_TO_DAEMON_BIN, 'rb').read()).hexdigest()

if not Path(PATH_TO_DAEMON_SRC_MD5).exists():
    with open(PATH_TO_DAEMON_SRC_MD5, 'w') as file:
        file.write(SOURCE_MD5_CURRENT)
else:
    with open(PATH_TO_DAEMON_SRC_MD5, 'r') as file:
        SOURCE_MD5_PREVIOUS = str(file.read())
    if SOURCE_MD5_PREVIOUS != SOURCE_MD5_CURRENT:
        print(f"Sources file {PATH_TO_DAEMON_SRC} has changed. Recompiling...", file=sys.stdout)
        result = compile_daemon()
        with open(PATH_TO_DAEMON_SRC_MD5, 'w') as file:
            file.write(SOURCE_MD5_CURRENT)

connections_big_list = []
def process_data(data):
    now = time.time()
    connections_list = []
    connections = data.strip().split('\t')
    for conn in connections:
        local, remote, state = conn.split(',')
        connections_list.append((local, remote, state))
    connections_big_list.append((now, connections_list))
    print(datetime.datetime.now(), len(connections_list), file=sys.stdout)
    sys.stdout.flush()

class ArgHelp:
    interval  = "interval for fetching a snapshot of the system's network connections at the moment in seconds"
    pipe_path = "path to the named pipe through which the daemon transmits a snapshot of network connections"

def main():
    DEFAULT_INTERVAL  = 1
    DEFAULT_PIPE_PATH = "/tmp/tcp_connections.pipe"

    from argparse import ArgumentParser, Namespace

    parser = ArgumentParser()
    parser.add_argument('-i', '--interval', type=float, help=ArgHelp.interval)
    parser.add_argument('-p', '--pipe-path', type=str, help=ArgHelp.pipe_path)
    args = parser.parse_args()

    if args.interval:
        try:
            float(args.interval)
            if args.interval > 0:
                interval = args.interval
            else:
                print(f"Interval must be a number more than zero", file=sys.stderr)
                sys.exit(254)
        except Exception as e:
            print(e, file=sys.stderr)
            exit(253)
    else: interval = DEFAULT_INTERVAL

    if args.pipe_path:
        pipe_path = args.pipe_path
    else: pipe_path = DEFAULT_PIPE_PATH

    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)

    daemon_pid = subprocess.Popen(
        [PATH_TO_DAEMON_BIN, "-i", str(interval), "-p", pipe_path]
    ).pid

    with open(pipe_path, 'r') as pipe_fd:
        try:
            while True:
                for line in pipe_fd:
                    if line: process_data(line)
                time.sleep(interval)
        except KeyboardInterrupt:
            os.kill(daemon_pid, 2)
            os.remove(pipe_path)

            print(file=sys.stdout)
            for i, s in enumerate(connections_big_list, 1):
                print(f"{i}. {datetime.datetime.fromtimestamp(s[0])}", file=sys.stdout)
                for j, c in enumerate(s[1], 1): print(f"  {j}. {c}", file=sys.stdout)

if __name__ == "__main__":
    main()
