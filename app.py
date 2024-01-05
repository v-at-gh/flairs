#!/usr/bin/env python3

from flask import Flask
from flask import render_template

app = Flask(__name__)

from get_data import get_data

@app.route("/")
def index():
    processes_with_connections = get_data()
    return render_template('index.html', process_list=processes_with_connections)

if __name__ == "__main__":
    app.run(debug=True)
