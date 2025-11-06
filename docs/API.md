# API Documentation - Chat Server Protocol

## IRC-Style Commands

This document describes the IRC-style commands supported by the chat server and their object-based protocol equivalents.

## Client Commands

### `/connect <server-name> [port#]`
**Purpose**: Connect to named server  
**Parameters**: 
- `server-name` (required): Server hostname or IP address
- `port#` (optional): Server port number (default: 8080)

**Examples**:
```
/connect localhost
/connect localhost 8080
/connect 192.168.1.100 9000
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.CONNECT,
    parameters=["localhost", "8080"]
)
```

**Server Response**:
```python
# Success
Response(
    response_type=ResponseType.SUCCESS,
    success=True,
    message="Connected to server"
)

# Error
Response(
    response_type=ResponseType.ERROR,
    success=False,
    error_code=ErrorCode.CONNECTION_ERROR,
    message="Unable to connect to server"
)
```

---

### `/nick <nickname>`
**Purpose**: Set unique nickname  
**Parameters**: 
- `nickname` (required): Desired nickname (max 32 characters, alphanumeric + underscore)

**Examples**:
```
/nick danny123
/nick alice_smith
/nick user42
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.NICK,
    parameters=["danny123"]
)
```

**Server Response**:
```python
# Success
Response(
    response_type=ResponseType.SUCCESS,
    success=True,
    message="Nickname set to 'danny123'"
)

# Error - Nickname in use
Response(
    response_type=ResponseType.ERROR,
    success=False,
    error_code=ErrorCode.NICKNAME_IN_USE,
    message="Nickname 'danny123' is already in use"
)
```

---

### `/list`
**Purpose**: List channels and number of users  
**Parameters**: None

**Example**:
```
/list
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.LIST,
    parameters=[]
)
```

**Server Response**:
```python
Response(
    response_type=ResponseType.CHANNEL_LIST,
    success=True,
    data={
        "channels": [
            {"name": "#general", "user_count": 5},
            {"name": "#random", "user_count": 2},
            {"name": "#dev", "user_count": 3}
        ]
    }
)
```

---

### `/join <channel>`
**Purpose**: Join a channel  
**Parameters**: 
- `channel` (required): Channel name (auto-prefixed with # if not present)

**Examples**:
```
/join #general
/join general
/join #random
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.JOIN,
    parameters=["#general"]
)
```

**Server Response**:
```python
# Success
Response(
    response_type=ResponseType.SUCCESS,
    success=True,
    message="Joined channel #general"
)

# Error - Already in channel
Response(
    response_type=ResponseType.ERROR,
    success=False,
    error_code=ErrorCode.ALREADY_IN_CHANNEL,
    message="You are already in channel #general"
)
```

**Server Event** (broadcast to channel members):
```python
Event(
    event_type=EventType.USER_JOINED,
    data={
        "channel": "#general",
        "nickname": "danny123",
        "user_count": 6
    }
)
```

---

### `/leave [<channel>]`
**Purpose**: Leave current or specified channel  
**Parameters**: 
- `channel` (optional): Channel name to leave (leaves current channel if not specified)

**Examples**:
```
/leave
/leave #general
/leave #random
```

**Protocol Object**:
```python
# Leave current channel
Command(
    command_type=CommandType.LEAVE,
    parameters=[]
)

# Leave specific channel
Command(
    command_type=CommandType.LEAVE,
    parameters=["#general"]
)
```

**Server Response**:
```python
# Success
Response(
    response_type=ResponseType.SUCCESS,
    success=True,
    message="Left channel #general"
)

# Error - Not in channel
Response(
    response_type=ResponseType.ERROR,
    success=False,
    error_code=ErrorCode.NOT_IN_CHANNEL,
    message="You are not in channel #general"
)
```

**Server Event** (broadcast to remaining channel members):
```python
Event(
    event_type=EventType.USER_LEFT,
    data={
        "channel": "#general",
        "nickname": "danny123",
        "user_count": 4
    }
)
```

---

### `/quit`
**Purpose**: Leave chat and disconnect from server  
**Parameters**: None

**Example**:
```
/quit
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.QUIT,
    parameters=[]
)
```

**Server Response**:
```python
Response(
    response_type=ResponseType.SUCCESS,
    success=True,
    message="Goodbye!"
)
```

---

### `/help`
**Purpose**: Print help message  
**Parameters**: None

**Example**:
```
/help
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.HELP,
    parameters=[]
)
```

**Server Response**:
```python
Response(
    response_type=ResponseType.HELP_TEXT,
    success=True,
    data={
        "commands": [
            {
                "command": "/connect <server> [port]",
                "description": "Connect to chat server"
            },
            {
                "command": "/nick <nickname>",
                "description": "Set your nickname"
            },
            {
                "command": "/list",
                "description": "List available channels"
            },
            {
                "command": "/join <channel>",
                "description": "Join a channel"
            },
            {
                "command": "/leave [channel]",
                "description": "Leave current or specified channel"
            },
            {
                "command": "/quit",
                "description": "Quit the chat client"
            },
            {
                "command": "/help",
                "description": "Show this help message"
            }
        ]
    }
)
```

---

## Regular Messages

**Purpose**: Send chat message to current channel  
**Format**: Any text not starting with `/`

**Examples**:
```
Hello everyone!
How is everyone doing today?
Check out this link: https://example.com
```

**Protocol Object**:
```python
Command(
    command_type=CommandType.MESSAGE,
    parameters=["Hello everyone!"]
)
```

**Server Event** (broadcast to channel members):
```python
Event(
    event_type=EventType.MESSAGE_BROADCAST,
    data={
        "channel": "#general",
        "nickname": "danny123",
        "message": "Hello everyone!",
        "timestamp": 1699234567.123
    }
)
```

---

## Object-Based Protocol Details

### Message Base Structure

All protocol messages inherit from the base `Message` class:

```python
@dataclass
class Message:
    message_type: MessageType  # COMMAND, EVENT, RESPONSE
    timestamp: float          # Unix timestamp
```

### JSON Serialization

Messages are serialized to JSON for network transmission:

```json
{
    "message_type": "command",
    "timestamp": 1699234567.123,
    "command_type": "join",
    "parameters": ["#general"]
}
```

### Error Codes

The protocol defines standard error codes:

```python
class ErrorCode(enum.Enum):
    INVALID_COMMAND = "invalid_command"
    NICKNAME_IN_USE = "nickname_in_use"
    CHANNEL_NOT_FOUND = "channel_not_found"
    NOT_IN_CHANNEL = "not_in_channel"
    ALREADY_IN_CHANNEL = "already_in_channel"
    SERVER_FULL = "server_full"
    CONNECTION_ERROR = "connection_error"
```

### Protocol Constants

```python
MAX_MESSAGE_LENGTH = 1024      # Maximum message size
MAX_NICKNAME_LENGTH = 32       # Maximum nickname length
MAX_CHANNEL_LENGTH = 32        # Maximum channel name length
PROTOCOL_VERSION = "1.0"       # Protocol version
```

---

## Server Events

### User Joined Channel
```python
Event(
    event_type=EventType.USER_JOINED,
    data={
        "channel": "#general",
        "nickname": "alice",
        "user_count": 5
    }
)
```

### User Left Channel
```python
Event(
    event_type=EventType.USER_LEFT,
    data={
        "channel": "#general",
        "nickname": "alice",
        "user_count": 4
    }
)
```

### Message Broadcast
```python
Event(
    event_type=EventType.MESSAGE_BROADCAST,
    data={
        "channel": "#general",
        "nickname": "alice",
        "message": "Hello everyone!",
        "timestamp": 1699234567.123
    }
)
```

### Channel Created
```python
Event(
    event_type=EventType.CHANNEL_CREATED,
    data={
        "channel": "#newchannel",
        "creator": "alice"
    }
)
```

### Channel Deleted
```python
Event(
    event_type=EventType.CHANNEL_DELETED,
    data={
        "channel": "#oldchannel"
    }
)
```

---

## Usage Examples

### Complete Connection Flow

1. **Client connects to server**:
```python
Command(command_type=CommandType.CONNECT, parameters=["localhost", "8080"])
```

2. **Server responds**:
```python
Response(response_type=ResponseType.SUCCESS, success=True, message="Connected")
```

3. **Client sets nickname**:
```python
Command(command_type=CommandType.NICK, parameters=["danny"])
```

4. **Server responds**:
```python
Response(response_type=ResponseType.SUCCESS, success=True, message="Nickname set")
```

5. **Client joins channel**:
```python
Command(command_type=CommandType.JOIN, parameters=["#general"])
```

6. **Server responds and broadcasts**:
```python
Response(response_type=ResponseType.SUCCESS, success=True, message="Joined #general")
Event(event_type=EventType.USER_JOINED, data={"channel": "#general", "nickname": "danny"})
```

7. **Client sends message**:
```python
Command(command_type=CommandType.MESSAGE, parameters=["Hello everyone!"])
```

8. **Server broadcasts to channel**:
```python
Event(event_type=EventType.MESSAGE_BROADCAST, 
      data={"channel": "#general", "nickname": "danny", "message": "Hello everyone!"})
```
