"""utils.py - Utility functions and helper classes

TODO: Define the following utility functions:

LOGGING UTILITIES:
- Logger class for debug output (levels 0=errors, 1=all events)
- Timestamp formatting functions
- Color output functions (for extra credit)

STRING UTILITIES:
- Command parsing functions
- Message formatting functions
- Input validation functions

NETWORK UTILITIES:
- Socket helper functions
- Error handling functions
- Connection validation functions

THREADING UTILITIES:
- Thread pool management (for Stage 3)
- Synchronization helpers
- Safe shutdown mechanisms

TASKS TO IMPLEMENT:
1. Create Colors class with ANSI color codes and colorize() method
2. Create Logger class with debug levels and color support
   - Implement _format_timestamp() method
   - Implement error() method (always shown)
   - Implement info() method (debug level 1 only)
   - Implement debug() method
   - Implement success() method
3. Create ThreadPool class for Stage 3 multi-threading
   - Implement submit_task() method
   - Implement _worker_thread() method
   - Implement shutdown() method
4. Create NetworkUtils class with static methods
   - Implement create_server_socket() method
   - Implement create_client_socket() method
   - Implement send_message() method
   - Implement receive_message() method
5. Create InputValidator class with static validation methods
   - Implement validate_nickname() method
   - Implement validate_channel_name() method
   - Implement validate_port() method
6. Implement utility functions:
   - setup_signal_handlers() for graceful shutdown (extra credit)
   - format_timestamp() for consistent time formatting
   - parse_command_line_args() for argument processing
"""
