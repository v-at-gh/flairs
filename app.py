#!/usr/bin/env python3

from flask import Flask
from flask import render_template
import json, subprocess

app = Flask(__name__)

from Netstat import Netstat
from Process import Process

def get_data():

    connections = Netstat.get_connections()
    pids = Netstat.get_connection_pids(connections)
    processes = [Process(pid) for pid in pids]

    try:
        processes_with_connections = []
        for process in processes:
            processes_with_connections.append(process.get_connections_of_process())
    except json.JSONDecodeError:
        processes_with_connections = []

    return processes_with_connections

@app.route("/")
def index():
    processes_with_connections = get_data()

    return render_template('index.html', process_list=processes_with_connections)


if __name__ == "__main__":
    app.run(debug=True)