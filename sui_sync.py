#!/usr/bin/env python3
"""
Эмуляция отправки хеша состояния роя в Sui testnet.
Реальная интеграция будет после деплоя контракта.
"""
import json
import hashlib
import time
import os
import glob

STATE_FILE = "state.json"
LAST_HASH_FILE = "last_hash.txt"
SEND_INTERVAL = 30  # секунд

def get_swarm_state():
    """Собирает текущее состояние роя из файлов ключей."""
    state = {
        "timestamp": int(time.time() * 1000),
        "agents": {}
    }
    
    # Собираем информацию об агентах из папки keys
    keys_dir = "keys"
    if os.path.exists(keys_dir):
        for pub_file in glob.glob(f"{keys_dir}/*_pub.pem"):
            agent_name = os.path.basename(pub_file).replace("_pub.pem", "")
            with open(pub_file, "r") as f:
                pubkey = f.read().strip()
            state["agents"][agent_name] = {
                "pubkey": pubkey[:50] + "...",  # сокращённо для читаемости
                "status": "active"
            }
    
    # Если есть файл с логами агента — пытаемся найти лидера
    log_files = glob.glob("*.log")
    for log_file in log_files:
        try:
            with open(log_file, "r") as f:
                logs = f.readlines()[-100:]
                for line in logs:
                    if "AGENT" in line and "role: leader" in line:
                        # Извлекаем имя агента из строки вида "AGENT agent_a (role: leader)"
                        parts = line.split("AGENT")[1].split("(")[0].strip()
                        state["leader"] = parts
                        break
        except:
            pass
    
    return state

def get_state_hash():
    """Возвращает хеш состояния."""
    state = get_swarm_state()
    state_str = json.dumps(state, sort_keys=True)
    return hashlib.sha256(state_str.encode()).hexdigest(), state

def log_state_diff(old_hash, new_hash, state):
    """Логирует изменение состояния."""
    print("\n" + "="*60)
    print(f"[SUI] 🧠 Swarm State Snapshot")
    print(f"[SUI] Timestamp: {state['timestamp']}")
    print(f"[SUI] Agents: {len(state['agents'])}")
    for agent, info in state['agents'].items():
        role = "👑 LEADER" if state.get('leader') == agent else "  follower"
        print(f"[SUI]   - {agent}: {role} | pubkey: {info['pubkey'][:40]}...")
    print(f"[SUI] Old hash: {old_hash[:16]}...")
    print(f"[SUI] New hash: {new_hash[:16]}...")
    if old_hash != new_hash:
        print(f"[SUI] ✅ STATE CHANGED — would send to Sui blockchain")
    else:
        print(f"[SUI] ⏸️  No change, skipping")
    print("="*60 + "\n")

def main():
    print(f"[SUI] 🚀 Starting swarm state sync (check every {SEND_INTERVAL}s)")
    print(f"[SUI] 📁 Keys directory: {os.path.abspath('keys')}")
    
    last_hash = None
    
    while True:
        new_hash, state = get_state_hash()
        
        if last_hash is None:
            last_hash = new_hash
            log_state_diff(last_hash, new_hash, state)
        elif new_hash != last_hash:
            log_state_diff(last_hash, new_hash, state)
            last_hash = new_hash
        else:
            # Небольшой вывод для демонстрации, что скрипт жив
            print(f"[SUI] ⏳ Checking... state unchanged (hash: {new_hash[:16]}...)")
        
        time.sleep(SEND_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SUI] 👋 Shutting down")
