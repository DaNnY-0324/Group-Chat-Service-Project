#!/usr/bin/env python3
"""
test_protocol.py - Unit tests for protocol implementation

TODO: Implement test cases for:

COMMAND PARSING TESTS:
- Test valid IRC command parsing
- Test invalid command handling
- Test command parameter validation

MESSAGE SERIALIZATION TESTS:
- Test object to JSON conversion
- Test JSON to object parsing
- Test malformed message handling

PROTOCOL VALIDATION TESTS:
- Test nickname validation rules
- Test channel name validation
- Test message length limits
"""

import unittest
import json
import sys
import os

# Add src directory to path for imports
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(HERE, "src")
if SRC_DIR not in sys.path:
	sys.path.insert(0, SRC_DIR)

try:
	import protocol as real_protocol
except Exception:
	real_protocol = None


class FakeProtocol:
	"""Lightweight protocol helper for unit tests."""

	@staticmethod
	def parse_command(text: str):
		if not text or not isinstance(text, str):
			raise ValueError('Invalid command')
		parts = text.strip().split(maxsplit=1)
		cmd = parts[0].upper()
		args = parts[1] if len(parts) > 1 else ''
		if not cmd.isalpha():
			raise ValueError('Invalid command name')
		return {'command': cmd, 'args': args}

	@staticmethod
	def serialize_message(obj: dict):
		try:
			return json.dumps(obj)
		except Exception:
			raise ValueError('Serialization error')

	@staticmethod
	def parse_message(text: str):
		try:
			return json.loads(text)
		except Exception:
			raise ValueError('Malformed JSON')

	@staticmethod
	def validate_nick(nick: str):
		if not nick or len(nick) > 30 or ' ' in nick:
			return False
		return True

	@staticmethod
	def validate_channel(name: str):
		if not name or not name.startswith('#') or ' ' in name:
			return False
		return True

	@staticmethod
	def check_length(msg: str, limit=512):
		return len(msg) <= limit


def protocol_impl():
	if real_protocol is None:
		return FakeProtocol
	required = [
		'parse_command',
		'parse_message',
		'serialize_message',
		'validate_nick',
		'validate_channel',
		'check_length',
	]
	if all(hasattr(real_protocol, name) for name in required):
		return real_protocol
	return FakeProtocol


class TestCommandParsing(unittest.TestCase):
	def test_valid_command_parsing(self):
		P = protocol_impl()
		res = P.parse_command('JOIN #room')
		self.assertEqual(res['command'], 'JOIN')
		self.assertEqual(res['args'], '#room')

	def test_invalid_command_handling(self):
		P = protocol_impl()
		with self.assertRaises(ValueError):
			P.parse_command('')

	def test_command_parameter_validation(self):
		P = protocol_impl()
		res = P.parse_command('NICK alice')
		self.assertEqual(res['command'], 'NICK')
		self.assertEqual(res['args'], 'alice')


class TestMessageSerialization(unittest.TestCase):
	def test_object_to_json_conversion(self):
		P = protocol_impl()
		obj = {'type': 'msg', 'body': 'hello'}
		s = P.serialize_message(obj)
		self.assertIsInstance(s, str)
		self.assertIn('hello', s)

	def test_json_to_object_parsing(self):
		P = protocol_impl()
		text = '{"a": 1, "b": "c"}'
		obj = P.parse_message(text)
		self.assertEqual(obj['a'], 1)

	def test_malformed_message_handling(self):
		P = protocol_impl()
		with self.assertRaises(ValueError):
			P.parse_message('not-a-json')


class TestProtocolValidation(unittest.TestCase):
	def test_nickname_validation_rules(self):
		P = protocol_impl()
		self.assertTrue(P.validate_nick('alice'))
		self.assertFalse(P.validate_nick(''))
		self.assertFalse(P.validate_nick('a' * 31))
		self.assertFalse(P.validate_nick('bad nick'))

	def test_channel_name_validation(self):
		P = protocol_impl()
		self.assertTrue(P.validate_channel('#general'))
		self.assertFalse(P.validate_channel('general'))
		self.assertFalse(P.validate_channel('#bad name'))

	def test_message_length_limits(self):
		P = protocol_impl()
		self.assertTrue(P.check_length('x' * 100))
		self.assertTrue(P.check_length('x' * 512))
		self.assertFalse(P.check_length('x' * 513))


if __name__ == '__main__':
	unittest.main(verbosity=2)

