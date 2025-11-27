#!/usr/bin/env python3
"""server_main.py - Entry point for ChatServer application

This module provides the main entry point for the chat server with command line
argument parsing, logging setup, and graceful shutdown handling.
"""

import sys
import os
import time

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_server import ChatServer
from utils import (
    Logger, Colors, parse_server_args, validate_server_args,
    setup_signal_handlers, create_banner, get_local_ip
)


def display_startup_banner(port: int, debug_level: int, local_ip: str):
    """Display colorful startup banner"""
    banner = create_banner("CSC4220 CHAT SERVER", "Multi-threaded IRC-style Server")
    
    print(Colors.cyan(banner, bold=True))
    print()
    print(Colors.green("🚀 Server Configuration:", bold=True))
    print(f"   • Port: {Colors.yellow(str(port), bold=True)}")
    print(f"   • Debug Level: {Colors.yellow(str(debug_level), bold=True)} ({'All Events' if debug_level == 1 else 'Errors Only'})")
    print(f"   • Local IP: {Colors.yellow(local_ip, bold=True)}")
    print(f"   • Max Threads: {Colors.yellow('4', bold=True)}")
    print()
    print(Colors.blue("📋 Supported Commands:", bold=True))
    print("   • /connect <server> [port] - Connect to server")
    print("   • /nick <nickname>        - Set nickname")
    print("   • /join <channel>         - Join channel")
    print("   • /leave [channel]        - Leave channel")
    print("   • /list                   - List channels")
    print("   • /quit                   - Disconnect")
    print("   • /help                   - Show help")
    print()
    print(Colors.magenta("🎯 Features Enabled:", bold=True))
    print("   • Multi-channel support")
    print("   • Multi-threading (max 4 concurrent)")
    print("   • 3-minute idle timeout")
    print("   • Colored terminal output")
    print("   • Graceful Ctrl-C shutdown")
    print("   • Enhanced logging system")
    print()


def main():
    """Main entry point for the chat server"""
    try:
        # Parse command line arguments
        args = parse_server_args()
        
        # Validate arguments
        is_valid, error_msg = validate_server_args(args)
        if not is_valid:
            print(Colors.red(f"❌ Error: {error_msg}", bold=True))
            sys.exit(1)
        
        # Create logger with specified debug level
        logger = Logger(debug_level=args.debug, use_colors=True)
        
        # Get local IP for display
        local_ip = get_local_ip()
        
        # Display startup banner
        display_startup_banner(args.port, args.debug, local_ip)
        
        # Create chat server instance
        logger.info(f"Initializing ChatServer on port {args.port}")
        server = ChatServer(port=args.port, debug_level=args.debug)
        
        # Setup signal handlers for graceful shutdown
        def shutdown_handler():
            logger.info("Shutdown signal received")
            server.graceful_shutdown()
        
        setup_signal_handlers(shutdown_handler)
        
        # Start the server
        print(Colors.green("🔥 Starting server...", bold=True))
        print(Colors.cyan(f"📡 Listening on {local_ip}:{args.port}"))
        print(Colors.yellow("Press Ctrl+C to shutdown gracefully"))
        print("=" * 60)
        print()
        
        logger.success(f"ChatServer started successfully on port {args.port}")
        server.start_server()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.yellow('🛑 Keyboard interrupt received. Shutting down...')}")
        if 'server' in locals():
            server.graceful_shutdown()
        sys.exit(0)
        
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(Colors.red(f"❌ Error: Port {args.port} is already in use!", bold=True))
            print(Colors.yellow("💡 Try a different port or stop the existing server."))
        else:
            print(Colors.red(f"❌ Network Error: {e}", bold=True))
        sys.exit(1)
        
    except Exception as e:
        print(Colors.red(f"❌ Unexpected Error: {e}", bold=True))
        print(Colors.yellow("💡 Check the logs for more details."))
        sys.exit(1)
    
    finally:
        if 'server' in locals():
            server.graceful_shutdown()
        print(Colors.green("✅ Server shutdown complete.", bold=True))


if __name__ == "__main__":
    main()
