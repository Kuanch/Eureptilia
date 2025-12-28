#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT Login Module - Handle PTT login via PyPtt WebSocket
"""

import PyPtt
import json
from typing import Optional


def load_credentials(credential_file: str = 'my_private_password.json') -> dict:
    """
    Load credentials from JSON file

    Args:
        credential_file: Path to credential JSON file

    Returns:
        Dictionary with 'account' and 'password' keys
    """
    with open(credential_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def login(username: str, password: str, kick_other_session: bool = True) -> PyPtt.API:
    """
    Login to PTT using PyPtt

    Args:
        username: PTT account username
        password: PTT account password
        kick_other_session: Whether to kick duplicate sessions

    Returns:
        PyPtt.API instance (logged in)

    Raises:
        PyPtt.exceptions.LoginError: Login failed
    """
    ptt_bot = PyPtt.API()

    ptt_bot.login(
        username,
        password,
        kick_other_session=kick_other_session
    )

    return ptt_bot


def login_with_credentials(credential_file: str = 'my_private_password.json',
                          kick_other_session: bool = True) -> PyPtt.API:
    """
    Login to PTT using credentials from file

    Args:
        credential_file: Path to credential JSON file
        kick_other_session: Whether to kick duplicate sessions

    Returns:
        PyPtt.API instance (logged in)

    Raises:
        PyPtt.exceptions.LoginError: Login failed
        FileNotFoundError: Credential file not found
    """
    credentials = load_credentials(credential_file)

    return login(
        credentials['account'],
        credentials['password'],
        kick_other_session=kick_other_session
    )


if __name__ == '__main__':
    """Test login functionality"""

    print("="*60)
    print("PTT LOGIN TEST")
    print("="*60)

    try:
        print("\nLogging in...")
        ptt_bot = login_with_credentials()

        print("Login successful!")
        print(f"Connected to PTT via WebSocket")

        # Logout
        print("\nLogging out...")
        ptt_bot.logout()
        print("Logout successful")

    except PyPtt.exceptions.LoginError as e:
        print(f"\nLogin failed: {e}")

    except FileNotFoundError:
        print("\nCredential file not found!")

    except Exception as e:
        import traceback
        print(f"\nError: {e}")
        traceback.print_exc()
