"""chat_client.py - Simple text-based chat client

CSC4220: Computer Networks - Chat Server Project
Team: Danny Nguyen, David Salas, Romeo Henderson
File Created by Danny Nguyen
"""

import socket
import threading
import json
import sys
import time
from typing import Optional, Dict, Any


# Simple color codes for client output
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_CYAN = '\033[1;36m'
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        return f"{color}{text}{Colors.RESET}"


class ChatClient:
    """
    Simple text-based chat client for connecting to ChatServer
    """
    
    def __init__(self):
        """
        Initialize the chat client
        """
        self.client_socket = None
        self.connected = False
        self.nickname = ""
        self.current_channel = ""
        self.receive_thread = None
        self.running = False
        self.server_host = ""
        self.server_port = 0
    
    def connect_to_server(self, server_name: str, port: int = 8080) -> bool:
        """
        Connect to the chat server
        
        Args:
            server_name: Server hostname or IP address
            port: Server port number
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create client socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)  # 10 second timeout
            
            # Connect to server
            print(f"Connecting to {server_name}:{port}...")
            self.client_socket.connect((server_name, port))
            
            # Connection successful
            self.connected = True
            self.server_host = server_name
            self.server_port = port
            self.running = True
            
            # Start message receiving thread
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
            self.display_message(f"Connected to {server_name}:{port}", "success")
            self.display_message("Set your nickname with: /nick <your_nickname>", "info")
            return True
            
        except socket.timeout:
            self.display_message("Connection timeout. Server may be down.", "error")
            return False
        except ConnectionRefusedError:
            self.display_message(f"Connection refused. Is the server running on {server_name}:{port}?", "error")
            return False
        except socket.gaierror:
            self.display_message(f"Cannot resolve hostname: {server_name}", "error")
            return False
        except Exception as e:
            self.display_message(f"Connection error: {e}", "error")
            return False
    
    def send_command(self, command_str: str) -> bool:
        """
        Send command to server
        
        Args:
            command_str: Command string to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or not self.client_socket:
            self.display_message("Not connected to server. Use /connect first.", "error")
            return False
        
        try:
            # Create simple message format (we'll use JSON-like structure)
            message = {
                "type": "command",
                "command": command_str,
                "nickname": self.nickname,
                "timestamp": time.time()
            }
            
            # Send as JSON
            message_json = json.dumps(message) + "\n"
            self.client_socket.send(message_json.encode('utf-8'))
            return True
            
        except BrokenPipeError:
            self.display_message("Connection lost to server.", "error")
            self.connected = False
            return False
        except Exception as e:
            self.display_message(f"Error sending command: {e}", "error")
            return False
    
    def receive_messages(self) -> None:
        """
        Receive messages from server (runs in separate thread)
        """
        buffer = ""
        
        while self.running and self.connected:
            try:
                # Receive data from server
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    # Server closed connection
                    self.display_message("Server closed connection.", "error")
                    self.connected = False
                    break
                
                buffer += data
                
                # Process complete messages (separated by newlines)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self.process_server_message(line.strip())
                        
            except socket.timeout:
                continue  # Keep trying
            except Exception as e:
                if self.running:  # Only show error if we're still supposed to be running
                    self.display_message(f"Error receiving messages: {e}", "error")
                break
        
        self.connected = False
    
    def process_server_message(self, message: str) -> None:
        """
        Process a message received from the server
        
        Args:
            message: Raw message from server
        """
        try:
            # Try to parse as JSON
            data = json.loads(message)
            
            if data.get("type") == "response":
                # Server response to our command
                if data.get("success"):
                    self.display_message(data.get("message", "Success"), "success")
                else:
                    self.display_message(data.get("message", "Error"), "error")
                    
            elif data.get("type") == "event":
                # Server event (user joined, message broadcast, etc.)
                event_type = data.get("event")
                
                if event_type == "message":
                    # Chat message
                    nickname = data.get("nickname", "Unknown")
                    channel = data.get("channel", "")
                    msg = data.get("message", "")
                    self.display_message(f"[{channel}] <{nickname}> {msg}", "chat")
                    
                elif event_type == "user_joined":
                    nickname = data.get("nickname", "Unknown")
                    channel = data.get("channel", "")
                    self.display_message(f"*** {nickname} joined {channel}", "info")
                    
                elif event_type == "user_left":
                    nickname = data.get("nickname", "Unknown")
                    channel = data.get("channel", "")
                    self.display_message(f"*** {nickname} left {channel}", "info")
                    
                elif event_type == "channel_list":
                    channels = data.get("channels", [])
                    self.display_message("\n=== Channel List ===", "info")
                    if channels:
                        for channel in channels:
                            name = channel.get("name", "")
                            count = channel.get("users", 0)
                            self.display_message(f"  {name} ({count} users)", "info")
                    else:
                        self.display_message("  No channels available", "info")
                    self.display_message("==================\n", "info")
                    
            else:
                # Plain text message
                self.display_message(message, "info")
                
        except json.JSONDecodeError:
            # Not JSON, treat as plain text
            self.display_message(message, "info")
    
    def process_user_input(self) -> None:
        """
        Process user input from terminal
        """
        while self.running:
            try:
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command or regular message
                if user_input.startswith("/"):
                    # It's a command
                    if not self.parse_and_handle_command(user_input):
                        continue
                else:
                    # It's a regular chat message
                    if not self.connected:
                        self.display_message("Not connected. Use /connect to connect to a server.", "error")
                        continue
                    
                    if not self.current_channel:
                        self.display_message("Not in a channel. Use /join <channel> to join a channel.", "error")
                        continue
                    
                    # Send as regular message
                    self.send_command(user_input)
                    
            except EOFError:
                # Ctrl+D pressed
                break
            except KeyboardInterrupt:
                # Ctrl+C pressed
                break
    
    def parse_and_handle_command(self, command_str: str) -> bool:
        """
        Parse and handle IRC-style commands
        
        Args:
            command_str: Command string starting with /
            
        Returns:
            True if command was handled, False otherwise
        """
        parts = command_str[1:].split()  # Remove / and split
        if not parts:
            return False
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "connect":
            if len(args) < 1:
                self.display_message("Usage: /connect <server> [port]", "error")
                return False
            
            server = args[0]
            port = int(args[1]) if len(args) > 1 else 8080
            
            if self.connected:
                self.display_message("Already connected. Use /quit to disconnect first.", "error")
                return False
            
            return self.connect_to_server(server, port)
        
        elif cmd == "nick":
            if len(args) < 1:
                self.display_message("Usage: /nick <nickname>", "error")
                return False
            
            new_nick = args[0]
            if len(new_nick) > 32:
                self.display_message("Nickname too long (max 32 characters)", "error")
                return False
            
            self.nickname = new_nick
            if self.connected:
                self.send_command(command_str)
            else:
                self.display_message(f"Nickname set to '{new_nick}' (will be used when you connect)", "success")
            return True
        
        elif cmd == "join":
            if len(args) < 1:
                self.display_message("Usage: /join <channel>", "error")
                return False
            
            channel = args[0]
            if not channel.startswith("#"):
                channel = "#" + channel
            
            self.current_channel = channel
            return self.send_command(f"/join {channel}")
        
        elif cmd == "leave":
            channel = args[0] if args else self.current_channel
            if channel and not channel.startswith("#"):
                channel = "#" + channel
            
            if channel == self.current_channel:
                self.current_channel = ""
            
            return self.send_command(f"/leave {channel}" if channel else "/leave")
        
        elif cmd == "list":
            return self.send_command("/list")
        
        elif cmd == "quit":
            if self.connected:
                self.send_command("/quit")
                time.sleep(0.5)  # Give server time to process
            self.disconnect()
            self.running = False
            return True
        
        elif cmd == "help":
            self.show_help()
            return True
        
        else:
            self.display_message(f"Unknown command: /{cmd}. Type /help for available commands.", "error")
            return False
    
    def display_message(self, message: str, message_type: str = "info") -> None:
        """
        Display message to user with optional formatting
        
        Args:
            message: Message to display
            message_type: Type of message (info, error, success, chat)
        """
        timestamp = time.strftime("%H:%M:%S")
        
        if message_type == "error":
            print(f"[{timestamp}] {Colors.colorize(message, Colors.BOLD_RED)}")
        elif message_type == "success":
            print(f"[{timestamp}] {Colors.colorize(message, Colors.BOLD_GREEN)}")
        elif message_type == "chat":
            print(f"[{timestamp}] {message}")  # Chat messages don't need extra coloring
        elif message_type == "info":
            print(f"[{timestamp}] {Colors.colorize(message, Colors.CYAN)}")
        else:
            print(f"[{timestamp}] {message}")
    
    def show_help(self) -> None:
        """
        Display help information to user
        """
        help_text = """
=== CHAT CLIENT HELP ===

Connection Commands:
  /connect <server> [port]  - Connect to chat server (default port: 8080)
  /nick <nickname>          - Set your nickname
  /quit                     - Quit the client

Channel Commands:
  /list                     - List all channels and user counts
  /join <channel>           - Join a channel (# added automatically)
  /leave [channel]          - Leave current or specified channel

Other Commands:
  /help                     - Show this help message

Examples:
  /connect localhost 8080   - Connect to local server
  /nick danny123            - Set nickname
  /join general             - Join #general channel
  /leave                    - Leave current channel
  Hello everyone!           - Send message to current channel

Tips:
  - You must connect and set a nickname before joining channels
  - Type regular messages (without /) to chat in your current channel
  - Use Ctrl+C or /quit to exit gracefully
        """
        print(Colors.colorize(help_text, Colors.YELLOW))
    
    def disconnect(self) -> None:
        """
        Disconnect from server and clean up
        """
        self.running = False
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        
        self.display_message("Disconnected from server.", "info")
    
    def run(self) -> None:
        """
        Main client loop
        """
        self.running = True
        
        self.display_message("Chat client started. Type /help for commands.", "info")
        self.display_message("Use /connect <server> [port] to connect to a server.", "info")
        
        try:
            self.process_user_input()
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()
