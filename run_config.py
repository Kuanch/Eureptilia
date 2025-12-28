#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT Parser - Run crawler tasks from configuration file
"""

import sys
from login import login_with_credentials
from crawler import run_config


def main():
    """Main function"""

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 run_config.py <config_file.json>")
        print("\nExample:")
        print("  python3 run_config.py config_example.json")
        sys.exit(1)

    config_file = sys.argv[1]

    print("="*60)
    print("PTT PARSER - CONFIG-BASED CRAWLER")
    print("="*60)
    print(f"\nConfiguration file: {config_file}")

    ptt_bot = None

    try:
        # Login
        print("\nLogging in to PTT...")
        ptt_bot = login_with_credentials()
        print("Login successful!")

        # Run tasks from config
        run_config(ptt_bot, config_file)

    except FileNotFoundError:
        print(f"\nError: Configuration file '{config_file}' not found!")

    except Exception as e:
        import traceback
        print(f"\nError occurred: {e}")
        traceback.print_exc()

    finally:
        # Logout
        if ptt_bot:
            try:
                print("\nLogging out...")
                ptt_bot.logout()
                print("Logout successful")
            except:
                pass


if __name__ == '__main__':
    main()
