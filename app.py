#!/usr/bin/env python3

from flask import Flask
from flask import render_template
import json, subprocess

app = Flask(__name__)

def get_data():
    netstat_parser_program = '/Users/v/data/src/github.com/vitpodsokhin/apples/test.py'

    # Run the external program and capture its output
    result = subprocess.run(['python3', netstat_parser_program], stdout=subprocess.PIPE, text=True)
    
    try:
        process_info = json.loads(json.dumps(result.stdout))
    except json.JSONDecodeError:
        process_info = []

    return process_info

@app.route("/")
def index():
    process_info = get_data()

    return render_template('index.html', process_list=json.dumps(process_info, indent=2))


if __name__ == "__main__":
    app.run(debug=True)