#!/usr/bin/env python3
"""test_server.py - Integration tests for chat server

This module contains integration tests for the ChatServer functionality,
including client connections, message handling, and multi-threading.
"""

import unittest
import threading
import socket
import time
import json
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat_server import ChatServer


class TestChatServer(unittest.TestCase):
    """Integration tests for ChatServer"""
    
    def setUp(self):
        """Set up test server"""
        self.server_port = 9999  # Use a test port
        self.server = ChatServer(port=self.server_port, debug_level=0)
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(0.5)
    
    def tearDown(self):
        """Clean up after tests"""
        self.server.graceful_shutdown()
        time.sleep(0.1)
    
    def create_test_client(self):
        """Create a test client socket"""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', self.server_port))
        return client
    
    def send_message(self, client, message):
        """Send a message to server"""
        encoded = message.encode('utf-8')
        length = len(encoded).to_bytes(4, byteorder='big')
        client.sendall(length + encoded)
    
    def receive_message(self, client, timeout=1.0):
        """Receive a message from server"""
        client.settimeout(timeout)
        try:
            # Receive length
            length_data = client.recv(4)
            if not length_data:
                return None
            
            length = int.from_bytes(length_data, byteorder='big')
            
            # Receive message
            message_data = b''
            while len(message_data) < length:
                chunk = client.recv(length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return message_data.decode('utf-8')
        except socket.timeout:
            return None
        finally:
            client.settimeout(None)
    
    def test_server_startup(self):
        """Test that server starts successfully"""
        # Server should be running from setUp
        self.assertTrue(self.server.running)
    
    def test_client_connection(self):
        """Test client can connect to server"""
        client = self.create_test_client()
        
        # Should receive welcome message
        response = self.receive_message(client)
        self.assertIsNotNone(response)
        
        client.close()
    
    def test_nickname_setting(self):
        """Test setting nickname"""
        client = self.create_test_client()
        
        # Receive welcome message
        welcome = self.receive_message(client)
        self.assertIsNotNone(welcome)
        
        # Send nick command
        nick_command = json.dumps({
            "type": "command",
            "command": "nick",
            "params": ["testuser"]
        })
        self.send_message(client, nick_command)
        
        # Should receive confirmation
        response = self.receive_message(client)
        self.assertIsNotNone(response)
        
        client.close()
    
    def test_channel_operations(self):
        """Test joining and leaving channels"""
        client = self.create_test_client()
        
        # Receive welcome message
        welcome = self.receive_message(client)
        self.assertIsNotNone(welcome)
        
        # Set nickname first
        nick_command = json.dumps({
            "type": "command",
            "command": "nick",
            "params": ["testuser"]
        })
        self.send_message(client, nick_command)
        self.receive_message(client)  # Consume response
        
        # Join channel
        join_command = json.dumps({
            "type": "command",
            "command": "join",
            "params": ["#testchannel"]
        })
        self.send_message(client, join_command)
        
        # Should receive join confirmation
        response = self.receive_message(client)
        self.assertIsNotNone(response)
        
        client.close()
    
    def test_message_broadcasting(self):
        """Test message broadcasting in channels"""
        # Create two clients
        client1 = self.create_test_client()
        client2 = self.create_test_client()
        
        try:
            # Setup client1
            self.receive_message(client1)  # Welcome
            
            # Set nickname
            self.send_message(client1, json.dumps({
                "type": "command", "command": "nick", "params": ["user1"]
            }))
            self.receive_message(client1)  # Nick response
            
            # Join channel
            self.send_message(client1, json.dumps({
                "type": "command", "command": "join", "params": ["#test"]
            }))
            self.receive_message(client1)  # Join response
            
            # Setup client2
            self.receive_message(client2)  # Welcome
            
            # Set nickname
            self.send_message(client2, json.dumps({
                "type": "command", "command": "nick", "params": ["user2"]
            }))
            self.receive_message(client2)  # Nick response
            
            # Join channel
            self.send_message(client2, json.dumps({
                "type": "command", "command": "join", "params": ["#test"]
            }))
            self.receive_message(client2)  # Join response
            
            # Client1 sends message
            self.send_message(client1, json.dumps({
                "type": "message",
                "channel": "#test",
                "content": "Hello from user1"
            }))
            
            # Client2 should receive the message
            message = self.receive_message(client2, timeout=2.0)
            self.assertIsNotNone(message)
            
        finally:
            client1.close()
            client2.close()
    
    def test_multiple_clients(self):
        """Test multiple clients can connect simultaneously"""
        clients = []
        
        try:
            # Connect multiple clients
            for i in range(3):
                client = self.create_test_client()
                clients.append(client)
                
                # Should receive welcome message
                response = self.receive_message(client)
                self.assertIsNotNone(response)
        
        finally:
            # Clean up
            for client in clients:
                client.close()
    
    def test_list_channels(self):
        """Test listing channels"""
        client = self.create_test_client()
        
        try:
            # Setup
            self.receive_message(client)  # Welcome
            
            # Set nickname
            self.send_message(client, json.dumps({
                "type": "command", "command": "nick", "params": ["testuser"]
            }))
            self.receive_message(client)  # Nick response
            
            # List channels
            self.send_message(client, json.dumps({
                "type": "command", "command": "list", "params": []
            }))
            
            # Should receive channel list
            response = self.receive_message(client)
            self.assertIsNotNone(response)
            
        finally:
            client.close()
    
    def test_invalid_commands(self):
        """Test handling of invalid commands"""
        client = self.create_test_client()
        
        try:
            # Receive welcome message
            self.receive_message(client)
            
            # Send invalid command
            self.send_message(client, json.dumps({
                "type": "command",
                "command": "invalid",
                "params": []
            }))
            
            # Should receive error response
            response = self.receive_message(client)
            self.assertIsNotNone(response)
            
        finally:
            client.close()
    
    def test_concurrent_operations(self):
        """Test thread safety with concurrent operations"""
        def client_worker(client_id):
            """Worker function for concurrent client"""
            client = self.create_test_client()
            
            try:
                # Basic operations
                self.receive_message(client)  # Welcome
                
                # Set unique nickname
                self.send_message(client, json.dumps({
                    "type": "command",
                    "command": "nick",
                    "params": [f"user{client_id}"]
                }))
                self.receive_message(client)  # Response
                
                # Join channel
                self.send_message(client, json.dumps({
                    "type": "command",
                    "command": "join",
                    "params": ["#concurrent"]
                }))
                self.receive_message(client)  # Response
                
                # Send message
                self.send_message(client, json.dumps({
                    "type": "message",
                    "channel": "#concurrent",
                    "content": f"Message from user{client_id}"
                }))
                
                # Brief delay
                time.sleep(0.1)
                
            finally:
                client.close()
        
        # Create multiple concurrent clients
        threads = []
        for i in range(5):
            thread = threading.Thread(target=client_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)
    
    def test_graceful_disconnect(self):
        """Test graceful client disconnection"""
        client = self.create_test_client()
        
        try:
            # Setup client
            self.receive_message(client)  # Welcome
            
            # Set nickname
            self.send_message(client, json.dumps({
                "type": "command", "command": "nick", "params": ["testuser"]
            }))
            self.receive_message(client)  # Response
            
            # Send quit command
            self.send_message(client, json.dumps({
                "type": "command", "command": "quit", "params": []
            }))
            
            # Should receive goodbye message
            response = self.receive_message(client)
            self.assertIsNotNone(response)
            
        finally:
            client.close()


class TestServerUtilities(unittest.TestCase):
    """Test server utility functions"""
    
    def test_server_creation(self):
        """Test server can be created with different parameters"""
        # Test with default parameters
        server1 = ChatServer(port=8888)
        self.assertEqual(server1.port, 8888)
        self.assertEqual(server1.debug_level, 0)
        
        # Test with debug level
        server2 = ChatServer(port=8889, debug_level=1)
        self.assertEqual(server2.debug_level, 1)
    
    def test_invalid_port(self):
        """Test server handles invalid port numbers"""
        # This should not raise an exception during creation
        # but may fail during startup
        server = ChatServer(port=99999)  # Invalid port
        self.assertIsNotNone(server)


if __name__ == '__main__':
    # Run tests with reduced verbosity for cleaner output
    unittest.main(verbosity=1)
