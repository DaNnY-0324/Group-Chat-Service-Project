#!/usr/bin/env python3
"""client_main.py - Entry point for ChatClient application

TODO: Implement the following functionality:

CLIENT INITIALIZATION:
- Create ChatClient instance
- Display welcome message and instructions
- Set up input/output handling

USER INTERACTION:
- Handle user input from terminal
- Process IRC commands
- Display server responses
- Manage connection state

CONNECTION MANAGEMENT:
- Handle connection failures
- Manage disconnections
- Provide connection status feedback

EXTRA CREDIT:
- Signal handling for Ctrl-C (graceful shutdown)
- Colored output support

TASKS TO IMPLEMENT:
1. Import required modules (sys, signal, chat_client, utils)
2. Implement display_welcome() function:
   - Show colored application title and team information
   - Display all available IRC commands with descriptions
   - Show connection instructions
   - Use Colors class for attractive formatting
3. Implement display_help() function:
   - Show detailed command syntax and examples
   - Explain connection process step-by-step
   - Provide usage tips and troubleshooting
4. Implement setup_signal_handlers() function:
   - Handle SIGINT (Ctrl-C) signal
   - Call client.disconnect() for graceful shutdown
   - Display shutdown message with colors
5. Implement main() function:
   - Display welcome message
   - Create ChatClient instance
   - Set up signal handlers for graceful shutdown
   - Start client.run() main loop
   - Handle KeyboardInterrupt and other exceptions
6. Add if __name__ == "__main__": guard and call main()
"""
