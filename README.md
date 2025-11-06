# CSC4220/6220: Computer Networks - Chat Server Project

## Team Members
- Danny Nguyen
- David Salas  
- Romeo Henderson

## Project Overview
Multi-client chat server implementation inspired by IRC principles, built with Python.

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
│   ├── chat_server.py       # Main server implementation
│   ├── chat_client.py       # Client implementation
│   ├── protocol.py          # Object-based protocol
│   ├── utils.py             # Utility functions
│   ├── server_main.py       # Server entry point
│   └── client_main.py       # Client entry point
├── tests/
│   ├── test_protocol.py     # Protocol unit tests
│   └── test_server.py       # Server integration tests
└── docs/
    ├── DESIGN.md            # Architecture documentation
    └── API.md               # Protocol API documentation
```

## Building and Running

### Running the Server
```bash
python src/server_main.py -p <port> -d <debug_level>
```

### Running the Client
```bash
python src/client_main.py
```

### Running Tests
```bash
python -m pytest tests/
```

## Testing Documentation
[TODO: Document testing procedures and results]

## Development Process Reflection
[TODO: Add observations and team member role descriptions]
