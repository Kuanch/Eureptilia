#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT Parser Main - Main crawler program for PTT Gossiping board
"""

import PyPtt
from login import login_with_credentials


def get_board_articles(ptt_bot: PyPtt.API, board: str, num_articles: int = 10):
    """
    Get latest articles from a board

    Args:
        ptt_bot: Logged in PyPtt API instance
        board: Board name
        num_articles: Number of latest articles to fetch

    Returns:
        List of article dictionaries
    """
    # Get newest index
    newest_index = ptt_bot.get_newest_index(
        PyPtt.NewIndex.BOARD,
        board=board
    )

    print(f"Newest article index: {newest_index}")

    # Calculate start index
    start_index = max(1, newest_index - num_articles + 1)

    # Fetch articles
    articles = []
    for i in range(start_index, newest_index + 1):
        try:
            article = ptt_bot.get_post(
                board=board,
                index=i
            )

            if article:
                articles.append(article)

        except Exception as e:
            print(f"Error fetching article {i}: {e}")
            continue

    return articles


def display_articles(articles: list):
    """
    Display article list

    Args:
        articles: List of article dictionaries
    """
    print("\n" + "="*60)
    print(f"FETCHED {len(articles)} ARTICLES")
    print("="*60)

    for article in articles:
        index = article.get('index', 'N/A')
        title = article.get('title', 'N/A')
        author = article.get('author', 'N/A')
        date = article.get('date', 'N/A')

        print(f"\n[{index}] {title}")
        print(f"  Author: {author} | Date: {date}")


def display_article_detail(article: dict):
    """
    Display detailed article information

    Args:
        article: Article dictionary
    """
    print("\n" + "="*60)
    print("ARTICLE DETAILS")
    print("="*60)

    print(f"\nIndex: {article.get('index', 'N/A')}")
    print(f"Title: {article.get('title', 'N/A')}")
    print(f"Author: {article.get('author', 'N/A')}")
    print(f"Date: {article.get('date', 'N/A')}")
    print(f"Board: {article.get('board', 'N/A')}")
    print(f"AID: {article.get('aid', 'N/A')}")
    print(f"IP: {article.get('ip', 'N/A')}")

    content = article.get('content', '')
    print(f"\nContent:\n{content}")

    push_list = article.get('push_list', [])
    print(f"\n{'='*60}")
    print(f"PUSHES ({len(push_list)} total)")
    print("="*60)

    if push_list:
        for push in push_list:
            push_type = push.get('type', '')
            author = push.get('author', '')
            content = push.get('content', '')
            ipdatetime = push.get('time', '')

            print(f"{push_type} {author}: {content} ({ipdatetime})")
    else:
        print("No pushes")


def main():
    """Main function"""

    print("="*60)
    print("PTT PARSER - GOSSIPING BOARD CRAWLER")
    print("="*60)

    ptt_bot = None

    try:
        # Login
        print("\nLogging in to PTT...")
        ptt_bot = login_with_credentials()
        print("Login successful!")

        # Target board
        board = 'Gossiping'

        # Get latest articles
        print(f"\n{'='*60}")
        print(f"FETCHING ARTICLES FROM {board}")
        print("="*60)

        articles = get_board_articles(ptt_bot, board, num_articles=10)

        # Display article list
        display_articles(articles)

        # Display last (newest) article in detail
        if articles:
            print("\n" + "="*60)
            print("DISPLAYING NEWEST ARTICLE")
            print("="*60)

            newest_article = articles[-1]
            display_article_detail(newest_article)

        print("\n" + "="*60)
        print("CRAWLING COMPLETED SUCCESSFULLY")
        print("="*60)

    except PyPtt.exceptions.LoginError as e:
        print(f"\nLogin failed: {e}")

    except PyPtt.exceptions.NoSuchBoard as e:
        print(f"\nBoard not found: {e}")

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
