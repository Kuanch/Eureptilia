#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT WebSocket Login Module - Handles automated login to PTT WebSocket terminal
"""

import json
import time
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class PTTWebSocketClient:
    """PTT WebSocket terminal client for automated login and interaction"""

    def __init__(self, headless: bool = False):
        """
        Initialize PTT WebSocket client

        Args:
            headless: Run browser in headless mode
        """
        self.driver = None
        self.headless = headless
        self.ptt_url = "https://term.ptt.cc"

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def load_credentials(self, credential_file: str) -> Dict[str, str]:
        """
        Load credentials from JSON file

        Args:
            credential_file: Path to JSON file containing account and password

        Returns:
            Dictionary with 'account' and 'password' keys
        """
        with open(credential_file, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        return credentials

    def send_keys_to_input(self, text: str, press_enter: bool = True):
        """
        Send keys to the PTT terminal input field

        Args:
            text: Text to send
            press_enter: Whether to press Enter after typing
        """
        # Use pure JavaScript approach to avoid Selenium visibility issues
        result = self.driver.execute_script("""
            var text = arguments[0];
            var pressEnter = arguments[1];

            var input = document.querySelector('input');
            if (!input) {
                return 'Input not found';
            }

            input.focus();
            input.value = text;

            // Trigger input event
            var inputEvent = new Event('input', { bubbles: true });
            input.dispatchEvent(inputEvent);

            if (pressEnter) {
                var events = [
                    new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                    new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                    new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                ];
                events.forEach(e => input.dispatchEvent(e));
            }

            return 'Success';
        """, text, press_enter)

        if result != 'Success':
            raise Exception(f"Failed to send keys: {result}")

        time.sleep(1 if press_enter else 0.5)

    def wait_for_text(self, text: str, timeout: int = 10) -> bool:
        """
        Wait for specific text to appear on page

        Args:
            text: Text to wait for
            timeout: Maximum wait time in seconds

        Returns:
            True if text appears, False if timeout
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: text in driver.page_source
            )
            return True
        except Exception as e:
            print(f"Wait for text '{text}' failed: {e}")
            return False

    def login(self, username: str, password: str) -> bool:
        """
        Perform login to PTT

        Args:
            username: PTT account username
            password: PTT account password

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Navigate to PTT
            print(f"Navigating to {self.ptt_url}...")
            self.driver.get(self.ptt_url)
            time.sleep(3)

            # Wait for login prompt
            print("Waiting for login prompt...")
            if not self.wait_for_text("請輸入代號", timeout=15):
                print("Failed to find login prompt")
                print(f"Current page source length: {len(self.driver.page_source)}")
                return False

            # Enter username
            print(f"Entering username: {username}")
            time.sleep(1)
            self.send_keys_to_input(username, press_enter=True)
            time.sleep(2)

            # Wait for password prompt
            if not self.wait_for_text("請輸入您的密碼", timeout=10):
                print("Failed to find password prompt")
                return False

            # Enter password
            print("Entering password...")
            self.send_keys_to_input(password, press_enter=True)
            time.sleep(3)

            # Wait for login response (welcome message or duplicate login prompt)
            print("Waiting for login response...")
            time.sleep(2)

            # Check if there's a duplicate login prompt
            if "重複登入" in self.driver.page_source or "您想刪除" in self.driver.page_source:
                print("Duplicate login detected, sending 'y' to kick old session...")
                self.send_keys_to_input('y', press_enter=True)
                time.sleep(2)

            # Now wait for welcome message
            if not self.wait_for_text("歡迎", timeout=10):
                # Try alternative success indicators
                if not self.wait_for_text("請按任意鍵繼續", timeout=3):
                    print("Failed to find welcome message")
                    # Take screenshot
                    self.driver.save_screenshot('/Users/guan/ptt_parser/after_password.png')
                    print("Screenshot saved to after_password.png")
                    return False

            # Press any key to continue
            print("Pressing key to continue...")
            self.driver.execute_script("""
                var input = document.querySelector('input');
                if (input) {
                    input.focus();
                    var enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    input.dispatchEvent(enterEvent);
                }
            """)
            time.sleep(3)

            # Check if main menu appears
            if self.wait_for_text("主功能表", timeout=10):
                print("Login successful! Reached main menu.")
                return True
            else:
                print("Failed to reach main menu")
                return False

        except Exception as e:
            import traceback
            print(f"Login failed with error: {e}")
            print(f"Full traceback:")
            traceback.print_exc()

            # Save screenshot for debugging
            try:
                self.driver.save_screenshot('/Users/guan/ptt_parser/login_error.png')
                print("Screenshot saved to login_error.png")
            except:
                pass

            return False

    def get_page_text(self) -> str:
        """
        Get current page text content

        Returns:
            Text content of current page
        """
        return self.driver.find_element(By.TAG_NAME, 'body').text

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()


def main():
    """Main function to test PTT login"""
    # Initialize client
    client = PTTWebSocketClient(headless=False)

    try:
        # Setup driver
        client.setup_driver()

        # Load credentials
        credentials = client.load_credentials('my_private_password.json')

        # Perform login
        success = client.login(
            username=credentials['account'],
            password=credentials['password']
        )

        if success:
            print("\n" + "="*50)
            print("LOGIN SUCCESSFUL!")
            print("="*50)

            # Keep browser open for a while to see the result
            time.sleep(5)
        else:
            print("\n" + "="*50)
            print("LOGIN FAILED!")
            print("="*50)

    finally:
        # Close browser
        client.close()


if __name__ == '__main__':
    main()
