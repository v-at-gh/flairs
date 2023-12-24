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

    processes_with_connections = []
    for process in processes:
        processes_with_connections.append(process.get_connections_of_process())
    
    try:
        process_info = processes_with_connections
    except json.JSONDecodeError:
        process_info = []

    return process_info

@app.route("/")
def index():
    process_info = get_data()

    return render_template('index.html', process_list=process_info)


if __name__ == "__main__":
    app.run(debug=True)