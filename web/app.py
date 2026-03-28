from flask import Flask, render_template, jsonify
import json
import os
import subprocess

app = Flask(__name__)

def get_swarm_state():
    state = {"agents": []}
    for agent in ["agent_a", "agent_b", "agent_c"]:
        log_file = f"/tmp/{agent}.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()[-10:]
                state["agents"].append({"name": agent, "logs": lines})
    return state

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def api_state():
    return jsonify(get_swarm_state())

@app.route('/api/e_stop')
def e_stop():
    return jsonify({"status": "E-Stop sent"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
