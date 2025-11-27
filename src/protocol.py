"""protocol.py - Object-based protocol definitions

This module defines the object-based protocol for the chat server system.
All communication between client and server uses JSON-serialized objects.
"""

import json
import re
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Union


# Protocol Constants
MAX_MESSAGE_LENGTH = 512
MAX_NICKNAME_LENGTH = 16
MAX_CHANNEL_NAME_LENGTH = 32
PROTOCOL_VERSION = "1.0"


class MessageType(Enum):
    """Types of messages in the protocol"""
    COMMAND = "command"
    EVENT = "event"
    RESPONSE = "response"


class CommandType(Enum):
    """IRC-style commands supported by the protocol"""
    CONNECT = "connect"
    NICK = "nick"
    LIST = "list"
    JOIN = "join"
    LEAVE = "leave"
    QUIT = "quit"
    HELP = "help"
    MESSAGE = "message"


class EventType(Enum):
    """Server events sent to clients"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    MESSAGE_BROADCAST = "message_broadcast"
    CHANNEL_CREATED = "channel_created"
    NICKNAME_CHANGED = "nickname_changed"
    SERVER_SHUTDOWN = "server_shutdown"


class ResponseType(Enum):
    """Server responses to client commands"""
    SUCCESS = "success"
    ERROR = "error"
    CHANNEL_LIST = "channel_list"
    USER_LIST = "user_list"
    HELP_TEXT = "help_text"
    WELCOME = "welcome"


class ErrorCode(Enum):
    """Error codes for failed operations"""
    INVALID_COMMAND = "invalid_command"
    NICKNAME_IN_USE = "nickname_in_use"
    INVALID_NICKNAME = "invalid_nickname"
    CHANNEL_NOT_FOUND = "channel_not_found"
    INVALID_CHANNEL_NAME = "invalid_channel_name"
    NOT_IN_CHANNEL = "not_in_channel"
    ALREADY_IN_CHANNEL = "already_in_channel"
    SERVER_FULL = "server_full"
    CONNECTION_FAILED = "connection_failed"
    PERMISSION_DENIED = "permission_denied"
    MESSAGE_TOO_LONG = "message_too_long"


@dataclass
class Message:
    """Base message class for all protocol communications"""
    message_type: MessageType
    timestamp: float
    version: str = PROTOCOL_VERSION
    
    def to_json(self) -> str:
        """Serialize message to JSON string"""
        data = asdict(self)
        # Convert enums to their values
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize message from JSON string"""
        try:
            data = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid JSON message: {e}")
    
    def validate(self) -> bool:
        """Validate message structure and content"""
        return (
            hasattr(self, 'message_type') and
            hasattr(self, 'timestamp') and
            hasattr(self, 'version') and
            self.version == PROTOCOL_VERSION
        )


@dataclass
class Command(Message):
    """Command message from client to server"""
    command_type: CommandType = None
    parameters: Dict[str, Any] = None
    client_id: Optional[str] = None
    
    def __post_init__(self):
        self.message_type = MessageType.COMMAND
        if self.parameters is None:
            self.parameters = {}
    
    def validate(self) -> bool:
        """Validate command message"""
        return (
            super().validate() and
            hasattr(self, 'command_type') and
            hasattr(self, 'parameters') and
            isinstance(self.parameters, dict)
        )


@dataclass
class Event(Message):
    """Event message from server to clients"""
    event_type: EventType = None
    data: Dict[str, Any] = None
    channel: Optional[str] = None
    
    def __post_init__(self):
        self.message_type = MessageType.EVENT
        if self.data is None:
            self.data = {}
    
    def validate(self) -> bool:
        """Validate event message"""
        return (
            super().validate() and
            hasattr(self, 'event_type') and
            hasattr(self, 'data') and
            isinstance(self.data, dict)
        )


@dataclass
class Response(Message):
    """Response message from server to client"""
    response_type: ResponseType = None
    success: bool = False
    data: Dict[str, Any] = None
    error_code: Optional[ErrorCode] = None
    
    def __post_init__(self):
        self.message_type = MessageType.RESPONSE
        if self.data is None:
            self.data = {}
    
    def validate(self) -> bool:
        """Validate response message"""
        return (
            super().validate() and
            hasattr(self, 'response_type') and
            hasattr(self, 'success') and
            hasattr(self, 'data') and
            isinstance(self.data, dict)
        )


# Utility Functions

def parse_irc_command(command_line: str) -> tuple[str, List[str]]:
    """Parse IRC-style command line into command and parameters"""
    if not command_line.startswith('/'):
        return 'message', [command_line]
    
    parts = command_line[1:].split()
    if not parts:
        return '', []
    
    command = parts[0].lower()
    params = parts[1:] if len(parts) > 1 else []
    
    return command, params


def create_error_response(error_code: ErrorCode, message: str, timestamp: float) -> Response:
    """Create a standardized error response"""
    return Response(
        message_type=MessageType.RESPONSE,
        response_type=ResponseType.ERROR,
        success=False,
        data={'message': message},
        error_code=error_code,
        timestamp=timestamp
    )


def create_success_response(response_type: ResponseType, data: Dict[str, Any], timestamp: float) -> Response:
    """Create a standardized success response"""
    return Response(
        message_type=MessageType.RESPONSE,
        response_type=response_type,
        success=True,
        data=data,
        timestamp=timestamp
    )


# Validation Functions

def validate_nickname(nickname: str) -> bool:
    """Validate nickname format and length"""
    if not nickname or len(nickname) > MAX_NICKNAME_LENGTH:
        return False
    
    # Nickname must start with letter, contain only alphanumeric and underscore
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, nickname))


def validate_channel_name(channel: str) -> bool:
    """Validate channel name format and length"""
    if not channel or len(channel) > MAX_CHANNEL_NAME_LENGTH:
        return False
    
    # Channel must start with #, contain only alphanumeric, underscore, and hyphen
    pattern = r'^#[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, channel))


def validate_connect_params(params: Dict[str, Any]) -> bool:
    """Validate CONNECT command parameters"""
    required_keys = ['server']
    return all(key in params for key in required_keys)


def validate_nick_params(params: Dict[str, Any]) -> bool:
    """Validate NICK command parameters"""
    return 'nickname' in params and validate_nickname(params['nickname'])


def validate_join_params(params: Dict[str, Any]) -> bool:
    """Validate JOIN command parameters"""
    return 'channel' in params and validate_channel_name(params['channel'])


def validate_leave_params(params: Dict[str, Any]) -> bool:
    """Validate LEAVE command parameters"""
    # Channel parameter is optional for LEAVE
    if 'channel' in params:
        return validate_channel_name(params['channel'])
    return True


def validate_message_params(params: Dict[str, Any]) -> bool:
    """Validate MESSAGE parameters"""
    return (
        'content' in params and 
        isinstance(params['content'], str) and
        len(params['content']) <= MAX_MESSAGE_LENGTH
    )
