#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT Web Crawler - Crawl PTT using the web version (https://www.ptt.cc)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time


class PTTWebCrawler:
    """PTT Web version crawler"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.base_url = "https://www.ptt.cc"

    def verify_18(self, board: str) -> bool:
        """
        Handle 18+ verification for boards like Gossiping

        Args:
            board: Board name

        Returns:
            True if verification successful
        """
        url = f"{self.base_url}/bbs/{board}/index.html"
        response = self.session.get(url)

        # Check if 18+ verification is needed
        if 'over18' in response.url or '我同意' in response.text:
            print(f"Board {board} requires 18+ verification, submitting...")

            # Submit verification
            verify_url = f"{self.base_url}/ask/over18"
            data = {'from': f'/bbs/{board}/index.html', 'yes': 'yes'}
            self.session.post(verify_url, data=data)

            return True

        return True

    def get_board_articles(self, board: str, pages: int = 1) -> List[Dict]:
        """
        Get article list from a board

        Args:
            board: Board name (e.g., 'Gossiping')
            pages: Number of pages to crawl

        Returns:
            List of article dictionaries
        """
        # Handle 18+ verification if needed
        self.verify_18(board)

        articles = []
        url = f"{self.base_url}/bbs/{board}/index.html"

        for page_num in range(pages):
            print(f"Crawling page {page_num + 1}/{pages}: {url}")

            response = self.session.get(url)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')

            # Find all article entries
            entries = soup.find_all('div', class_='r-ent')

            for entry in entries:
                try:
                    # Extract article info
                    title_tag = entry.find('div', class_='title').find('a')

                    if not title_tag:
                        continue  # Skip deleted articles

                    article = {
                        'title': title_tag.text.strip(),
                        'url': self.base_url + title_tag['href'],
                        'author': entry.find('div', class_='author').text.strip() if entry.find('div', class_='author') else '',
                        'date': entry.find('div', class_='date').text.strip() if entry.find('div', class_='date') else '',
                        'push_count': entry.find('div', class_='nrec').text.strip() if entry.find('div', class_='nrec') else '0'
                    }

                    articles.append(article)

                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue

            # Find previous page link
            prev_link = soup.find('a', string='‹ 上頁')
            if prev_link and page_num < pages - 1:
                url = self.base_url + prev_link['href']
                time.sleep(0.5)  # Be polite, don't hammer the server
            else:
                break

        return articles

    def get_article_content(self, url: str) -> Dict:
        """
        Get article content

        Args:
            url: Article URL

        Returns:
            Dictionary with article content
        """
        response = self.session.get(url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'lxml')

        # Extract article metadata
        meta_tags = soup.find_all('span', class_='article-meta-tag')
        meta_values = soup.find_all('span', class_='article-meta-value')

        metadata = {}
        for tag, value in zip(meta_tags, meta_values):
            metadata[tag.text.strip()] = value.text.strip()

        # Extract article content
        main_content = soup.find('div', id='main-content')

        if not main_content:
            return {}

        # Remove metadata divs
        for meta_div in main_content.find_all('div', class_='article-metaline'):
            meta_div.extract()

        for meta_div in main_content.find_all('div', class_='article-metaline-right'):
            meta_div.extract()

        # Remove push section
        for push_div in main_content.find_all('div', class_='push'):
            push_div.extract()

        content = main_content.text.strip()

        # Extract pushes (comments)
        pushes = []
        push_divs = soup.find_all('div', class_='push')

        for push_div in push_divs:
            try:
                push_tag = push_div.find('span', class_='push-tag').text.strip()
                push_user = push_div.find('span', class_='push-userid').text.strip()
                push_content = push_div.find('span', class_='push-content').text.strip()
                push_time = push_div.find('span', class_='push-ipdatetime').text.strip()

                pushes.append({
                    'tag': push_tag,
                    'user': push_user,
                    'content': push_content,
                    'time': push_time
                })
            except:
                continue

        return {
            'metadata': metadata,
            'content': content,
            'pushes': pushes
        }


def main():
    """Main function to test PTT web crawler"""
    crawler = PTTWebCrawler()

    print("="*60)
    print("PTT WEB CRAWLER - GOSSIPING BOARD")
    print("="*60)

    # Get articles from Gossiping board
    print("\nFetching articles from Gossiping board...")
    articles = crawler.get_board_articles('Gossiping', pages=2)

    print(f"\nFound {len(articles)} articles")
    print("\nFirst 5 articles:")
    print("-"*60)

    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. [{article['push_count']}] {article['title']}")
        print(f"   Author: {article['author']}")
        print(f"   Date: {article['date']}")
        print(f"   URL: {article['url']}")

    # Get content of first article
    if articles:
        print("\n" + "="*60)
        print("FETCHING FIRST ARTICLE CONTENT")
        print("="*60)

        first_article = articles[0]
        content = crawler.get_article_content(first_article['url'])

        if content:
            print(f"\nTitle: {first_article['title']}")
            print(f"Author: {content['metadata'].get('作者', 'N/A')}")
            print(f"Board: {content['metadata'].get('看板', 'N/A')}")
            print(f"Time: {content['metadata'].get('時間', 'N/A')}")
            print(f"\nContent (first 500 chars):\n{content['content'][:500]}")
            print(f"\nTotal pushes: {len(content['pushes'])}")

            if content['pushes']:
                print("\nFirst 3 pushes:")
                for push in content['pushes'][:3]:
                    print(f"  {push['tag']} {push['user']}: {push['content']}")


if __name__ == '__main__':
    main()
