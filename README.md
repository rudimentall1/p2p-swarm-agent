# P2P Swarm Agent 🔥

[![Vertex Swarm Challenge](https://img.shields.io/badge/Vertex%20Swarm%20Challenge-2026-blue)](https://dorahacks.io/hackathon/global-vertex-swarm-challenge)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Decentralized swarm coordination with Ed25519 cryptographic signatures and Sui blockchain sync.**

A peer-to-peer agent system for robot swarms, drones, and AI agents. Every message is signed and verified, ensuring trustless coordination. State changes are hashed and prepared for settlement on the Sui blockchain.

## ✨ Key Features

- 🤝 **3+ agents** with automatic P2P discovery (libp2p + FoxMQ)
- 🔒 **Ed25519 signatures** — every message is signed and verified, preventing spoofing
- 🔄 **Auto role switching** — leader election cycles every 30 seconds
- 💓 **Heartbeat** every 5 seconds with stale detection (10 sec timeout)
- 🧠 **State hashing** — swarm state is hashed for on-chain anchoring
- 🌊 **Sui blockchain integration** — prepared for settlement via smart contracts
- 🐳 **Docker ready** — easy deployment with Dockerfiles

## 🎥 Demo Video

[Watch the demo on YouTube](https://youtu.be/XfRwFAQPLCs) — see 3 agents forming a swarm, automatically switching roles, and syncing state.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- FoxMQ broker (see [setup guide](https://github.com/tashigit/foxmq))

### Clone & Install
```bash
git clone https://github.com/rudimentall1/p2p-swarm-agent.git
cd p2p-swarm-agent
pip install -r requirements.txt
# Terminal 1 – Agent A
python node.py --host 127.0.0.1 --port 1883 --username agent_a --password agent_a --agent-id agent_a

# Terminal 2 – Agent B
python node.py --host 127.0.0.1 --port 1883 --username agent_b --password agent_b --agent-id agent_b

# Terminal 3 – Agent C
python node.py --host 127.0.0.1 --port 1883 --username agent_c --password agent_c --agent-id agent_c
# Terminal 4 – Watch state hashes change
python sui_sync.py
Architecture
Component	Description
node.py	Agent core with P2P, Ed25519 signatures, heartbeat, leader election
sui_sync.py	State monitor that hashes swarm state and simulates on-chain anchoring
keys/	Folder where Ed25519 keypairs for each agent are stored
Sui Blockchain Integration
The project is designed to settle state proofs on the Sui network. Every 30 seconds:

The swarm state is collected and hashed

The hash is compared with the previous one

If changed, it's logged as ready for on-chain settlement

Future version will call a Sui smart contract to store the hash
Tech Stack
P2P Layer: libp2p (via FoxMQ broker)

Cryptography: Ed25519 (signing all messages)

Language: Python 3.10+

Blockchain: Sui (state anchoring)

Container: Docker
Roadmap
P2P communication with libp2p

Ed25519 signatures

Auto leader election

Stale detection

State hashing

Sui testnet simulation

Real Sui smart contract deployment

Web dashboard with real-time swarm map

Docker Compose for one-command launch
 Author
Rinat (@rudimentall1)

GitHub: rudimentall1

DoraHacks: Rinat
License
MIT
Credits
Built for the Vertex Swarm Challenge 2026 with support from Tashi Network.
