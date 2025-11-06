"""chat_client.py - Simple text-based chat client

TODO: Implement the following functionality:

CLIENT CORE FEATURES:
- Connect to server using server name and port
- Send IRC-style commands to server using socket.send()
- Receive and display messages from server using socket.recv()
- Handle user input from terminal using input()
- Implement clean disconnect and error handling

SUPPORTED COMMANDS:
- /connect <server-name> [port#] - Connect to named server
- /nick <nickname> - Pick unique nickname
- /list - List channels and number of users
- /join <channel> - Join a channel
- /leave [<channel>] - Leave current or named channel
- /quit - Leave chat and disconnect
- /help - Print help message

EXTRA CREDIT:
- Colored terminal fonts using colorama
- Graceful shutdown with Ctrl-C using signal handling

TASKS TO IMPLEMENT:
1. Create ChatClient class with initialization method
2. Implement connect_to_server() method
3. Implement send_command() method
4. Implement receive_messages() method (runs in separate thread)
5. Implement process_user_input() method
6. Implement parse_command() method
7. Implement display_message() method with color support
8. Implement show_help() method
9. Implement disconnect() method
10. Implement run() method (main client loop)
11. Add signal handler for Ctrl-C (extra credit)
"""
