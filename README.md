# CSC4220/6220: Computer Networks - Chat Server Project

## Team Members

- **Danny Nguyen** - Lead Developer (Server & Client Implementation & Documentation)
- **David Salas** - Protocol & Utils Developer
- **Romeo Henderson** - Testing

## Project Overview

Multi-client chat server implementation inspired by IRC principles, built with Python. Features a complete IRC-style command system with multi-threading support and enhanced user experience.

## ✅ Implementation Status

- **COMPLETED**: All core functionality implemented and tested
- **COMPLETED**: Protocol classes and utilities (David & Romeo)
- **COMPLETED**: Unit and integration tests
- **READY**: Project ready for submission and demo

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
│   ├── protocol.py          # ✅ Object-based protocol (COMPLETE)
│   ├── utils.py             # ✅ Utility functions (COMPLETE)
│   └── server_main.py       # ✅ Server entry point (COMPLETE)
├── tests/
│   ├── test_protocol.py     # ✅ Protocol unit tests (COMPLETE)
│   └── test_server.py       # ✅ Server integration tests (COMPLETE)
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

### ✅ Additional Components (David & Romeo)

- **`protocol.py`** - Object-based protocol with JSON serialization
- **`utils.py`** - Utility classes for logging, threading, and networking
- **`server_main.py`** - Professional server entry point with argument parsing
- **`test_protocol.py`** - Comprehensive unit tests for protocol module
- **`test_server.py`** - Integration tests for server functionality

## 🚀 Building and Running

### Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or later)
- **Operating System**: macOS, Linux, or Windows
- **Terminal/Command Prompt** access

### 🎯 **Complete Terminal Setup Guide**

#### **Step 1: Navigate to Project Directory**

```bash
cd /Users/dnguyen0324/CascadeProjects/CSC4220_ChatServer_Team
```

#### **Step 2: Start the Server**

Open your **first terminal window** and run:

```bash
python3 src/server_main.py -p 8080 -d 1
```

**Arguments:**

- `-p 8080` = Port number (you can use any port 1024-65535)
- `-d 1` = Debug level (1 shows all events, 0 shows errors only)

You should see a colorful startup banner:

```
============================================================
                    CSC4220 CHAT SERVER                   
              Multi-threaded IRC-style Server             
============================================================

🚀 Server Configuration:
   • Port: 8080
   • Debug Level: 1 (All Events)
   • Local IP: 192.168.0.100
   • Max Threads: 4

🔥 Starting server...
📡 Listening on 192.168.0.100:8080
Press Ctrl+C to shutdown gracefully
```

#### **Step 3: Start Client(s)**

Open a **second terminal window** and run:

```bash
python3 src/client_main.py
```

You'll see the client interface:

```
============================================================
CSC4220 Chat Client
Team: Danny Nguyen, David Salas, Romeo Henderson
============================================================

Available Commands:
  /connect <server> [port]  - Connect to chat server
  /nick <nickname>          - Set your nickname
  /list                     - List available channels
  /join <channel>           - Join a channel
  /leave [channel]          - Leave current or specified channel
  /quit                     - Quit the chat client
  /help                     - Show this help message
============================================================
```

#### **Step 4: Connect and Chat**

In the client terminal, type these commands:

```bash
# Connect to the server
/connect localhost 8080

# Set your nickname
/nick alice

# Join a channel (creates it if it doesn't exist)
/join #general

# Send messages (just type without /)
Hello everyone! 👋

# List all channels
/list

# Get help
/help

# Quit when done
/quit
```

### 🎯 **Multi-Client Demo**

To test multiple clients simultaneously:

1. **Keep the server running** in terminal 1
2. **Open 3 more terminal windows** (terminals 2, 3, 4)
3. **In each terminal**, run:
   ```bash
   python3 src/client_main.py
   ```
4. **Connect each client** with different nicknames:
   ```bash
   # Terminal 2 (Alice)
   /connect localhost 8080
   /nick alice
   /join #general

   # Terminal 3 (Bob)  
   /connect localhost 8080
   /nick bob
   /join #general

   # Terminal 4 (Charlie)
   /connect localhost 8080
   /nick charlie
   /join #general
   ```
5. **Start chatting!** Messages sent by one client will appear in all others in the same channel.

### Quick Start (Alternative)

1. **Clone/Download the project:**

   ```bash
   cd CSC4220_ChatServer_Team
   ```
2. **Start the Server:**

   ```bash
   python src/server_main.py -p 8080
   ```

   Or with debug output:

   ```bash
   python src/server_main.py -p 8080 -d 1
   ```
3. **Start the Client (in a new terminal):**

   ```bash
   python src/client_main.py
   ```
4. **Connect to Server:**

   ```
   /connect localhost 8080
   /nick your_nickname
   /join #general
   Hello everyone!
   ```

### Server Usage

```bash
python src/server_main.py -p <port> [-d <debug_level>]
```

**Arguments:**

- `-p, --port`: Port number (1024-65535, required)
- `-d, --debug`: Debug level (0=errors only, 1=all events, default: 0)

**Examples:**

```bash
# Basic server on port 8080
python src/server_main.py -p 8080

# Server with full debug logging
python src/server_main.py -p 9000 -d 1

# Server on different port
python src/server_main.py -p 12345
```

### Client Usage

```bash
python src/client_main.py
```

**Available Commands:**

- `/connect <server> [port]` - Connect to chat server
- `/nick <nickname>` - Set your nickname
- `/join <channel>` - Join a channel (creates if doesn't exist)
- `/leave [channel]` - Leave current or specified channel
- `/list` - List all channels and user counts
- `/quit` - Disconnect and exit
- `/help` - Show help information
- `<message>` - Send message to current channel

**Example Session:**

```
Welcome to CSC4220 Chat Client!
> /connect localhost 8080
Connected to localhost:8080
> /nick alice
Nickname set to: alice
> /join #general
Joined channel: #general
> Hello everyone!
[#general] alice: Hello everyone!
> /list
Channels:
  #general (2 users)
  #random (1 user)
> /quit
Goodbye!
```

### 🧪 **Quick Test Commands**

You can also run the automated demo:

```bash
python3 demo_script.py
```

Or run the unit tests:

```bash
python3 tests/test_protocol.py
```

## 🧪 Testing

### Run Unit Tests

```bash
# Test protocol module
python3 -m pytest tests/test_protocol.py -v

# Test server functionality  
python3 -m pytest tests/test_server.py -v

# Run all tests
python3 -m pytest tests/ -v

# Alternative (without pytest)
python3 tests/test_protocol.py
```

### Manual Testing

1. **Start server:**

   ```bash
   python src/server_main.py -p 8080 -d 1
   ```
2. **Open multiple terminals and start clients:**

   ```bash
   # Terminal 2
   python src/client_main.py

   # Terminal 3
   python src/client_main.py

   # Terminal 4
   python src/client_main.py
   ```
3. **Test scenarios:**

   - Multiple users joining same channel
   - Message broadcasting
   - Channel creation and listing
   - Graceful disconnection
   - Server shutdown with Ctrl-C

## 🐛 Troubleshooting

### Common Terminal Issues

**If you get "command not found: python3":**

```bash
# Try with python instead
python src/server_main.py -p 8080 -d 1
python src/client_main.py
```

**If port 8080 is busy:**

```bash
# Use a different port
python3 src/server_main.py -p 9000 -d 1
# Then connect with: /connect localhost 9000
```

**If you get permission errors:**

```bash
# Use ports above 1024 (no sudo needed)
python3 src/server_main.py -p 8080 -d 1
```

### Common Issues

**Port already in use:**

```
Error: Port 8080 is already in use!
Solution: Use a different port or stop the existing server
```

**Connection refused:**

```
Error: Connection refused
Solution: Make sure the server is running and the port is correct
```

**Permission denied (ports < 1024):**

```
Error: Permission denied
Solution: Use ports 1024 or higher, or run with sudo (not recommended)
```

**Python version issues:**

```
Error: SyntaxError or import errors
Solution: Ensure Python 3.8+ is installed
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python src/server_main.py -p 8080 -d 1
```

This shows:

- Client connections/disconnections
- Channel operations
- Message routing
- Error details
- Thread activity

### 🎬 **Expected Terminal Experience**

**Server Terminal** will show:

- Colorful startup banner with configuration
- Client connection logs (e.g., "New connection from 127.0.0.1:12345")
- Message routing debug info
- Channel operations (joins, leaves, creates)
- Real-time activity logging

**Client Terminal** will show:

- Professional chat interface with team info
- Real-time message reception from other users
- Colored command responses and confirmations
- Channel notifications (user joins/leaves)
- Error messages with helpful suggestions

**Features You'll Experience:**

- ✅ Multi-client chat rooms with real-time messaging
- ✅ Dynamic channel creation and management
- ✅ Colored terminal output for better readability
- ✅ Professional error handling with clear messages
- ✅ Graceful Ctrl-C shutdown for both server and client
- ✅ Thread-safe concurrent operations

## 📊 Performance Notes

- **Max Concurrent Clients**: 4 (configurable in code)
- **Idle Timeout**: 3 minutes of inactivity
- **Message Length**: 512 characters max
- **Nickname Length**: 16 characters max
- **Channel Name Length**: 32 characters max

## 🔧 Development Process

### Architecture Decisions

1. **Multi-threading**: Used thread pool with max 4 workers to handle concurrent clients
2. **JSON Protocol**: Structured message format for reliability
3. **Object-oriented Design**: Clean separation of concerns
4. **Error Handling**: Comprehensive error handling and user feedback
5. **Testing**: Unit tests for protocol, integration tests for server

### Team Contributions

- **Danny Nguyen**: Core server/client implementation, multi-threading, IRC protocol
- **David Salas**: Protocol classes, utility functions, JSON serialization
- **Romeo Henderson**: Testing framework, documentation, validation functions

### Testing Methodology

1. **Unit Tests**: Protocol validation, message serialization, utility functions
2. **Integration Tests**: Multi-client scenarios, message broadcasting, error handling
3. **Manual Testing**: Real-world usage scenarios, stress testing, edge cases
4. **Performance Testing**: Concurrent client connections, message throughput

### Observations

- **Thread Safety**: Careful use of locks prevents race conditions
- **Scalability**: Thread pool design allows controlled resource usage
- **User Experience**: Colored output and clear error messages improve usability
- **Robustness**: Graceful handling of network errors and client disconnections
