"""irc_protocol.py 

CSC4220: Computer Networks - Chat Server Project
Team: Danny Nguyen, David Salas, Romeo Henderson
File Created by Romeo Henderson
"""
import json
import re
from enum import Enum, unique
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List



#Protocol constaints from RFC 1459
class IRCLimits (Enum):
    MAX_MESSAGE_LENGTH = 512
    MAX_NICKNAME_LENGTH = 9
    MAX_CHANNEL_NAME_LENGTH = 200
    DEFAULT_PORT = 5555
    #regex for nickname restriction: nicknames cannot contain . , * \ ? ! @ or spaces 
    NICKNAME_ALLOWED_CHARACTERS_PATTERN = r'^[a-zA-Z][^.,*\?!@ ]*$'

#Enums used for IRC protocol
@unique
class IRCMessageType (Enum):
    COMMAND = "COMMAND"     #CLIENT -> SERVER REQUESTS
    EVENT = "EVENT"         #SERVER -> CLIENT NOTIFICATIONS
    RESPONSE = "RESPONSE" #SERVER -> CLIENT REPLIES

@unique 
class IRCCommandType (Enum):
    #Standard IRC Commands
    CONNECT = "CONNECT"
    NICK = "NICK"
    LIST = "LIST"
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    QUIT = "QUIT"
    HELP = "HELP"
    MESSAGE = "MESSAGE" 

@unique 
class IRCEventType (Enum):
    #enums for server-initiated notifications
    USER_JOINED = "USER_JOINED"   
    USER_LEFT = "USER_LEFT"
    MESSAGE_BROADCAST = "MESSAGE_BROADCAST"

@unique
class IRCResponseType (Enum):
    #server replies enums 
    #CHANNEL_LIST = "CHANNEL_LIST"
    RPL_SUCCESS = "SUCCESS"
    RPL_ERROR = "ERROR"
    RPL_CHANNEL_LIST = "CHANNEL_LIST"
    RPL_HELP_TEXT = "HELP_TEXT"

@unique
class IRCErrorCode (Enum):
    ERR_INVALID_COMMAND = 400
    ERR_NICKNAME_REQUIRED = 410
    ERR_NICKNAME_IN_USE = 411
    ERR_NOT_IN_CHANNEL = 421
    ERR_INVALID_CHANNEL_NAME = 424

# Message class using @dataclass decorator for clean dunder methods
@dataclass
class Message: 
    messageType: Optional[IRCMessageType] = None #made optional
    #serializes (conversion of data structure/enum to json string) 
    def to_json(self)-> str: 
        #converts enum values to json string
        data = self._to_dict() #converts dataclass instance self (the first parameter in instance method within a class)as a dictionary
        return json.dumps(data)
    
    def _to_dict(self)-> Dict[str, Any]:
        #convert message to dictionary
        result={
            'messageType': self.messageType.value if self.messageType else None
        }
        return result 

    @staticmethod
    def from_json(json_str: str)-> Optional ['Message']:
        #deserializes a JSON string into a Message object (or subclass)
        try:
            data = json.loads(json_str)
            msgType = IRCMessageType(data['messageType']) 
            if msgType == IRCMessageType.COMMAND:
                return Command.from_dict(data) 
            elif msgType == IRCMessageType.EVENT:
                return Event.from_dict(data)
            elif msgType == IRCMessageType.RESPONSE:
                return Response.from_dict(data)
            else:
                return Message(**data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error in deserializing JSON string: {e}")
            return None
        #validation for messages, such as length 
    def validate(self)->tuple [bool, Optional[str]]:
        if len(self.to_json())> IRCLimits.MAX_MESSAGE_LENGTH.value:
            return False, "Message exceeds IRC Message Limit"
        return True, None 
    
#Command class that inherits from Message parent 
@dataclass
class Command (Message):
    #command messages sent from client to server 
    commandType: IRCCommandType
    parameters: Dict[str, Any] = field(default_factory=dict)
    #used post init to connect an instance of Command with its messagetype from message
    def __post_init__(self):
        self.messageType = IRCMessageType.COMMAND

    def _to_dict(self) -> Dict[str,Any]:
        result = super()._to_dict()
        result['commandType'] = self.commandType.value
        result ['parameters'] = self.parameters
        return result 
    #create command from dictionary
    @staticmethod
    def from_dict (data: Dict[str, Any])-> 'Command': 
        return Command(
            commandType = IRCCommandType(data['commandType']),
            parameters = data.get('parameters', {})
        )
    #command validations such has nickname length, nickname characters, etc. 
    def validate(self)-> tuple[bool, Optional[str]]:
        #checks parent validation first 
        valid, error = super().validate()
        if not valid:
            return False, error
        if not self.commandType:
            return False, "Command type missing"
        # Command validations using match/switch statement 
        match self.commandType:
            case IRCCommandType.CONNECT:
                return validate_Connect(self.parameters)
            case IRCCommandType.NICK:
                 return validate_Nick(self.parameters)
            case IRCCommandType.JOIN:
                 return validate_Join(self.parameters)
            case IRCCommandType.LEAVE:
                 return validate_Leave(self.parameters)
            case IRCCommandType.MESSAGE:
                 return validate_Message(self.parameters)
            case _: 
                return True, None
            
#Event class that inherits from Message            
@dataclass
class Event(Message):
    #event messages sent from server to client, defaults to None
    eventType: IRCEventType
    parameters: Dict[str,Any] = field(default_factory=dict)
#a data class that runs after init setting every event up automatically with message type
    def __post_init__(self):
        self.messageType = IRCMessageType.EVENT

    def _to_dict(self) -> Dict[str, Any]:
        result = super()._to_dict()
        result ['eventType'] = self.eventType.value
        result ['parameters'] = self.parameters
        return result 
    #create event dictionary 
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Event':
        return Event (
            eventType = IRCEventType(data['eventType']),
            parameters = data.get('parameters', {})
        )
    #event vailidation 
    def validate(self)-> tuple[bool, Optional[str]]:
         #validate event message 
        valid, error = super().validate()

        if not valid: 
            return False, error 
    #checks if event type is set 
        if not self.eventType:
            return False, "Event type missing"
        return True, None 

#Reponse class that inherits from Message
@dataclass
class Response (Message):
    #Response messages sent from server to client 
    responseType: IRCResponseType
    success: bool = True
    message: Optional[str]= None
    errorCode: Optional[IRCErrorCode]= None
    data: Dict[str, Any] = field(default_factory=dict) #additional response data for list command
    def __post_init__(self):
        self.messageType = IRCMessageType.RESPONSE
    
    def _to_dict(self)-> Dict[str, Any]:
        result = super()._to_dict()
        result['responseType'] = self.responseType.value
        result['success'] = self.success 
        result['message'] = self.message
        if self.errorCode:
            result['errorCode'] = self.errorCode.value
        return result 
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Response':
        #create response from dictionary 
        errorCode = None
        if 'errorCode' in data and data['errorCode']:
            errorCode = IRCErrorCode(data['errorCode'])

        return Response(
            responseType= IRCResponseType (data['responseType']),
            success = data.get('success', True),
            message = data.get('message', ''),
            errorCode = errorCode
        )
    
    def validate(self)->tuple [bool, Optional[str]]:
        valid, error = super().validate()
        if not valid: 
            return False, error 
        if not self.responseType:
            return False, "Response type missing"
        if not self.success and not self.errorCode:
            return False, "Error response missing error code"
        return True, None
    
#Command validations 
def validate_Connect (paramaters: Dict[str, Any])-> tuple[bool, Optional[str]]:
    if 'server' not in paramaters:
        return False, "Missing server parameter"
    server = paramaters['server'] #extracting server from dictionary 
    if not server or not isinstance (server, str):
        return False, "Invalid server name "
    if 'port' in paramaters:
        port = paramaters['port']
        if not isinstance(port, int) or port<1 or port >65535:
            return False, "Invalid port number"
    return True, None

def validate_Nick(parameters: Dict[str, Any])->tuple [bool, Optional[str]]:
    if 'nickname' not in parameters:
        return False, "Missing nickname parameter"
    nickname = parameters['nickname']
    if not nickname or not isinstance (nickname, str):
        return False, "Invalid nickname"
    if len(nickname)>IRCLimits.MAX_NICKNAME_LENGTH.value:
        return False, f"Nickname exceeds limit of {IRCLimits.MAX_NICKNAME_LENGTH.value} characters"
    if not re.match(IRCLimits.NICKNAME_ALLOWED_CHARACTERS_PATTERN.value, nickname):
        return False, "Nickname contains invalid characters"
    return True, None

def validate_Join (parameters: Dict[str, Any])-> tuple[bool, Optional[str]]:
    if 'channel' not in parameters:
        return False, "Missing channel parameter"
    channel = parameters['channel']
    if not channel or not isinstance (channel, str):
        return False, "Invalid channel name"
    if len(channel)>IRCLimits.MAX_CHANNEL_NAME_LENGTH.value:
        return False, f"Channel name exceeds {IRCLimits.MAX_CHANNEL_NAME_LENGTH.value} characters"
    if not channel.startswith('#'):
        return False, "Channel name is required to start with #"
    return True, None

def validate_Leave (parameters: Dict[str, Any])-> tuple [bool, Optional[str]]:
    #leave will leave any current ch, no validation required
    return True, None

def validate_Message(parameters: Dict[str, Any])-> tuple[bool, Optional[str]]:
    if 'channel' not in parameters:
        return False, "Missing channel parameter"
    if 'text' not in parameters:
        return False, "Missing message parameter"
    text = parameters ['text']
    if not text or not isinstance(text, str):
        return False, "Invalid message"
    if len(text)>IRCLimits.MAX_MESSAGE_LENGTH.value:
        return False, f"Message exceeds {IRCLimits.MAX_MESSAGE_LENGTH.value} characters"
    return True, None


#parser used to go through irc commands and turn them into objects
def parseIRCCOMMAND (commandStr: str)->Optional[Command]:
    if not commandStr or not commandStr.startswith('/'):
        return None 
    parts = commandStr[1:].split(None, 2) #remove / and splits
    if not parts:
        return None
    command = parts[0].upper()

    try: 
        match command:
            case 'CONNECT':
                 server = parts[1] if len(parts) > 1 else None
                 port = int(parts[2]) if len(parts) > 2 else IRCLimits.DEFAULT_PORT.value
                 return Command(
                    commandType=IRCCommandType.CONNECT,
                    parameters={'server': server, 'port': port}
                 )
            case 'NICK':
                nickname = parts[1] if len(parts) > 1 else None
                return Command(
                commandType=IRCCommandType.NICK,
                parameters = {'nickname': nickname}
                 )
            case 'LIST':
                return Command(commandType = IRCCommandType.LIST)
            case 'JOIN':
                channel = parts[1] if len(parts) > 1 else None
                if channel and not channel.startswith('#'):
                    channel = '#' + channel
                return Command(
                    commandType = IRCCommandType.JOIN,
                    parameters = {'channel': channel}
                 )
        
            case 'LEAVE':
                channel = parts[1] if len(parts) > 1 else None
                return Command(
                    commandType = IRCCommandType.LEAVE,
                    parameters = {'channel': channel}
                )
        
            case 'QUIT':
                return Command(commandType = IRCCommandType.QUIT)
        
            case 'HELP':
                return Command(commandType = IRCCommandType.HELP)
            case 'MESSAGE':
                if len(parts) < 3:
                    return None
                channel = parts[1]
                text = parts[2]
                if channel and not channel.startswith('#'):
                    channel = '#' + channel
                return Command(
                     commandType=IRCCommandType.MESSAGE,
                     parameters={'channel': channel, 'text': text}
                 )
            case _:
                return None
    except (IndexError, ValueError):
        return None
#function for giving error codes and generating a Response instance 
def createErrorResponse (errorCode: IRCErrorCode, message:str)-> Response:
    return Response(
        responseType = IRCResponseType.RPL_ERROR,
        success = False,
        message = message,
        errorCode = errorCode,
    )
#help function that explain all the accepted commands 
def createHelpResponse()->Response:
    helpTXT = '''
Available Commands: 
    /connect <server> [port]    - connects to server
    /nick <nickname>            - creates server name 
    /list                       - list all chs and users 
    /join <channel>             - join a channel 
    /leave [channel]            - leave current channel
    /quit                       - Disconnect from server 
    /help                       - Shows available commands 

    Channel names must start with #
'''
    return Response (
        responseType = IRCResponseType.RPL_HELP_TEXT,
        success = True,
        message = helpTXT.strip()
    )
