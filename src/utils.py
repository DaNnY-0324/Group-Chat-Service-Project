"""utils.py - Utility functions and helper classes

This module provides utility functions and helper classes for the chat server system.
Includes logging, networking, threading, and validation utilities.
"""

import socket
import threading
import time
import signal
import sys
import argparse
from datetime import datetime
from typing import Optional, Callable, Any, Tuple
from queue import Queue, Empty


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """Apply color formatting to text"""
        prefix = cls.BOLD if bold else ""
        return f"{prefix}{color}{text}{cls.RESET}"
    
    @classmethod
    def red(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.RED, bold)
    
    @classmethod
    def green(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.GREEN, bold)
    
    @classmethod
    def yellow(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.YELLOW, bold)
    
    @classmethod
    def blue(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.BLUE, bold)
    
    @classmethod
    def cyan(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.CYAN, bold)
    
    @classmethod
    def magenta(cls, text: str, bold: bool = False) -> str:
        return cls.colorize(text, cls.MAGENTA, bold)


class Logger:
    """Logger class with debug levels and color support"""
    
    def __init__(self, debug_level: int = 0, use_colors: bool = True):
        """
        Initialize logger
        
        Args:
            debug_level: 0 = errors only, 1 = all events
            use_colors: Whether to use colored output
        """
        self.debug_level = debug_level
        self.use_colors = use_colors
        self._lock = threading.Lock()
    
    def _format_timestamp(self) -> str:
        """Format current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log(self, level: str, message: str, color_func: Optional[Callable] = None):
        """Internal logging method with thread safety"""
        with self._lock:
            timestamp = self._format_timestamp()
            formatted_msg = f"[{timestamp}] [{level}] {message}"
            
            if self.use_colors and color_func:
                formatted_msg = color_func(formatted_msg)
            
            print(formatted_msg)
    
    def error(self, message: str):
        """Log error message (always shown)"""
        self._log("ERROR", message, Colors.red if self.use_colors else None)
    
    def info(self, message: str):
        """Log info message (debug level 1 only)"""
        if self.debug_level >= 1:
            self._log("INFO", message, Colors.cyan if self.use_colors else None)
    
    def debug(self, message: str):
        """Log debug message (debug level 1 only)"""
        if self.debug_level >= 1:
            self._log("DEBUG", message, Colors.yellow if self.use_colors else None)
    
    def success(self, message: str):
        """Log success message"""
        self._log("SUCCESS", message, Colors.green if self.use_colors else None)
    
    def warning(self, message: str):
        """Log warning message"""
        self._log("WARNING", message, Colors.yellow if self.use_colors else None)


class ThreadPool:
    """Thread pool for managing concurrent connections"""
    
    def __init__(self, max_threads: int = 4):
        """Initialize thread pool with maximum thread count"""
        self.max_threads = max_threads
        self.threads = []
        self.task_queue = Queue()
        self.shutdown_flag = threading.Event()
        self.active_tasks = 0
        self._lock = threading.Lock()
        
        # Start worker threads
        for i in range(max_threads):
            thread = threading.Thread(target=self._worker_thread, name=f"Worker-{i}")
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
    
    def submit_task(self, func: Callable, *args, **kwargs) -> bool:
        """Submit a task to the thread pool"""
        if self.shutdown_flag.is_set():
            return False
        
        try:
            self.task_queue.put((func, args, kwargs), timeout=1.0)
            with self._lock:
                self.active_tasks += 1
            return True
        except:
            return False
    
    def _worker_thread(self):
        """Worker thread main loop"""
        while not self.shutdown_flag.is_set():
            try:
                # Get task with timeout
                task_data = self.task_queue.get(timeout=1.0)
                if task_data is None:  # Shutdown signal
                    break
                
                func, args, kwargs = task_data
                
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"Task execution error: {e}")
                finally:
                    with self._lock:
                        self.active_tasks -= 1
                    self.task_queue.task_done()
                    
            except Empty:
                continue  # Timeout, check shutdown flag
    
    def shutdown(self, timeout: float = 5.0):
        """Shutdown the thread pool gracefully"""
        self.shutdown_flag.set()
        
        # Add shutdown signals to queue
        for _ in self.threads:
            self.task_queue.put(None)
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=timeout)
    
    def get_active_task_count(self) -> int:
        """Get number of currently active tasks"""
        with self._lock:
            return self.active_tasks


class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def create_server_socket(port: int, host: str = 'localhost') -> socket.socket:
        """Create and configure a server socket"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        return server_socket
    
    @staticmethod
    def create_client_socket() -> socket.socket:
        """Create a client socket"""
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    @staticmethod
    def send_message(sock: socket.socket, message: str) -> bool:
        """Send a message through socket with length prefix"""
        try:
            # Encode message
            encoded_msg = message.encode('utf-8')
            msg_length = len(encoded_msg)
            
            # Send length prefix (4 bytes) followed by message
            length_prefix = msg_length.to_bytes(4, byteorder='big')
            sock.sendall(length_prefix + encoded_msg)
            return True
        except Exception:
            return False
    
    @staticmethod
    def receive_message(sock: socket.socket, timeout: Optional[float] = None) -> Optional[str]:
        """Receive a message from socket with length prefix"""
        try:
            if timeout:
                sock.settimeout(timeout)
            
            # Receive length prefix (4 bytes)
            length_data = b''
            while len(length_data) < 4:
                chunk = sock.recv(4 - len(length_data))
                if not chunk:
                    return None
                length_data += chunk
            
            # Decode message length
            msg_length = int.from_bytes(length_data, byteorder='big')
            
            # Receive message data
            message_data = b''
            while len(message_data) < msg_length:
                chunk = sock.recv(msg_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return message_data.decode('utf-8')
        except Exception:
            return None
        finally:
            if timeout:
                sock.settimeout(None)


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number range"""
        return 1024 <= port <= 65535
    
    @staticmethod
    def validate_nickname(nickname: str) -> bool:
        """Validate nickname format"""
        if not nickname or len(nickname) > 16:
            return False
        return nickname.replace('_', '').isalnum() and nickname[0].isalpha()
    
    @staticmethod
    def validate_channel_name(channel: str) -> bool:
        """Validate channel name format"""
        if not channel or len(channel) > 32:
            return False
        if not channel.startswith('#'):
            return False
        return channel[1:].replace('_', '').replace('-', '').isalnum()
    
    @staticmethod
    def validate_server_address(address: str) -> bool:
        """Validate server address format"""
        if not address:
            return False
        
        # Check if it's a valid hostname or IP
        try:
            socket.gethostbyname(address)
            return True
        except socket.gaierror:
            return False


# Utility Functions

def setup_signal_handlers(shutdown_callback: Callable):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n{Colors.yellow('Received shutdown signal. Shutting down gracefully...')}")
        shutdown_callback()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """Format timestamp for consistent display"""
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_server_args() -> argparse.Namespace:
    """Parse command line arguments for server"""
    parser = argparse.ArgumentParser(
        description="Multi-threaded Chat Server",
        epilog="""
Examples:
  python server_main.py -p 8080
  python server_main.py -p 9000 -d 1
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Port number to bind server (1024-65535)'
    )
    
    parser.add_argument(
        '-d', '--debug',
        type=int,
        choices=[0, 1],
        default=0,
        help='Debug level: 0=errors only, 1=all events (default: 0)'
    )
    
    return parser.parse_args()


def validate_server_args(args: argparse.Namespace) -> Tuple[bool, str]:
    """Validate parsed server arguments"""
    if not InputValidator.validate_port(args.port):
        return False, f"Invalid port number: {args.port}. Must be between 1024-65535."
    
    if args.debug not in [0, 1]:
        return False, f"Invalid debug level: {args.debug}. Must be 0 or 1."
    
    return True, "Arguments are valid."


def get_local_ip() -> str:
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def create_banner(title: str, subtitle: str = "", width: int = 60) -> str:
    """Create a formatted banner for display"""
    lines = []
    lines.append("=" * width)
    lines.append(f"{title:^{width}}")
    if subtitle:
        lines.append(f"{subtitle:^{width}}")
    lines.append("=" * width)
    return "\n".join(lines)
