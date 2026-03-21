import argparse
import json
import time
import threading
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import paho.mqtt.client as mqtt

TOPIC_SWARM = "swarm/state"
TOPIC_HELLO = "swarm/hello"

peers = {}
my_role = "follower"
my_id = None
running = True
lock = threading.Lock()

# Генерация или загрузка ключей
def load_or_generate_keys(agent_id):
    key_dir = "keys"
    os.makedirs(key_dir, exist_ok=True)
    priv_path = f"{key_dir}/{agent_id}_priv.pem"
    pub_path = f"{key_dir}/{agent_id}_pub.pem"

    if os.path.exists(priv_path) and os.path.exists(pub_path):
        with open(priv_path, "rb") as f:
            private_key = ed25519.Ed25519PrivateKey.from_pem(f.read())
        with open(pub_path, "rb") as f:
            public_key = ed25519.Ed25519PublicKey.from_pem(f.read())
        print(f"[KEYS] Loaded existing keys for {agent_id}")
    else:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        with open(priv_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(pub_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print(f"[KEYS] Generated new keys for {agent_id}")

    return private_key, public_key

def sign_message(private_key, message):
    signature = private_key.sign(message.encode())
    return base64.b64encode(signature).decode()

def verify_signature(public_key, message, signature_b64):
    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message.encode())
        return True
    except:
        return False

def now_ms():
    return int(time.time() * 1000)

def publish_json(client, topic, data):
    payload = json.dumps(data)
    client.publish(topic, payload, qos=1)
    print(f"[SEND] {topic}: {payload}")

def print_peer_status():
    with lock:
        print("\n" + "="*50)
        print(f"AGENT {my_id} (role: {my_role})")
        print("-"*50)
        for pid, info in peers.items():
            status = info.get("status", "unknown")
            role = info.get("role", "unknown")
            last_seen = info.get("last_seen", 0)
            age = (now_ms() - last_seen) / 1000 if last_seen else 0
            print(f"  {pid}: role={role}, status={status}, age={age:.1f}s")
        print("="*50 + "\n")

def heartbeat_loop(client, agent_id, private_key):
    global my_role
    while running:
        time.sleep(5)
        with lock:
            current_role = my_role
        msg = {
            "type": "HEARTBEAT",
            "agent_id": agent_id,
            "role": current_role,
            "timestamp": now_ms()
        }
        msg_str = json.dumps(msg)
        msg["signature"] = sign_message(private_key, msg_str)
        publish_json(client, TOPIC_SWARM, msg)

def stale_checker():
    while running:
        time.sleep(2)
        now = now_ms()
        changes = False
        with lock:
            for peer_id, info in list(peers.items()):
                if now - info["last_seen"] > 10000:
                    if info["status"] != "stale":
                        info["status"] = "stale"
                        print(f"[STALE] {peer_id}")
                        changes = True
        if changes:
            print_peer_status()

def auto_role_switcher(client, agent_id, private_key):
    global my_role
    while running:
        time.sleep(30)
        with lock:
            my_role = "leader" if my_role == "follower" else "follower"
            new_role = my_role
        msg = {
            "type": "ROLE_CHANGE",
            "agent_id": agent_id,
            "new_role": new_role,
            "timestamp": now_ms()
        }
        msg_str = json.dumps(msg)
        msg["signature"] = sign_message(private_key, msg_str)
        publish_json(client, TOPIC_SWARM, msg)
        print(f"[AUTO-ROLE] → {my_role}")
        print_peer_status()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[CONNECTED] {userdata['agent_id']}")
        client.subscribe(TOPIC_SWARM, qos=1)
        client.subscribe(TOPIC_HELLO, qos=1)

        hello_msg = {
            "type": "HELLO",
            "agent_id": userdata['agent_id'],
            "pubkey": userdata['pubkey'],
            "timestamp": now_ms()
        }
        publish_json(client, TOPIC_HELLO, hello_msg)

        global my_id
        my_id = userdata['agent_id']

        threading.Thread(target=heartbeat_loop, args=(client, my_id, userdata['privkey']), daemon=True).start()
        threading.Thread(target=stale_checker, daemon=True).start()
        threading.Thread(target=auto_role_switcher, args=(client, my_id, userdata['privkey']), daemon=True).start()
    else:
        print(f"[ERROR] Connection failed")

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()
    try:
        data = json.loads(payload)
        msg_type = data.get("type")
        peer_id = data.get("agent_id")
        timestamp = data.get("timestamp", 0)

        if not peer_id or peer_id == userdata['agent_id']:
            return

        # Проверка подписи
        if "signature" in data:
            msg_without_sig = {k: v for k, v in data.items() if k != "signature"}
            msg_str = json.dumps(msg_without_sig)
            if peer_id in userdata['pubkeys']:
                pubkey_pem = userdata['pubkeys'][peer_id]
                pubkey = ed25519.Ed25519PublicKey.from_pem(pubkey_pem.encode())
                if not verify_signature(pubkey, msg_str, data["signature"]):
                    print(f"[SECURITY] Invalid signature from {peer_id}")
                    return
            else:
                print(f"[SECURITY] No pubkey for {peer_id}, storing anyway")
                if "pubkey" in data:
                    userdata['pubkeys'][peer_id] = data["pubkey"]
        else:
            print(f"[WARN] No signature from {peer_id}")

        with lock:
            if peer_id not in peers:
                peers[peer_id] = {
                    "last_seen": timestamp,
                    "role": data.get("role", "follower"),
                    "status": "active"
                }
                print(f"[NEW PEER] {peer_id}")
            else:
                peers[peer_id]["last_seen"] = timestamp
                peers[peer_id]["status"] = "active"
                if data.get("role"):
                    peers[peer_id]["role"] = data.get("role")

        if msg_type == "HELLO":
            print(f"[HELLO] from {peer_id}")
        elif msg_type == "HEARTBEAT":
            print(f"[HEARTBEAT] {peer_id} role={data.get('role')}")
        elif msg_type == "ROLE_CHANGE":
            print(f"[ROLE_CHANGE] {peer_id} → {data.get('new_role')}")

    except Exception as e:
        print(f"[ERROR] {e}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print("[DISCONNECTED]")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=1883, type=int)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--agent-id", required=True)
    args = parser.parse_args()

    privkey, pubkey = load_or_generate_keys(args.agent_id)

    client = mqtt.Client(
        client_id=args.agent_id,
        protocol=mqtt.MQTTv5,
        userdata={
            "host": args.host,
            "port": args.port,
            "agent_id": args.agent_id,
            "privkey": privkey,
            "pubkey": pubkey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "pubkeys": {}
        }
    )

    client.username_pw_set(args.username, args.password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(args.host, args.port, keepalive=60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        global running
        running = False
        client.disconnect()

if __name__ == "__main__":
    main()
