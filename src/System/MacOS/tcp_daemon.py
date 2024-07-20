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
SOURCES_BINDIR_PATH = get_project_directory() / 'bin'

if not SOURCES_BINDIR_PATH.exists():
    Path.mkdir(SOURCES_BINDIR_PATH)

PATH_TO_DAEMON_SRC     = SOURCES_SRCDIR_PATH / 'tcp_daemon.c'
PATH_TO_DAEMON_SRC_MD5 = SOURCES_SRCDIR_PATH / 'tcp_daemon.c.md5sum'
PATH_TO_DAEMON_BIN     = SOURCES_BINDIR_PATH / 'tcp_daemon'
# PATH_TO_DAEMON_BIN_MD5 = './tcp_daemon.md5sum'

def compile_daemon():
    COMPILER_ARGS= [C_COMPILER, PATH_TO_DAEMON_SRC, '-o', PATH_TO_DAEMON_BIN]
    result = subprocess.run(COMPILER_ARGS, capture_output=True)
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
        if result.stderr:
            print(result.returncode, result.stderr, file=sys.stderr)
            sys.exit(254)
        with open(PATH_TO_DAEMON_SRC_MD5, 'w') as file:
            file.write(SOURCE_MD5_CURRENT)

connections_big_list = []
def process_data(data):
    now = time.time()
    connections_list = []
    connections = data.strip().split('\t')
    for conn in connections:
        local, remote = conn.split(',')
        connections_list.append((local, remote))
    connections_big_list.append((now, connections_list))
    print(datetime.datetime.now(), len(connections_list), file=sys.stdout)
    sys.stdout.flush()

def main():
    pipe_path = "/tmp/tcp_connections.pipe"

    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)
    subprocess.run([PATH_TO_DAEMON_BIN])

    with open(pipe_path, 'r') as pipe_fd:
        try:
            while True:
                for line in pipe_fd:
                    if line: process_data(line)
                time.sleep(1)
        except KeyboardInterrupt:
            for i, s in enumerate(connections_big_list, 1):
                print(i)
                for c in s[1]: print(f"  {c}")

if __name__ == "__main__":
    main()
