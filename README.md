# P2P Swarm Agent

A decentralized multi-agent coordination prototype combining P2P communication, cryptographic message verification, swarm state management, and Sui state anchoring.

## Problem

Independent agents need to coordinate roles and state while remaining resilient to peer failure and maintaining verifiable state transitions.

## Solution

Agents discover peers, exchange signed messages, elect roles, monitor liveness, and hash swarm state for optional on-chain anchoring.

## Architecture

```text
Agents
  |
  +--> P2P discovery / FoxMQ
  |
  +--> Ed25519 message verification
  |
  +--> Heartbeat + stale detection
  |
  +--> Leader election
  |
  +--> State hashing
  |
  +--> Sui state anchoring
```

## Features

- 3+ agent coordination
- Ed25519 signatures
- Automatic peer discovery
- Leader election and role switching
- Heartbeat and stale-peer detection
- State hashing
- Sui testnet integration for state anchoring
- Telegram control interface
- Web dashboard
- Docker support

## Stack

- Python 3.10+
- libp2p / FoxMQ
- Ed25519
- Sui
- Flask
- python-telegram-bot
- Docker

## Testing

```bash
pytest tests/
```

## Status

Prototype / challenge project focused on decentralized swarm coordination and verifiable state synchronization.
