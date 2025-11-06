"""protocol.py - Object-based protocol definitions

TODO: Define the following:

MESSAGE TYPES:
- Command messages (CONNECT, NICK, LIST, JOIN, LEAVE, QUIT, HELP)
- Event messages (USER_JOINED, USER_LEFT, MESSAGE_BROADCAST)
- Response messages (SUCCESS, ERROR, CHANNEL_LIST, USER_LIST)

PROTOCOL STRUCTURES:
- Base Message class with serialization methods
- Command classes inheriting from Message
- Event classes for server notifications
- Response classes for server replies
- JSON serialization/deserialization methods

CONSTANTS:
- Command type enums
- Error codes
- Maximum message lengths
- Protocol version information

TASKS TO IMPLEMENT:
1. Create MessageType enum (COMMAND, EVENT, RESPONSE)
2. Create CommandType enum (CONNECT, NICK, LIST, JOIN, LEAVE, QUIT, HELP, MESSAGE)
3. Create EventType enum (USER_JOINED, USER_LEFT, MESSAGE_BROADCAST, etc.)
4. Create ResponseType enum (SUCCESS, ERROR, CHANNEL_LIST, USER_LIST, HELP_TEXT)
5. Create ErrorCode enum (INVALID_COMMAND, NICKNAME_IN_USE, etc.)
6. Define protocol constants (MAX_MESSAGE_LENGTH, MAX_NICKNAME_LENGTH, etc.)
7. Create base Message dataclass with to_json(), from_json(), validate() methods
8. Create Command dataclass inheriting from Message
9. Create Event dataclass inheriting from Message
10. Create Response dataclass inheriting from Message
11. Implement parse_irc_command() utility function
12. Implement create_error_response() utility function
13. Implement create_success_response() utility function
14. Add command-specific validation methods (validate_connect, validate_nick, etc.)
"""
