#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT WebSocket Client - Pure WebSocket-based client without browser automation
"""

import websocket
import json
import time
import re
from typing import Optional, Callable


class PTTWebSocketClient:
    """Pure WebSocket client for PTT terminal"""

    def __init__(self, debug: bool = False):
        """
        Initialize PTT WebSocket client

        Args:
            debug: Enable debug output
        """
        self.ws = None
        self.debug = debug
        self.buffer = ""
        # PTT WebSocket endpoint
        self.url = "wss://ws.ptt.cc/bbs"

    def connect(self):
        """Establish WebSocket connection to PTT"""
        if self.debug:
            print(f"Connecting to {self.url}...")

        try:
            # Set required headers for PTT WebSocket (must use list format)
            headers = [
                'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Origin: https://term.ptt.cc'
            ]

            self.ws = websocket.create_connection(
                self.url,
                header=headers
            )

            if self.debug:
                print("Connected successfully")

        except Exception as e:
            if self.debug:
                print(f"Connection error: {e}")
            raise

    def send(self, text: str):
        """
        Send text to PTT terminal

        Args:
            text: Text to send (will append \\r for Enter key)
        """
        if self.debug:
            print(f"Sending: {repr(text)}")

        self.ws.send(text)

    def send_command(self, command: str):
        """
        Send command with Enter key

        Args:
            command: Command to send
        """
        self.send(command + "\r")

    def receive(self, timeout: float = 5.0) -> str:
        """
        Receive data from WebSocket

        Args:
            timeout: Timeout in seconds

        Returns:
            Received text data
        """
        self.ws.settimeout(timeout)
        try:
            data = self.ws.recv()
            if isinstance(data, bytes):
                # Try to decode as UTF-8
                text = data.decode('utf-8', errors='ignore')
            else:
                text = data

            self.buffer += text

            if self.debug:
                print(f"Received: {repr(text[:100])}...")

            return text
        except websocket.WebSocketTimeoutException:
            return ""

    def wait_for_text(self, pattern: str, timeout: float = 10.0, clear_buffer: bool = False) -> bool:
        """
        Wait for specific text pattern to appear

        Args:
            pattern: Text pattern to wait for
            timeout: Maximum wait time in seconds
            clear_buffer: Clear buffer before waiting

        Returns:
            True if pattern found, False if timeout
        """
        if clear_buffer:
            self.buffer = ""

        start_time = time.time()

        while time.time() - start_time < timeout:
            self.receive(timeout=1.0)

            if pattern in self.buffer:
                if self.debug:
                    print(f"Found pattern: {pattern}")
                return True

        if self.debug:
            print(f"Pattern not found: {pattern}")
            print(f"Buffer content: {self.buffer[-500:]}")

        return False

    def login(self, username: str, password: str) -> bool:
        """
        Login to PTT

        Args:
            username: Account username
            password: Account password

        Returns:
            True if login successful
        """
        try:
            # Wait for login prompt
            if not self.wait_for_text("請輸入代號", timeout=10, clear_buffer=True):
                print("Failed to find login prompt")
                return False

            # Send username
            print(f"Logging in as: {username}")
            self.send_command(username)
            time.sleep(1)

            # Wait for password prompt
            if not self.wait_for_text("請輸入您的密碼"):
                print("Failed to find password prompt")
                return False

            # Send password
            self.send_command(password)
            time.sleep(2)

            # Check for duplicate login
            if "重複登入" in self.buffer or "刪除其他" in self.buffer:
                print("Duplicate login detected, kicking old session...")
                self.send_command("y")
                time.sleep(2)

            # Wait for welcome message
            if not self.wait_for_text("歡迎"):
                print("Failed to find welcome message")
                return False

            # Press any key to continue
            print("Pressing Enter to continue...")
            self.send_command("")
            time.sleep(2)

            # Check for main menu
            if self.wait_for_text("主功能表"):
                print("Login successful! Reached main menu.")
                return True

            return False

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def navigate_to_board(self, board_path: list) -> bool:
        """
        Navigate to a specific board using menu selections

        Args:
            board_path: List of selections to reach the board
                       e.g., ['c', '13', '1'] for Gossiping

        Returns:
            True if navigation successful
        """
        try:
            for i, selection in enumerate(board_path):
                print(f"Navigating step {i+1}: {selection}")

                # Clear buffer before sending command
                self.buffer = ""

                # Send selection
                self.send_command(selection)
                time.sleep(2)

                # Wait for response
                self.receive(timeout=2.0)

                if self.debug:
                    print(f"Current buffer: {self.buffer[-200:]}")

            return True

        except Exception as e:
            print(f"Navigation failed: {e}")
            return False

    def get_current_screen(self) -> str:
        """
        Get current screen content

        Returns:
            Current buffer content
        """
        # Receive any pending data
        self.receive(timeout=1.0)
        return self.buffer

    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            if self.debug:
                print("Connection closed")


def main():
    """Main function to test PTT WebSocket client"""
    # Load credentials
    with open('my_private_password.json', 'r') as f:
        credentials = json.load(f)

    # Create client
    client = PTTWebSocketClient(debug=True)

    try:
        # Connect to PTT
        client.connect()

        # Login
        if client.login(credentials['account'], credentials['password']):
            print("\n" + "="*60)
            print("LOGIN SUCCESSFUL - NOW IN MAIN MENU")
            print("="*60)

            # Navigate to Gossiping board
            print("\nNavigating to Gossiping board...")
            print("Path: (C) 分組討論區 -> 13 熱門即時看板 -> 1 Gossiping")

            board_path = ['c', '13', '1']
            if client.navigate_to_board(board_path):
                print("\n" + "="*60)
                print("NAVIGATION SUCCESSFUL")
                print("="*60)

                # Get current screen
                time.sleep(2)
                screen = client.get_current_screen()
                print("\nCurrent screen content (last 1000 chars):")
                print(screen[-1000:])
            else:
                print("Navigation failed")
        else:
            print("Login failed")

    finally:
        # Close connection
        client.close()


if __name__ == '__main__':
    main()
