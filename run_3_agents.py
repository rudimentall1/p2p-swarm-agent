#!/usr/bin/env python3
import subprocess
import time
import threading
import os

agents = [
    {"id": "agent_a", "port": 1883, "user": "agent_a", "pass": "agent_a"},
    {"id": "agent_b", "port": 1883, "user": "agent_b", "pass": "agent_b"},
    {"id": "agent_c", "port": 1883, "user": "agent_c", "pass": "agent_c"},
]

def run_agent(agent):
    cmd = [
        "python3", "node.py",
        "--host", "127.0.0.1",
        "--port", str(agent["port"]),
        "--username", agent["user"],
        "--password", agent["pass"],
        "--agent-id", agent["id"]
    ]
    with open(f"{agent['id']}.log", "w") as f:
        subprocess.Popen(cmd, stdout=f, stderr=f)
    print(f"[START] {agent['id']}")

# Очистка старых логов
os.system("rm -f *.log")

# Запуск агентов
for agent in agents:
    run_agent(agent)

print("\n✅ Все 3 агента запущены! Логи в *.log")
print("Следи за логами: tail -f agent_a.log")
