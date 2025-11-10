"""chat_server.py - Main chat server implementation

CSC4220: Computer Networks - Chat Server Project
Team: Danny Nguyen, David Salas, Romeo Henderson
File Created by Danny Nguyen

STAGE 1: Single-channel, single-threaded server ✓
STAGE 2: Multi-channel support ✓
STAGE 3: Multi-threading (max 4 threads) ✓
"""

import socket
import threading
import json
import time
import signal
import sys
import select
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


# Simple color codes for server output
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


@dataclass
class ClientInfo:
    """Information about connected clients"""
    socket: socket.socket
    nickname: str = ""
    channels: Set[str] = field(default_factory=set)
    last_activity: float = field(default_factory=time.time)
    address: tuple = ("", 0)
    
    def __post_init__(self):
        if not self.last_activity:
            self.last_activity = time.time()


class ChatServer:
    """
    Multi-client chat server supporting IRC-style commands
    Supports all 3 stages: single-channel → multi-channel → multi-threaded
    """
    
    def __init__(self, port: int = 8080, debug_level: int = 0):
        """
        Initialize the chat server
        
        Args:
            port: Port number to bind to
            debug_level: 0 for errors only, 1 for all events
        """
        self.port = port
        self.debug_level = debug_level
        self.server_socket = None
        self.clients: Dict[socket.socket, ClientInfo] = {}
        self.channels: Dict[str, Set[socket.socket]] = {}
        self.running = False
        self.lock = threading.Lock()  # For thread safety in Stage 3
        self.max_threads = 4  # Stage 3 requirement
        self.active_threads = 0
        self.last_activity = time.time()
        self.inactivity_timer = None
        
        # Default channel for Stage 1
        self.default_channel = "#general"
        self.channels[self.default_channel] = set()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def log(self, message: str, level: str = "info") -> None:
        """
        Log message with timestamp and color
        
        Args:
            message: Message to log
            level: Log level (info, error, success, debug)
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "error" or self.debug_level >= 1:
            if level == "error":
                print(f"[{timestamp}] {Colors.colorize(f'ERROR: {message}', Colors.BOLD_RED)}")
            elif level == "success":
                print(f"[{timestamp}] {Colors.colorize(message, Colors.BOLD_GREEN)}")
            elif level == "debug" and self.debug_level >= 1:
                print(f"[{timestamp}] {Colors.colorize(f'DEBUG: {message}', Colors.CYAN)}")
            else:
                print(f"[{timestamp}] {Colors.colorize(message, Colors.YELLOW)}")
    
    def start_server(self) -> None:
        """
        Start the chat server
        """
        try:
            # Create and configure server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to port and start listening
            self.server_socket.bind(('', self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.log(f"Chat server started on port {self.port}", "success")
            self.log(f"Debug level: {self.debug_level} ({'All Events' if self.debug_level == 1 else 'Errors Only'})", "info")
            self.log("Waiting for client connections...", "info")
            
            # Start inactivity timer
            self.reset_inactivity_timer()
            
            # Start accepting client connections
            self.accept_clients()
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                self.log(f"Port {self.port} is already in use. Try a different port.", "error")
            else:
                self.log(f"Failed to start server: {e}", "error")
            sys.exit(1)
        except Exception as e:
            self.log(f"Server startup error: {e}", "error")
            sys.exit(1)
    
    def accept_clients(self) -> None:
        """
        Accept incoming client connections
        """
        while self.running:
            try:
                # Use select to check for incoming connections with timeout
                ready, _, _ = select.select([self.server_socket], [], [], 1.0)
                
                if ready:
                    client_socket, address = self.server_socket.accept()
                    self.log(f"New connection from {address[0]}:{address[1]}", "debug")
                    
                    # Create client info
                    client_info = ClientInfo(
                        socket=client_socket,
                        address=address
                    )
                    
                    with self.lock:
                        self.clients[client_socket] = client_info
                        self.last_activity = time.time()
                        self.reset_inactivity_timer()
                    
                    # Handle client in separate thread (Stage 3) or same thread (Stages 1-2)
                    if self.active_threads < self.max_threads:
                        # Stage 3: Multi-threaded
                        client_thread = threading.Thread(
                            target=self.handle_client_thread,
                            args=(client_socket,),
                            daemon=True
                        )
                        client_thread.start()
                        with self.lock:
                            self.active_threads += 1
                    else:
                        # Stages 1-2: Single-threaded or thread limit reached
                        self.handle_client(client_socket)
                        
            except OSError:
                if self.running:
                    self.log("Error accepting connections", "error")
                break
            except Exception as e:
                if self.running:
                    self.log(f"Error in accept_clients: {e}", "error")
    
    def handle_client_thread(self, client_socket: socket.socket) -> None:
        """
        Handle client in separate thread (Stage 3)
        
        Args:
            client_socket: Socket for client communication
        """
        try:
            self.handle_client(client_socket)
        finally:
            with self.lock:
                self.active_threads -= 1
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle communication with a single client
        
        Args:
            client_socket: Socket for client communication
        """
        buffer = ""
        
        try:
            while self.running:
                # Set socket timeout for non-blocking behavior
                client_socket.settimeout(1.0)
                
                try:
                    # Receive data from client
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        # Client disconnected
                        break
                    
                    buffer += data
                    
                    # Process complete messages (separated by newlines)
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            self.process_client_message(client_socket, line.strip())
                            
                            # Update activity
                            with self.lock:
                                if client_socket in self.clients:
                                    self.clients[client_socket].last_activity = time.time()
                                self.last_activity = time.time()
                                self.reset_inactivity_timer()
                
                except socket.timeout:
                    continue  # Keep trying
                except Exception as e:
                    self.log(f"Error receiving from client: {e}", "error")
                    break
                    
        except Exception as e:
            self.log(f"Error handling client: {e}", "error")
        finally:
            self.disconnect_client(client_socket)
    
    def process_client_message(self, client_socket: socket.socket, message: str) -> None:
        """
        Process a message from a client
        
        Args:
            client_socket: Client socket
            message: Raw message from client
        """
        try:
            # Try to parse as JSON
            data = json.loads(message)
            
            if data.get("type") == "command":
                command = data.get("command", "")
                nickname = data.get("nickname", "")
                
                # Update client nickname if provided
                with self.lock:
                    if client_socket in self.clients and nickname:
                        self.clients[client_socket].nickname = nickname
                
                self.process_command(client_socket, command)
                
        except json.JSONDecodeError:
            # Not JSON, treat as plain text command
            self.process_command(client_socket, message)
    
    def process_command(self, client_socket: socket.socket, command: str) -> None:
        """
        Process IRC-style commands from clients
        
        Args:
            client_socket: Socket of the client who sent the command
            command: Command string to process
        """
        with self.lock:
            if client_socket not in self.clients:
                return
            
            client_info = self.clients[client_socket]
        
        # Parse command
        if command.startswith("/"):
            parts = command[1:].split()
            if not parts:
                return
            
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            self.log(f"Processing command: {cmd} from {client_info.nickname or 'unknown'}", "debug")
            
            if cmd == "nick":
                self.handle_nick_command(client_socket, args)
            elif cmd == "list":
                self.handle_list_command(client_socket)
            elif cmd == "join":
                self.handle_join_command(client_socket, args)
            elif cmd == "leave":
                self.handle_leave_command(client_socket, args)
            elif cmd == "quit":
                self.handle_quit_command(client_socket)
            elif cmd == "help":
                self.handle_help_command(client_socket)
            else:
                self.send_error(client_socket, f"Unknown command: /{cmd}")
        else:
            # Regular chat message
            self.handle_chat_message(client_socket, command)
    
    def handle_nick_command(self, client_socket: socket.socket, args: List[str]) -> None:
        """Handle /nick command"""
        if not args:
            self.send_error(client_socket, "Usage: /nick <nickname>")
            return
        
        new_nick = args[0]
        if len(new_nick) > 32:
            self.send_error(client_socket, "Nickname too long (max 32 characters)")
            return
        
        # Check if nickname is already in use
        with self.lock:
            for other_socket, other_client in self.clients.items():
                if other_socket != client_socket and other_client.nickname == new_nick:
                    self.send_error(client_socket, f"Nickname '{new_nick}' is already in use")
                    return
            
            # Set nickname
            old_nick = self.clients[client_socket].nickname
            self.clients[client_socket].nickname = new_nick
        
        self.send_success(client_socket, f"Nickname set to '{new_nick}'")
        self.log(f"Client {client_socket.getpeername()} set nickname to '{new_nick}'", "debug")
        
        # If client was in channels, notify others of nickname change
        if old_nick:
            for channel in self.clients[client_socket].channels:
                self.broadcast_to_channel(
                    {
                        "type": "event",
                        "event": "nick_change",
                        "old_nickname": old_nick,
                        "new_nickname": new_nick,
                        "channel": channel
                    },
                    channel,
                    exclude=client_socket
                )
    
    def handle_list_command(self, client_socket: socket.socket) -> None:
        """Handle /list command"""
        with self.lock:
            channel_list = []
            for channel_name, users in self.channels.items():
                channel_list.append({
                    "name": channel_name,
                    "users": len(users)
                })
        
        self.send_response(client_socket, {
            "type": "event",
            "event": "channel_list",
            "channels": channel_list
        })
    
    def handle_join_command(self, client_socket: socket.socket, args: List[str]) -> None:
        """Handle /join command"""
        if not args:
            # Join default channel
            channel = self.default_channel
        else:
            channel = args[0]
            if not channel.startswith("#"):
                channel = "#" + channel
        
        with self.lock:
            client_info = self.clients[client_socket]
            
            # Check if already in channel
            if channel in client_info.channels:
                self.send_error(client_socket, f"You are already in {channel}")
                return
            
            # Add to channel
            if channel not in self.channels:
                self.channels[channel] = set()
            
            self.channels[channel].add(client_socket)
            client_info.channels.add(channel)
        
        self.send_success(client_socket, f"Joined channel {channel}")
        
        # Notify others in channel
        self.broadcast_to_channel(
            {
                "type": "event",
                "event": "user_joined",
                "nickname": client_info.nickname or "Unknown",
                "channel": channel
            },
            channel,
            exclude=client_socket
        )
        
        self.log(f"{client_info.nickname or 'Unknown'} joined {channel}", "debug")
    
    def handle_leave_command(self, client_socket: socket.socket, args: List[str]) -> None:
        """Handle /leave command"""
        with self.lock:
            client_info = self.clients[client_socket]
            
            if args:
                channel = args[0]
                if not channel.startswith("#"):
                    channel = "#" + channel
            else:
                # Leave all channels
                channels_to_leave = list(client_info.channels)
                for ch in channels_to_leave:
                    self.remove_user_from_channel(client_socket, ch)
                return
            
            if channel not in client_info.channels:
                self.send_error(client_socket, f"You are not in {channel}")
                return
            
            self.remove_user_from_channel(client_socket, channel)
    
    def handle_quit_command(self, client_socket: socket.socket) -> None:
        """Handle /quit command"""
        self.send_success(client_socket, "Goodbye!")
        self.disconnect_client(client_socket)
    
    def handle_help_command(self, client_socket: socket.socket) -> None:
        """Handle /help command"""
        help_text = """
=== CHAT SERVER HELP ===

Available Commands:
  /nick <nickname>     - Set your nickname
  /list                - List all channels and user counts
  /join [<channel>]    - Join a channel (default: #general)
  /leave [<channel>]   - Leave channel (or all channels if none specified)
  /quit                - Disconnect from server
  /help                - Show this help message

Examples:
  /nick alice          - Set nickname to 'alice'
  /join #general       - Join #general channel
  /join programming    - Join #programming channel (# added automatically)
  /leave #general      - Leave #general channel
  /leave               - Leave all channels
  Hello everyone!      - Send message to current channels

Tips:
  - Set a nickname before joining channels
  - You can be in multiple channels at once
  - Regular messages (without /) are sent to all your channels
        """
        
        self.send_response(client_socket, {
            "type": "response",
            "success": True,
            "message": help_text
        })
    
    def handle_chat_message(self, client_socket: socket.socket, message: str) -> None:
        """Handle regular chat message"""
        with self.lock:
            if client_socket not in self.clients:
                return
            
            client_info = self.clients[client_socket]
            
            if not client_info.nickname:
                self.send_error(client_socket, "Please set a nickname first with /nick <nickname>")
                return
            
            if not client_info.channels:
                self.send_error(client_socket, "Please join a channel first with /join <channel>")
                return
            
            # Broadcast message to all channels the user is in
            for channel in client_info.channels:
                self.broadcast_to_channel(
                    {
                        "type": "event",
                        "event": "message",
                        "nickname": client_info.nickname,
                        "channel": channel,
                        "message": message,
                        "timestamp": time.time()
                    },
                    channel,
                    exclude=client_socket
                )
        
        self.log(f"Message from {client_info.nickname}: {message}", "debug")
    
    def broadcast_to_channel(self, message: dict, channel: str, exclude: socket.socket = None) -> None:
        """
        Broadcast message to all users in a channel
        
        Args:
            message: Message dictionary to broadcast
            channel: Channel name
            exclude: Socket to exclude from broadcast
        """
        with self.lock:
            if channel not in self.channels:
                return
            
            message_json = json.dumps(message) + "\n"
            disconnected_clients = []
            
            for client_socket in self.channels[channel]:
                if client_socket == exclude:
                    continue
                
                try:
                    client_socket.send(message_json.encode('utf-8'))
                except:
                    # Client disconnected, mark for removal
                    disconnected_clients.append(client_socket)
            
            # Remove disconnected clients
            for client_socket in disconnected_clients:
                self.disconnect_client(client_socket)
    
    def remove_user_from_channel(self, client_socket: socket.socket, channel: str) -> None:
        """
        Remove user from a channel
        
        Args:
            client_socket: Client socket
            channel: Channel name
        """
        with self.lock:
            if client_socket not in self.clients:
                return
            
            client_info = self.clients[client_socket]
            
            if channel in client_info.channels:
                client_info.channels.remove(channel)
            
            if channel in self.channels and client_socket in self.channels[channel]:
                self.channels[channel].remove(client_socket)
                
                # Delete empty channels (except default)
                if len(self.channels[channel]) == 0 and channel != self.default_channel:
                    del self.channels[channel]
        
        self.send_success(client_socket, f"Left channel {channel}")
        
        # Notify others in channel
        self.broadcast_to_channel(
            {
                "type": "event",
                "event": "user_left",
                "nickname": client_info.nickname or "Unknown",
                "channel": channel
            },
            channel
        )
        
        self.log(f"{client_info.nickname or 'Unknown'} left {channel}", "debug")
    
    def disconnect_client(self, client_socket: socket.socket) -> None:
        """
        Disconnect a client and clean up
        
        Args:
            client_socket: Client socket to disconnect
        """
        with self.lock:
            if client_socket not in self.clients:
                return
            
            client_info = self.clients[client_socket]
            
            # Remove from all channels
            for channel in list(client_info.channels):
                self.remove_user_from_channel(client_socket, channel)
            
            # Close socket
            try:
                client_socket.close()
            except:
                pass
            
            # Remove from clients
            del self.clients[client_socket]
            
            self.log(f"Client {client_info.nickname or 'unknown'} disconnected", "debug")
    
    def send_response(self, client_socket: socket.socket, response: dict) -> None:
        """Send response to client"""
        try:
            response_json = json.dumps(response) + "\n"
            client_socket.send(response_json.encode('utf-8'))
        except:
            self.disconnect_client(client_socket)
    
    def send_success(self, client_socket: socket.socket, message: str) -> None:
        """Send success response to client"""
        self.send_response(client_socket, {
            "type": "response",
            "success": True,
            "message": message
        })
    
    def send_error(self, client_socket: socket.socket, message: str) -> None:
        """Send error response to client"""
        self.send_response(client_socket, {
            "type": "response",
            "success": False,
            "message": message
        })
    
    def reset_inactivity_timer(self) -> None:
        """Reset the 3-minute inactivity timer"""
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
        
        self.inactivity_timer = threading.Timer(180.0, self.check_inactivity)  # 3 minutes
        self.inactivity_timer.start()
    
    def check_inactivity(self) -> None:
        """Check for server inactivity and shutdown if needed"""
        with self.lock:
            if len(self.clients) == 0:
                self.log("No clients connected for 3 minutes. Shutting down server.", "info")
                self.graceful_shutdown()
            else:
                # Reset timer if there are still clients
                self.reset_inactivity_timer()
    
    def signal_handler(self, signum, frame) -> None:
        """Handle Ctrl-C for graceful shutdown (extra credit)"""
        self.log("\nReceived shutdown signal. Shutting down gracefully...", "info")
        self.graceful_shutdown()
    
    def graceful_shutdown(self) -> None:
        """
        Gracefully shutdown the server
        """
        self.running = False
        
        # Cancel inactivity timer
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
        
        # Notify all connected clients
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    self.send_response(client_socket, {
                        "type": "response",
                        "success": True,
                        "message": "Server is shutting down. Goodbye!"
                    })
                except:
                    pass
                self.disconnect_client(client_socket)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.log("Server shutdown complete.", "success")
        sys.exit(0)
