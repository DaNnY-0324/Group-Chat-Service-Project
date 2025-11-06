# Design Document - Chat Server Project

## Architecture Overview

This document outlines the design and architecture of the CSC4220/6220 Chat Server project implemented in Python.

### System Components

- **ChatServer**: Multi-threaded server handling client connections and IRC-style commands
- **ChatClient**: Simple text-based client interface for user interaction
- **Protocol**: Object-based communication protocol using JSON serialization
- **Utils**: Shared utilities including logging, networking, and validation functions

## Protocol Design

### Object-Based Protocol

The system uses an object-based protocol that replaces traditional IRC text commands with structured JSON messages. This approach provides:

- **Type Safety**: Structured data with validation
- **Extensibility**: Easy to add new message types
- **Debugging**: Clear message structure for troubleshooting

### Message Types

#### 1. Command Messages (Client → Server)
```python
@dataclass
class Command(Message):
    command_type: CommandType  # CONNECT, NICK, LIST, JOIN, LEAVE, QUIT, HELP
    parameters: List[str]      # Command parameters
```

#### 2. Event Messages (Server → Clients)
```python
@dataclass
class Event(Message):
    event_type: EventType      # USER_JOINED, USER_LEFT, MESSAGE_BROADCAST
    data: Dict[str, Any]       # Event-specific data
```

#### 3. Response Messages (Server → Client)
```python
@dataclass
class Response(Message):
    response_type: ResponseType # SUCCESS, ERROR, CHANNEL_LIST, USER_LIST
    success: bool              # Operation success status
    data: Dict[str, Any]       # Response data
    error_code: Optional[ErrorCode]  # Error code if applicable
```

### Serialization Format

All messages are serialized to JSON for network transmission:
```json
{
    "message_type": "command",
    "timestamp": 1699234567.123,
    "command_type": "join",
    "parameters": ["#general"]
}
```

## Server Architecture

### Stage 1: Single-Channel, Single-Threaded
- Basic socket server accepting one client at a time
- Single default channel for all communication
- Sequential command processing

### Stage 2: Multi-Channel, Single-Threaded
- Support for multiple named channels
- Channel creation and management
- User-to-channel mapping

### Stage 3: Multi-Channel, Multi-Threaded
- Thread pool with maximum 4 concurrent threads
- Thread-safe data structures using `threading.Lock`
- Concurrent client handling

### Data Structures

```python
# Server state management
clients: Dict[socket.socket, ClientInfo]     # Connected clients
channels: Dict[str, Set[socket.socket]]      # Channel membership
```

```python
# Client information
@dataclass
class ClientInfo:
    socket: socket.socket
    nickname: str
    channels: Set[str]
    last_activity: float
```

## Threading Model (Stage 3)

### Thread Pool Management
- **ThreadPool** class manages worker threads
- Maximum 4 concurrent threads to prevent overload
- Task queue for client handling requests
- Graceful shutdown with thread cleanup

### Synchronization
- **threading.Lock** for shared data structures
- Atomic operations for channel membership
- Thread-safe message broadcasting

### Thread Safety Considerations
- All shared data structures protected by locks
- Client disconnection cleanup synchronized
- Channel operations atomic

## Error Handling Strategy

### Network Errors
- Socket connection failures
- Client disconnection detection
- Graceful handling of broken connections

### Protocol Errors
- Invalid command format
- Missing parameters
- Unknown command types

### Application Errors
- Duplicate nicknames
- Channel access violations
- Resource limits (thread pool full)

### Error Response Format
```python
Response(
    response_type=ResponseType.ERROR,
    success=False,
    error_code=ErrorCode.NICKNAME_IN_USE,
    message="Nickname 'danny' is already in use"
)
```

## Client Architecture

### User Interface
- Command-line interface with colored output (extra credit)
- Real-time message display
- Input validation and help system

### Connection Management
- Automatic reconnection handling
- Connection state tracking
- Graceful disconnection

### Message Handling
- Separate thread for receiving messages
- Command parsing and validation
- Response processing and display

## Testing Strategy

### Unit Tests
- Protocol message serialization/deserialization
- Command parsing and validation
- Utility function testing

### Integration Tests
- Server startup and shutdown
- Client connection handling
- Channel management operations
- Multi-threading functionality

### Test Coverage Areas
1. **Protocol Testing**: Message format validation
2. **Server Testing**: Connection handling, command processing
3. **Threading Testing**: Concurrent operations, thread safety
4. **Error Testing**: Invalid inputs, network failures

## Extra Credit Features

### 1. Colored Terminal Output (+5 points)
- **colorama** library for cross-platform color support
- Color-coded message types (errors, success, info)
- Enhanced user experience

### 2. Graceful Ctrl-C Shutdown (+5 points)
- Signal handlers for SIGINT/SIGTERM
- Proper resource cleanup
- Client notification before shutdown

### 3. Enhanced Logging (+5 points)
- Structured logging with timestamps
- Different log levels (ERROR, INFO, DEBUG)
- Thread-safe logging operations

## Security Considerations

### Input Validation
- Nickname format validation
- Channel name validation
- Command parameter sanitization

### Resource Management
- Connection limits
- Message size limits
- Thread pool limits

### Error Information
- Limited error details to prevent information leakage
- Sanitized error messages

## Performance Considerations

### Scalability
- Thread pool prevents resource exhaustion
- Efficient data structures for channel management
- Minimal memory footprint per client

### Network Efficiency
- JSON message format balance between readability and size
- Connection reuse
- Efficient message broadcasting

## Future Enhancements

### Potential Improvements
- Persistent channel history
- User authentication
- Private messaging
- File transfer capabilities
- Web-based client interface

### Scalability Improvements
- Database integration for user/channel persistence
- Load balancing for multiple server instances
- Redis for distributed channel management
