#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT Crawler - Flexible crawler with various search capabilities
"""

import PyPtt
import json
import time
from typing import List, Dict, Optional
from datetime import datetime


class PTTCrawler:
    """PTT Crawler with multiple search capabilities"""

    def __init__(self, ptt_bot: PyPtt.API):
        """
        Initialize crawler

        Args:
            ptt_bot: Logged in PyPtt API instance
        """
        self.ptt_bot = ptt_bot

    def get_articles(self, board: str, count: int = 10, start_time: Optional[str] = None,
                    end_time: Optional[str] = None) -> List[Dict]:
        """
        Get latest articles from board

        Args:
            board: Board name
            count: Number of articles to fetch (used if time filters not provided)
            start_time: Start time filter (HH:MM format), optional
            end_time: End time filter (HH:MM format), optional

        Returns:
            List of article dictionaries
        """
        # Use time-based filtering if provided
        if start_time and end_time:
            return self._get_articles_by_time_range(board, start_time, end_time)

        # Otherwise use count-based fetching
        newest_index = self.ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board=board
        )

        articles = []
        start_index = max(1, newest_index - count + 1)

        for i in range(start_index, newest_index + 1):
            try:
                article = self.ptt_bot.get_post(board=board, index=i)
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching article {i}: {e}")
                continue

        return articles

    def search_by_title(self, board: str, keyword: str, count: int = 10,
                       start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
        """
        Search articles by title keyword (using PTT's / search)

        Args:
            board: Board name
            keyword: Keyword to search in title
            count: Maximum number of articles to fetch (used if time filters not provided)
            start_time: Start time filter (HH:MM format), optional
            end_time: End time filter (HH:MM format), optional

        Returns:
            List of article dictionaries
        """
        # Create search list for PyPtt
        search_list = [(PyPtt.SearchType.KEYWORD, keyword)]

        # Use time-based filtering if provided
        if start_time and end_time:
            return self._get_articles_by_time_range(board, start_time, end_time, search_list=search_list)

        # Otherwise use count-based fetching
        try:
            newest_index = self.ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board=board,
                search_list=search_list
            )
        except:
            return []

        articles = []
        start_index = max(1, newest_index - count + 1)

        for i in range(start_index, newest_index + 1):
            try:
                article = self.ptt_bot.get_post(
                    board=board,
                    index=i,
                    search_list=search_list
                )
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching article {i}: {e}")
                continue

        return articles

    def search_by_author(self, board: str, author: str, count: int = 10,
                        start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
        """
        Search articles by author (using PTT's a search)

        Args:
            board: Board name
            author: Author ID
            count: Maximum number of articles to fetch (used if time filters not provided)
            start_time: Start time filter (HH:MM format), optional
            end_time: End time filter (HH:MM format), optional

        Returns:
            List of article dictionaries
        """
        search_list = [(PyPtt.SearchType.AUTHOR, author)]

        # Use time-based filtering if provided
        if start_time and end_time:
            return self._get_articles_by_time_range(board, start_time, end_time, search_list=search_list)

        # Otherwise use count-based fetching
        try:
            newest_index = self.ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board=board,
                search_list=search_list
            )
        except:
            return []

        articles = []
        start_index = max(1, newest_index - count + 1)

        for i in range(start_index, newest_index + 1):
            try:
                article = self.ptt_bot.get_post(
                    board=board,
                    index=i,
                    search_list=search_list
                )
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching article {i}: {e}")
                continue

        return articles

    def search_by_comment_content(self, board: str, keyword: str, count: int = 50,
                                 start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
        """
        Search for articles containing specific keyword in comments
        Note: This is NOT supported by PTT, so we need to fetch and filter manually

        Args:
            board: Board name
            keyword: Keyword to search in comment content
            count: Number of recent articles to scan (used if time filters not provided)
            start_time: Start time filter (HH:MM format), optional
            end_time: End time filter (HH:MM format), optional

        Returns:
            List of article dictionaries that contain the keyword in comments
        """
        # Get articles (either by time range or count)
        all_articles = self.get_articles(board, count, start_time=start_time, end_time=end_time)

        # Filter articles with matching comments
        matched_articles = []

        for article in all_articles:
            comments = article.get('comments', [])

            # Check if any comment contains the keyword
            for comment in comments:
                comment_content = comment.get('content', '')
                if keyword.lower() in comment_content.lower():
                    matched_articles.append(article)
                    break  # Found match, no need to check other comments

        return matched_articles

    def _get_articles_by_time_range(self, board: str, start_time: str, end_time: str,
                                   search_list: Optional[List] = None) -> List[Dict]:
        """
        Get articles within time range
        Helper method used by all search functions

        Args:
            board: Board name
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            search_list: Optional PyPtt search list for filtered searches

        Returns:
            List of article dictionaries in time range
        """
        from datetime import datetime, time

        # Find the article index range
        start_index, end_index = self.find_article_range_by_time(
            board, start_time, end_time, search_list=search_list
        )

        if start_index is None or end_index is None:
            print("Could not determine article range for specified time")
            return []

        # Fetch articles in the range
        all_articles = []
        print(f"Fetching articles from index {start_index} to {end_index}")

        for i in range(start_index, end_index + 1):
            try:
                article = self.ptt_bot.get_post(board=board, index=i, search_list=search_list)
                if article:
                    all_articles.append(article)
            except Exception as e:
                print(f"Error fetching article {i}: {e}")
                continue

        # Filter by exact time range
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))
        start_time_obj = time(start_h, start_m)
        end_time_obj = time(end_h, end_m)

        filtered_articles = []
        for article in all_articles:
            date_str = article.get('date', '')
            if not date_str:
                continue
            try:
                article_datetime = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
                article_time = article_datetime.time()

                if start_time_obj <= article_time <= end_time_obj:
                    filtered_articles.append(article)
            except (ValueError, TypeError):
                continue

        print(f"Found {len(filtered_articles)} articles in time range")
        return filtered_articles

    def find_article_range_by_time(self, board: str, start_time: str, end_time: str,
                                   search_list: Optional[List] = None,
                                   sample_interval: int = 100) -> tuple:
        """
        Find article index range that falls within specified time range
        Uses sampling strategy to efficiently locate the range

        Args:
            board: Board name
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            search_list: Optional PyPtt search list for filtered searches
            sample_interval: Number of articles to skip between samples

        Returns:
            Tuple of (start_index, end_index) or (None, None) if not found
        """
        from datetime import datetime, time, timedelta

        # Parse time strings
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))
        target_start = time(start_h, start_m)
        target_end = time(end_h, end_m)

        # Get newest index
        newest_index = self.ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board=board,
            search_list=search_list
        )

        print(f"Newest article index: {newest_index}")
        print(f"Searching for time range: {start_time} - {end_time}")

        # Sample articles to find approximate range
        current_index = newest_index
        samples = []

        while current_index > 0:
            try:
                article = self.ptt_bot.get_post(board=board, index=current_index, search_list=search_list)
                if article:
                    date_str = article.get('date', '')
                    try:
                        article_datetime = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
                        article_time = article_datetime.time()
                        samples.append((current_index, article_datetime, article_time))
                        print(f"Sample: index={current_index}, time={article_time}")

                        # If we've gone past the start time significantly, we can stop
                        if len(samples) >= 2:
                            # Calculate time difference per 100 articles
                            time_diff = samples[-2][1] - samples[-1][1]
                            if article_time < target_start:
                                # We've gone past the start time, adjust tolerance
                                tolerance = max(timedelta(minutes=10), abs(time_diff))
                                time_delta = datetime.combine(datetime.today(), target_start) - \
                                           datetime.combine(datetime.today(), article_time)

                                if abs(time_delta) > tolerance * 2:
                                    print(f"Gone too far past target range, stopping search")
                                    break

                    except ValueError as e:
                        print(f"Failed to parse date: {date_str}")
                        pass

            except Exception as e:
                print(f"Error fetching article {current_index}: {e}")

            current_index -= sample_interval

            # Safety limit: don't sample more than 1000 times (100k articles)
            if len(samples) >= 1000:
                print("Reached sampling limit")
                break

        if len(samples) < 2:
            print("Not enough samples to determine range")
            return (None, None)

        # Find the range that encompasses our target time
        end_index = None
        start_index = None

        for i, (idx, dt, t) in enumerate(samples):
            if t <= target_end and end_index is None:
                end_index = idx + sample_interval  # Add buffer
            if t <= target_start:
                start_index = max(1, idx - sample_interval)  # Add buffer
                break

        if end_index is None:
            end_index = samples[0][0]  # Use newest if not found
        if start_index is None:
            start_index = max(1, samples[-1][0] - sample_interval)

        print(f"Determined article range: {start_index} - {end_index}")
        return (start_index, end_index)

    def search_comments_by_author(self, board: str, author: str, start_time: Optional[str] = None,
                                 end_time: Optional[str] = None, count: int = 100) -> List[Dict]:
        """
        Search for articles where specific author has commented
        Note: This is NOT supported by PTT, so we need to fetch and filter manually

        Args:
            board: Board name
            author: Author ID to search for in comments
            start_time: Start time filter (HH:MM format), optional
            end_time: End time filter (HH:MM format), optional
            count: Number of recent articles to scan (used if time filters not provided)

        Returns:
            List of article dictionaries where the author has commented
        """
        # Get articles (either by time range or count)
        all_articles = self.get_articles(board, count, start_time=start_time, end_time=end_time)

        # Filter articles where author has commented
        matched_articles = []

        for article in all_articles:
            comments = article.get('comments', [])

            # Check if author has commented on this article
            for comment in comments:
                comment_author = comment.get('author', '')
                if comment_author.lower() == author.lower():
                    matched_articles.append(article)
                    break  # Found match, no need to check other comments

        return matched_articles

    def get_article_by_index(self, board: str, index: int) -> Optional[Dict]:
        """
        Get specific article by index

        Args:
            board: Board name
            index: Article index

        Returns:
            Article dictionary or None
        """
        try:
            return self.ptt_bot.get_post(board=board, index=index)
        except Exception as e:
            print(f"Error fetching article {index}: {e}")
            return None

    def get_articles_by_date_range(self, board: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Get articles within date range
        Note: This requires scanning articles and filtering by date

        Args:
            board: Board name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of article dictionaries in date range
        """
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Get newest index
        newest_index = self.ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board=board
        )

        matched_articles = []

        # Scan backwards from newest
        # Estimate: scan up to 1000 articles or until we're past start_date
        for i in range(newest_index, max(1, newest_index - 1000), -1):
            try:
                article = self.ptt_bot.get_post(board=board, index=i)

                if not article:
                    continue

                # Parse article date
                date_str = article.get('date', '')
                try:
                    # PTT date format: "Sat Oct  4 21:16:48 2025"
                    article_date = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')

                    # Check if in range
                    if start <= article_date <= end:
                        matched_articles.append(article)
                    elif article_date < start:
                        # Past start date, stop searching
                        break

                except ValueError:
                    continue

            except Exception as e:
                print(f"Error fetching article {i}: {e}")
                continue

        return matched_articles

    def save_to_json(self, data: List[Dict], output_file: str):
        """
        Save data to JSON file

        Args:
            data: Data to save
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(data)} items to {output_file}")


def run_task(crawler: PTTCrawler, task: Dict, options: Dict):
    """
    Run a single crawler task

    Args:
        crawler: PTTCrawler instance
        task: Task configuration
        options: Global options
    """
    task_type = task.get('type')

    print(f"\n{'='*60}")
    print(f"TASK TYPE: {task_type}")
    print("="*60)

    results = []

    if task_type == 'get_articles':
        board = task.get('board')
        count = task.get('count', 10)
        start_time = task.get('start_time')
        end_time = task.get('end_time')

        if start_time and end_time:
            print(f"Time range: {start_time} - {end_time}")
            results = crawler.get_articles(board, count, start_time=start_time, end_time=end_time)
        else:
            results = crawler.get_articles(board, count)

    elif task_type == 'search_title':
        board = task.get('board')
        keyword = task.get('keyword')
        count = task.get('count', 10)
        start_time = task.get('start_time')
        end_time = task.get('end_time')
        print(f"Searching for keyword: {keyword}")

        if start_time and end_time:
            print(f"Time range: {start_time} - {end_time}")
            results = crawler.search_by_title(board, keyword, count, start_time=start_time, end_time=end_time)
        else:
            results = crawler.search_by_title(board, keyword, count)

    elif task_type == 'search_author':
        board = task.get('board')
        author = task.get('author')
        count = task.get('count', 10)
        start_time = task.get('start_time')
        end_time = task.get('end_time')
        print(f"Searching for author: {author}")

        if start_time and end_time:
            print(f"Time range: {start_time} - {end_time}")
            results = crawler.search_by_author(board, author, count, start_time=start_time, end_time=end_time)
        else:
            results = crawler.search_by_author(board, author, count)

    elif task_type == 'search_comment':
        board = task.get('board')
        keyword = task.get('keyword')
        count = task.get('count', 50)
        start_time = task.get('start_time')
        end_time = task.get('end_time')
        print(f"Searching comments for keyword: {keyword}")

        if start_time and end_time:
            print(f"Time range: {start_time} - {end_time}")
            results = crawler.search_by_comment_content(board, keyword, count, start_time=start_time, end_time=end_time)
        else:
            results = crawler.search_by_comment_content(board, keyword, count)

    elif task_type == 'search_comments_by_author':
        board = task.get('board')
        author = task.get('author')
        start_time = task.get('start_time')
        end_time = task.get('end_time')
        count = task.get('count', 100)

        if start_time and end_time:
            print(f"Searching for articles where '{author}' has commented (time range: {start_time}-{end_time})")
            results = crawler.search_comments_by_author(board, author, start_time=start_time, end_time=end_time, count=count)
        else:
            print(f"Searching for articles where '{author}' has commented")
            results = crawler.search_comments_by_author(board, author, count=count)

    elif task_type == 'get_article':
        board = task.get('board')
        index = task.get('index')
        article = crawler.get_article_by_index(board, index)
        if article:
            results = [article]

    elif task_type == 'get_articles_by_date':
        board = task.get('board')
        start_date = task.get('start_date')
        end_date = task.get('end_date')
        print(f"Date range: {start_date} to {end_date}")
        results = crawler.get_articles_by_date_range(board, start_date, end_date)

    else:
        print(f"Unknown task type: {task_type}")
        return

    print(f"Found {len(results)} results")

    # Save results
    output_file = task.get('output')
    if output_file and results:
        crawler.save_to_json(results, output_file)

    # Add delay between tasks
    delay = options.get('delay_between_requests', 0.5)
    time.sleep(delay)


def run_config(ptt_bot: PyPtt.API, config_file: str):
    """
    Run crawler tasks from configuration file

    Args:
        ptt_bot: Logged in PyPtt API instance
        config_file: Path to configuration JSON file
    """
    # Load config
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    tasks = config.get('tasks', [])
    options = config.get('options', {})

    # Create crawler
    crawler = PTTCrawler(ptt_bot)

    # Run each task
    for task in tasks:
        try:
            run_task(crawler, task, options)
        except Exception as e:
            import traceback
            print(f"\nTask failed: {e}")
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print(f"ALL TASKS COMPLETED ({len(tasks)} tasks)")
    print("="*60)
