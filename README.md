# CSC4220/6220: Computer Networks - Chat Server Project

## Team Members

- **Danny Nguyen** - Lead Developer (Server & Client Implementation)
- **David Salas** - Protocol & Utils Developer
- **Romeo Henderson** - Testing & Documentation

## Project Overview

Multi-client chat server implementation inspired by IRC principles, built with Python. Features a complete IRC-style command system with multi-threading support and enhanced user experience.

## ✅ Implementation Status

- **COMPLETED**: Core server and client functionality (Danny Nguyen)
- **IN PROGRESS**: Protocol classes and utilities (David & Romeo)

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## Demo Video Link

[TODO: Add YouTube link here]

## File/Folder Manifest

```
CSC4220_ChatServer_Team/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── src/
│   ├── __init__.py          # Package initialization
│   ├── chat_server.py       # ✅ Main server implementation (COMPLETE)
│   ├── chat_client.py       # ✅ Client implementation (COMPLETE)
│   ├── client_main.py       # ✅ Client entry point (COMPLETE)
│   ├── protocol.py          # 🔄 Object-based protocol (TODO)
│   ├── utils.py             # 🔄 Utility functions (TODO)
│   └── server_main.py       # 🔄 Server entry point (TODO)
├── tests/
│   ├── test_protocol.py     # 🔄 Protocol unit tests (TODO)
│   └── test_server.py       # 🔄 Server integration tests (TODO)
└── docs/
    ├── DESIGN.md            # Architecture documentation
    └── API.md               # Protocol API documentation
```

### ✅ Completed Files (Danny Nguyen)

- **`chat_server.py`** - Full multi-threaded server with all 3 stages
- **`chat_client.py`** - Complete IRC client with all commands
- **`client_main.py`** - Professional client interface with colors

## 🎯 Features Implemented

### ✅ Server Features (chat_server.py)

- **Stage 1**: Single-channel, single-threaded server
- **Stage 2**: Multi-channel support with dynamic channel creation
- **Stage 3**: Multi-threading support (max 4 concurrent threads)
- **Extra Credit**:
  - Colored terminal output (+5 points)
  - Graceful Ctrl-C shutdown (+5 points)
  - Enhanced logging system (+5 points)
- 3-minute inactivity auto-shutdown
- Thread-safe operations with proper locking
- JSON-based message protocol

### ✅ Client Features (chat_client.py)

- Full IRC command support:
  - `/connect <server> [port]` - Connect to server
  - `/nick <nickname>` - Set unique nickname
  - `/join <channel>` - Join/create channels
  - `/leave [channel]` - Leave channels
  - `/list` - List channels and user counts
  - `/quit` - Graceful disconnect
  - `/help` - Show help information
- Multi-threaded message receiving
- Colored terminal output
- Robust error handling and connection management

### ✅ Client Interface (client_main.py)

- Professional welcome screen with team information
- Colored command-line interface
- Signal handling for graceful Ctrl-C shutdown
- Comprehensive help system
- Error handling with troubleshooting tips
