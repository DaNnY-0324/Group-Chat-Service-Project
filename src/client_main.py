#!/usr/bin/env python3
"""client_main.py - Entry point for ChatClient application

CSC4220: Computer Networks - Chat Server Project
Team: Danny Nguyen, David Salas, Romeo Henderson
File Created by Danny Nguyen
"""

import sys
import signal
from chat_client import ChatClient

# Simple color codes (since utils.py might not be ready yet)
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


def display_welcome():
    """
    Display welcome message and instructions
    """
    print(Colors.colorize("=" * 60, Colors.BOLD_CYAN))
    print(Colors.colorize("CSC4220 Chat Client", Colors.BOLD_CYAN))
    print(Colors.colorize("Team: Danny Nguyen, David Salas, Romeo Henderson", Colors.CYAN))
    print(Colors.colorize("=" * 60, Colors.BOLD_CYAN))
    print()
    print(Colors.colorize("Available Commands:", Colors.BOLD_YELLOW))
    print("  /connect <server> [port]  - Connect to chat server")
    print("  /nick <nickname>          - Set your nickname")
    print("  /list                     - List available channels")
    print("  /join <channel>           - Join a channel")
    print("  /leave [channel]          - Leave current or specified channel")
    print("  /quit                     - Quit the chat client")
    print("  /help                     - Show this help message")
    print()
    print(Colors.colorize("To get started, use: /connect localhost 8080", Colors.BOLD_GREEN))
    print(Colors.colorize("=" * 60, Colors.BOLD_CYAN))
    print()


def display_help():
    """
    Display detailed help information
    """
    print(Colors.colorize("\n=== DETAILED HELP ===", Colors.BOLD_YELLOW))
    print()
    print(Colors.colorize("Connection Process:", Colors.BOLD_GREEN))
    print("1. Start the client: python src/client_main.py")
    print("2. Connect to server: /connect <server> [port]")
    print("3. Set your nickname: /nick <your_nickname>")
    print("4. Join a channel: /join #general")
    print("5. Start chatting!")
    print()
    print(Colors.colorize("Command Examples:", Colors.BOLD_GREEN))
    print("  /connect localhost 8080   - Connect to local server")
    print("  /connect 192.168.1.100    - Connect to remote server (default port 8080)")
    print("  /nick danny123            - Set nickname to 'danny123'")
    print("  /join #general            - Join the #general channel")
    print("  /join programming         - Join #programming (# added automatically)")
    print("  /leave                    - Leave current channel")
    print("  /leave #general           - Leave specific channel")
    print("  /list                     - Show all channels and user counts")
    print()
    print(Colors.colorize("Tips:", Colors.BOLD_GREEN))
    print("  - Channel names starting with # are recommended")
    print("  - Nicknames must be unique on the server")
    print("  - Use Ctrl+C to quit gracefully")
    print("  - Type regular messages (no /) to chat in current channel")
    print()


def setup_signal_handlers(client_instance):
    """
    Set up signal handlers for graceful shutdown
    
    Args:
        client_instance: Client instance to shutdown
    """
    def signal_handler(signum, frame):
        print(Colors.colorize("\n\nGracefully shutting down client...", Colors.YELLOW))
        if client_instance and hasattr(client_instance, 'disconnect'):
            try:
                client_instance.disconnect()
            except:
                pass  # Ignore errors during shutdown
        print(Colors.colorize("Client shutdown complete. Goodbye!", Colors.GREEN))
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """
    Main entry point for chat client
    """
    client = None
    try:
        # Display welcome message
        display_welcome()
        
        # Create client instance
        client = ChatClient()
        
        # Set up signal handlers for graceful shutdown (extra credit)
        setup_signal_handlers(client)
        
        # Start client main loop
        client.run()
        
    except KeyboardInterrupt:
        print(Colors.colorize("\nClient shutting down...", Colors.YELLOW))
        if client and hasattr(client, 'disconnect'):
            try:
                client.disconnect()
            except:
                pass
        sys.exit(0)
    except Exception as e:
        print(Colors.colorize(f"Error running client: {e}", Colors.RED))
        print(Colors.colorize("\nTroubleshooting:", Colors.BOLD_YELLOW))
        print("1. Make sure the server is running first")
        print("2. Check if the server port is correct")
        print("3. Verify network connectivity")
        print("4. Try running: python src/server_main.py -p 8080 -d 1")
        sys.exit(1)


if __name__ == "__main__":
    main()
