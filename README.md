# P2P Swarm Agent

Decentralized swarm coordination with Ed25519 cryptographic signatures and Sui blockchain sync.

A peer-to-peer agent system for robot swarms, drones, and AI agents. Every message is signed and verified. State changes are hashed and prepared for settlement on the Sui blockchain.

---

## Features

- **3+ agents** with automatic P2P discovery (libp2p + FoxMQ)
- **Ed25519 signatures** — every message is signed and verified
- **Auto role switching** — leader election every 30 seconds
- **Heartbeat** every 5 seconds with stale detection (10 sec timeout)
- **State hashing** — swarm state is hashed for on-chain anchoring
- **Sui blockchain integration** — prepared for settlement via smart contracts
- **Docker ready**

---

## Demo Video

https://youtu.be/XfRwFAQPLCs

---

## Quick Start

### Prerequisites
- Python 3.10+
- FoxMQ broker (see [setup guide](https://github.com/tashigit/foxmq))

### Clone & Install
```bash
git clone https://github.com/rudimentall1/p2p-swarm-agent.git
cd p2p-swarm-agent
pip install -r requirements.txt
Run 3 Agents (3 separate terminals)
# Terminal 1 – Agent A
python node.py --host 127.0.0.1 --port 1883 --username agent_a --password agent_a --agent-id agent_a

# Terminal 2 – Agent B
python node.py --host 127.0.0.1 --port 1883 --username agent_b --password agent_b --agent-id agent_b

# Terminal 3 – Agent C
python node.py --host 127.0.0.1 --port 1883 --username agent_c --password agent_c --agent-id agent_c
Monitor Swarm State + Sui Sync
# Terminal 4
python sui_sync.py
Architecture
Component	Description
node.py	Agent core with P2P, Ed25519 signatures, heartbeat, leader election
sui_sync.py	State monitor that hashes swarm state and simulates on-chain anchoring
keys/	Ed25519 keypairs for each agent
Sui Blockchain Integration
Every 30 seconds:

Swarm state is collected and hashed

Hash is compared with the previous one

If changed, it's logged as ready for on-chain settlement

Future version will call a Sui smart contract to store the hash
Tech Stack
P2P Layer: libp2p (via FoxMQ broker)

Cryptography: Ed25519

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
Rinat
GitHub: rudimentall1
DoraHacks: Rinat
License
MIT

Built for the Vertex Swarm Challenge 2026 with support from Tashi Network.
