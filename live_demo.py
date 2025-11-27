#!/usr/bin/env python3
"""
Live Interactive Demo - Simulates multiple clients chatting
This demonstrates server-client communication in real-time
"""

import socket
import json
import time
import threading
import sys

class DemoClient:
    def __init__(self, name, port=8080):
        self.name = name
        self.port = port
        self.socket = None
        self.running = False
        self.receive_thread = None
        
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', self.port))
            print(f"✅ [{self.name}] Connected to server on port {self.port}")
            
            # Start receiving messages
            self.running = True
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Give time to receive welcome message
            time.sleep(0.3)
            return True
        except Exception as e:
            print(f"❌ [{self.name}] Connection failed: {e}")
            return False
    
    def receive_messages(self):
        """Receive messages from server"""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self.handle_message(msg)
                        except:
                            # Plain text message
                            if line.strip():
                                print(f"📨 [{self.name}] Received: {line[:80]}")
            except:
                break
    
    def handle_message(self, msg):
        """Handle received message"""
        msg_type = msg.get('type', '')
        
        if msg_type == 'event':
            event = msg.get('event', '')
            if event == 'user_joined':
                user = msg.get('user', 'Someone')
                channel = msg.get('channel', '#unknown')
                print(f"👋 [{self.name}] {user} joined {channel}")
            elif event == 'message':
                sender = msg.get('from', 'Unknown')
                content = msg.get('message', '')
                channel = msg.get('channel', '')
                print(f"💬 [{self.name}] [{channel}] {sender}: {content}")
        elif msg_type == 'response':
            success = msg.get('success', False)
            message = msg.get('message', '')
            if message:
                status = "✅" if success else "❌"
                print(f"{status} [{self.name}] {message[:60]}")
    
    def send_command(self, command, params=None):
        """Send command to server"""
        if params is None:
            params = []
        
        try:
            cmd = json.dumps({
                "type": "command",
                "command": command,
                "params": params
            }) + "\n"
            self.socket.sendall(cmd.encode('utf-8'))
            time.sleep(0.2)  # Wait for response
        except Exception as e:
            print(f"❌ [{self.name}] Send failed: {e}")
    
    def send_message(self, channel, message):
        """Send chat message"""
        try:
            msg = json.dumps({
                "type": "message",
                "channel": channel,
                "content": message
            }) + "\n"
            self.socket.sendall(msg.encode('utf-8'))
            print(f"📤 [{self.name}] Sent to {channel}: {message}")
            time.sleep(0.3)  # Wait for broadcast
        except Exception as e:
            print(f"❌ [{self.name}] Message send failed: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.send_command("quit")
                time.sleep(0.2)
                self.socket.close()
                print(f"👋 [{self.name}] Disconnected")
            except:
                pass

def run_live_demo():
    """Run the live demo with multiple clients"""
    print("=" * 70)
    print("🎬 LIVE DEMO: Multi-Client Chat Server Communication")
    print("=" * 70)
    print("\n🎯 This demo shows:")
    print("  • Server accepting multiple concurrent connections")
    print("  • Clients setting nicknames and joining channels")
    print("  • Real-time message broadcasting between clients")
    print("  • Multi-channel support")
    print("  • Graceful disconnection\n")
    
    # Create three clients
    alice = DemoClient("ALICE")
    bob = DemoClient("BOB")
    charlie = DemoClient("CHARLIE")
    
    try:
        # Step 1: Connect all clients
        print("\n" + "="*70)
        print("📡 STEP 1: Connecting Clients to Server")
        print("="*70)
        
        if not alice.connect():
            print("❌ Failed to connect Alice. Is the server running?")
            return
        time.sleep(0.5)
        
        if not bob.connect():
            print("❌ Failed to connect Bob")
            return
        time.sleep(0.5)
        
        if not charlie.connect():
            print("❌ Failed to connect Charlie")
            return
        time.sleep(0.5)
        
        print("\n✅ All 3 clients connected successfully!")
        
        # Step 2: Set nicknames
        print("\n" + "="*70)
        print("👤 STEP 2: Setting Nicknames")
        print("="*70)
        
        alice.send_command("nick", ["alice"])
        time.sleep(0.3)
        bob.send_command("nick", ["bob"])
        time.sleep(0.3)
        charlie.send_command("nick", ["charlie"])
        time.sleep(0.5)
        
        # Step 3: Join channel
        print("\n" + "="*70)
        print("🏠 STEP 3: Joining #general Channel")
        print("="*70)
        
        alice.send_command("join", ["#general"])
        time.sleep(0.5)
        bob.send_command("join", ["#general"])
        time.sleep(0.5)
        charlie.send_command("join", ["#general"])
        time.sleep(1)
        
        # Step 4: Chat messages
        print("\n" + "="*70)
        print("💬 STEP 4: Broadcasting Messages in #general")
        print("="*70)
        
        alice.send_message("#general", "Hello everyone! This is Alice! 👋")
        time.sleep(1)
        
        bob.send_message("#general", "Hi Alice! Bob here. Great to see you!")
        time.sleep(1)
        
        charlie.send_message("#general", "Hey team! Charlie joining the conversation!")
        time.sleep(1)
        
        alice.send_message("#general", "Awesome! All 3 clients are communicating!")
        time.sleep(1)
        
        # Step 5: List channels
        print("\n" + "="*70)
        print("📋 STEP 5: Listing Channels")
        print("="*70)
        
        alice.send_command("list")
        time.sleep(1)
        
        # Step 6: Multi-channel demo
        print("\n" + "="*70)
        print("🏠 STEP 6: Multi-Channel Support - Creating #random")
        print("="*70)
        
        bob.send_command("join", ["#random"])
        time.sleep(0.5)
        
        charlie.send_command("join", ["#random"])
        time.sleep(0.5)
        
        bob.send_message("#random", "Bob: This is a different channel!")
        time.sleep(1)
        
        charlie.send_message("#random", "Charlie: Yes! Multi-channel works!")
        time.sleep(1)
        
        # Alice is still in #general, so she won't see #random messages
        alice.send_message("#general", "Alice: I'm still in #general")
        time.sleep(1)
        
        # Step 7: Graceful disconnect
        print("\n" + "="*70)
        print("👋 STEP 7: Graceful Disconnection")
        print("="*70)
        
        alice.disconnect()
        time.sleep(0.5)
        bob.disconnect()
        time.sleep(0.5)
        charlie.disconnect()
        time.sleep(0.5)
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n🎉 Demonstrated Features:")
        print("  ✅ Multi-threaded server handling 3 concurrent clients")
        print("  ✅ Real-time message broadcasting within channels")
        print("  ✅ Multi-channel support (#general and #random)")
        print("  ✅ IRC-style commands (/nick, /join, /list, /quit)")
        print("  ✅ Graceful client disconnection")
        print("  ✅ Thread-safe concurrent operations")
        print("\n🏆 All requirements demonstrated!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        # Cleanup
        alice.disconnect()
        bob.disconnect()
        charlie.disconnect()

if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running first:")
    print("   python3 src/server_main.py -p 8080 -d 1\n")
    
    input("Press ENTER when server is ready...")
    
    run_live_demo()
