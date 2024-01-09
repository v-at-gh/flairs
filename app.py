#!/usr/bin/env python3

from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

from get_data import get_data

@app.route("/")
def index():
    processes_with_connections = get_data()
    return render_template(
        'index.html',
        process_list=processes_with_connections,
        amount_of_processes=len(processes_with_connections),
        datetime=str(datetime.now()).split('.')[:-1][0]
    )

@app.route("/tcp")
def list_tcp_connections():
    processes_with_connections = get_data()
    return render_template(
        'index.html',
        process_list=processes_with_connections,
        amount_of_processes=len(processes_with_connections),
        datetime=str(datetime.now()).split('.')[:-1][0]
    )

@app.route("/udp")
def list_udp_connections():
    processes_with_connections = get_data()
    return render_template(
        'index.html',
        process_list=processes_with_connections,
        amount_of_processes=len(processes_with_connections),
        datetime=str(datetime.now()).split('.')[:-1][0]
    )

if __name__ == "__main__":
    app.run(debug=True)
