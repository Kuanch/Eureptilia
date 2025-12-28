#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check specific article by index
"""

import PyPtt
import json


def main():
    # Load credentials
    with open('my_private_password.json', 'r') as f:
        credentials = json.load(f)

    ptt_bot = PyPtt.API()

    try:
        # Login
        ptt_bot.login(
            credentials['account'],
            credentials['password'],
            kick_other_session=True
        )

        board = 'Gossiping'

        # Check newest index
        newest_index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board=board
        )
        print(f"Current newest index: {newest_index}")

        # Get article 786781
        target_index = 786781
        print(f"\nFetching article {target_index}...")

        article = ptt_bot.get_post(
            board=board,
            index=target_index
        )

        if article:
            print(f"\nArticle {target_index}:")
            print(f"Title: {article.get('title', 'N/A')}")
            print(f"Author: {article.get('author', 'N/A')}")
            print(f"Date: {article.get('date', 'N/A')}")
            print(f"Index: {article.get('index', 'N/A')}")
            print(f"AID: {article.get('aid', 'N/A')}")
        else:
            print(f"Article {target_index} not found or deleted")

        # Also check article 786780
        print(f"\n{'='*60}")
        print(f"Fetching article 786780...")

        article_780 = ptt_bot.get_post(
            board=board,
            index=786780
        )

        if article_780:
            print(f"\nArticle 786780:")
            print(f"Title: {article_780.get('title', 'N/A')}")
            print(f"Author: {article_780.get('author', 'N/A')}")
            print(f"Date: {article_780.get('date', 'N/A')}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    finally:
        ptt_bot.logout()


if __name__ == '__main__':
    main()
