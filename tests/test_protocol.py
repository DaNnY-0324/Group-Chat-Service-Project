#!/usr/bin/env python3
"""test_protocol.py - Unit tests for protocol module

This module contains comprehensive unit tests for the protocol classes,
enums, validation functions, and utility methods.
"""

import unittest
import sys
import os
import time
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from protocol import (
    MessageType, CommandType, EventType, ResponseType, ErrorCode,
    Message, Command, Event, Response,
    parse_irc_command, create_error_response, create_success_response,
    validate_nickname, validate_channel_name, validate_connect_params,
    validate_nick_params, validate_join_params, validate_leave_params,
    validate_message_params, MAX_MESSAGE_LENGTH, MAX_NICKNAME_LENGTH,
    MAX_CHANNEL_NAME_LENGTH, PROTOCOL_VERSION
)


class TestProtocolEnums(unittest.TestCase):
    """Test protocol enum classes"""
    
    def test_message_type_enum(self):
        """Test MessageType enum values"""
        self.assertEqual(MessageType.COMMAND.value, "command")
        self.assertEqual(MessageType.EVENT.value, "event")
        self.assertEqual(MessageType.RESPONSE.value, "response")
    
    def test_command_type_enum(self):
        """Test CommandType enum values"""
        self.assertEqual(CommandType.CONNECT.value, "connect")
        self.assertEqual(CommandType.NICK.value, "nick")
        self.assertEqual(CommandType.LIST.value, "list")
        self.assertEqual(CommandType.JOIN.value, "join")
        self.assertEqual(CommandType.LEAVE.value, "leave")
        self.assertEqual(CommandType.QUIT.value, "quit")
        self.assertEqual(CommandType.HELP.value, "help")
        self.assertEqual(CommandType.MESSAGE.value, "message")
    
    def test_event_type_enum(self):
        """Test EventType enum values"""
        self.assertEqual(EventType.USER_JOINED.value, "user_joined")
        self.assertEqual(EventType.USER_LEFT.value, "user_left")
        self.assertEqual(EventType.MESSAGE_BROADCAST.value, "message_broadcast")
    
    def test_response_type_enum(self):
        """Test ResponseType enum values"""
        self.assertEqual(ResponseType.SUCCESS.value, "success")
        self.assertEqual(ResponseType.ERROR.value, "error")
        self.assertEqual(ResponseType.CHANNEL_LIST.value, "channel_list")
    
    def test_error_code_enum(self):
        """Test ErrorCode enum values"""
        self.assertEqual(ErrorCode.INVALID_COMMAND.value, "invalid_command")
        self.assertEqual(ErrorCode.NICKNAME_IN_USE.value, "nickname_in_use")
        self.assertEqual(ErrorCode.INVALID_NICKNAME.value, "invalid_nickname")


class TestMessageClasses(unittest.TestCase):
    """Test message dataclasses"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.timestamp = time.time()
    
    def test_command_creation(self):
        """Test Command message creation"""
        cmd = Command(
            message_type=MessageType.COMMAND,
            timestamp=self.timestamp,
            command_type=CommandType.NICK,
            parameters={'nickname': 'testuser'}
        )
        
        self.assertEqual(cmd.message_type, MessageType.COMMAND)
        self.assertEqual(cmd.command_type, CommandType.NICK)
        self.assertEqual(cmd.parameters['nickname'], 'testuser')
        self.assertTrue(cmd.validate())
    
    def test_event_creation(self):
        """Test Event message creation"""
        event = Event(
            message_type=MessageType.EVENT,
            timestamp=self.timestamp,
            event_type=EventType.USER_JOINED,
            data={'user': 'testuser', 'channel': '#general'}
        )
        
        self.assertEqual(event.message_type, MessageType.EVENT)
        self.assertEqual(event.event_type, EventType.USER_JOINED)
        self.assertEqual(event.data['user'], 'testuser')
        self.assertTrue(event.validate())
    
    def test_response_creation(self):
        """Test Response message creation"""
        response = Response(
            message_type=MessageType.RESPONSE,
            timestamp=self.timestamp,
            response_type=ResponseType.SUCCESS,
            success=True,
            data={'message': 'Operation successful'}
        )
        
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        self.assertEqual(response.response_type, ResponseType.SUCCESS)
        self.assertTrue(response.success)
        self.assertTrue(response.validate())
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        cmd = Command(
            message_type=MessageType.COMMAND,
            timestamp=self.timestamp,
            command_type=CommandType.NICK,
            parameters={'nickname': 'testuser'}
        )
        
        # Test serialization
        json_str = cmd.to_json()
        self.assertIsInstance(json_str, str)
        
        # Verify JSON is valid
        data = json.loads(json_str)
        self.assertEqual(data['command_type'], 'nick')
        self.assertEqual(data['parameters']['nickname'], 'testuser')


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_parse_irc_command(self):
        """Test IRC command parsing"""
        # Test regular message
        cmd, params = parse_irc_command("Hello world")
        self.assertEqual(cmd, "message")
        self.assertEqual(params, ["Hello world"])
        
        # Test command with parameters
        cmd, params = parse_irc_command("/nick testuser")
        self.assertEqual(cmd, "nick")
        self.assertEqual(params, ["testuser"])
        
        # Test command without parameters
        cmd, params = parse_irc_command("/list")
        self.assertEqual(cmd, "list")
        self.assertEqual(params, [])
        
        # Test command with multiple parameters
        cmd, params = parse_irc_command("/join #general password")
        self.assertEqual(cmd, "join")
        self.assertEqual(params, ["#general", "password"])
    
    def test_create_error_response(self):
        """Test error response creation"""
        timestamp = time.time()
        response = create_error_response(
            ErrorCode.INVALID_NICKNAME,
            "Invalid nickname format",
            timestamp
        )
        
        self.assertEqual(response.response_type, ResponseType.ERROR)
        self.assertFalse(response.success)
        self.assertEqual(response.error_code, ErrorCode.INVALID_NICKNAME)
        self.assertEqual(response.data['message'], "Invalid nickname format")
    
    def test_create_success_response(self):
        """Test success response creation"""
        timestamp = time.time()
        response = create_success_response(
            ResponseType.SUCCESS,
            {'message': 'Operation completed'},
            timestamp
        )
        
        self.assertEqual(response.response_type, ResponseType.SUCCESS)
        self.assertTrue(response.success)
        self.assertEqual(response.data['message'], 'Operation completed')


class TestValidationFunctions(unittest.TestCase):
    """Test validation functions"""
    
    def test_validate_nickname(self):
        """Test nickname validation"""
        # Valid nicknames
        self.assertTrue(validate_nickname("alice"))
        self.assertTrue(validate_nickname("user123"))
        self.assertTrue(validate_nickname("test_user"))
        
        # Invalid nicknames
        self.assertFalse(validate_nickname(""))  # Empty
        self.assertFalse(validate_nickname("123user"))  # Starts with number
        self.assertFalse(validate_nickname("user-name"))  # Contains hyphen
        self.assertFalse(validate_nickname("a" * 17))  # Too long
        self.assertFalse(validate_nickname("user@host"))  # Contains @
    
    def test_validate_channel_name(self):
        """Test channel name validation"""
        # Valid channel names
        self.assertTrue(validate_channel_name("#general"))
        self.assertTrue(validate_channel_name("#test-channel"))
        self.assertTrue(validate_channel_name("#room_123"))
        
        # Invalid channel names
        self.assertFalse(validate_channel_name(""))  # Empty
        self.assertFalse(validate_channel_name("general"))  # No #
        self.assertFalse(validate_channel_name("#"))  # Only #
        self.assertFalse(validate_channel_name("#" + "a" * 32))  # Too long
        self.assertFalse(validate_channel_name("#test@channel"))  # Invalid char
    
    def test_validate_connect_params(self):
        """Test CONNECT parameter validation"""
        # Valid parameters
        self.assertTrue(validate_connect_params({'server': 'localhost'}))
        self.assertTrue(validate_connect_params({'server': 'localhost', 'port': 8080}))
        
        # Invalid parameters
        self.assertFalse(validate_connect_params({}))  # Missing server
        self.assertFalse(validate_connect_params({'port': 8080}))  # Missing server
    
    def test_validate_nick_params(self):
        """Test NICK parameter validation"""
        # Valid parameters
        self.assertTrue(validate_nick_params({'nickname': 'alice'}))
        
        # Invalid parameters
        self.assertFalse(validate_nick_params({}))  # Missing nickname
        self.assertFalse(validate_nick_params({'nickname': '123invalid'}))  # Invalid nickname
    
    def test_validate_join_params(self):
        """Test JOIN parameter validation"""
        # Valid parameters
        self.assertTrue(validate_join_params({'channel': '#general'}))
        
        # Invalid parameters
        self.assertFalse(validate_join_params({}))  # Missing channel
        self.assertFalse(validate_join_params({'channel': 'invalid'}))  # Invalid channel
    
    def test_validate_leave_params(self):
        """Test LEAVE parameter validation"""
        # Valid parameters (channel is optional)
        self.assertTrue(validate_leave_params({}))  # No channel
        self.assertTrue(validate_leave_params({'channel': '#general'}))  # Valid channel
        
        # Invalid parameters
        self.assertFalse(validate_leave_params({'channel': 'invalid'}))  # Invalid channel
    
    def test_validate_message_params(self):
        """Test MESSAGE parameter validation"""
        # Valid parameters
        self.assertTrue(validate_message_params({'content': 'Hello world'}))
        self.assertTrue(validate_message_params({'content': 'A' * MAX_MESSAGE_LENGTH}))
        
        # Invalid parameters
        self.assertFalse(validate_message_params({}))  # Missing content
        self.assertFalse(validate_message_params({'content': 123}))  # Not string
        self.assertFalse(validate_message_params({'content': 'A' * (MAX_MESSAGE_LENGTH + 1)}))  # Too long


class TestProtocolConstants(unittest.TestCase):
    """Test protocol constants"""
    
    def test_constants(self):
        """Test protocol constant values"""
        self.assertEqual(MAX_MESSAGE_LENGTH, 512)
        self.assertEqual(MAX_NICKNAME_LENGTH, 16)
        self.assertEqual(MAX_CHANNEL_NAME_LENGTH, 32)
        self.assertEqual(PROTOCOL_VERSION, "1.0")


if __name__ == '__main__':
    unittest.main()
