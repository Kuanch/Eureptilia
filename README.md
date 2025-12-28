# PTT Parser

A flexible PTT (批踢踢) crawler using WebSocket connection via PyPtt library.

## Features

- **WebSocket-based**: Pure WebSocket connection, no browser automation required
- **Multiple search types**:
  - Get latest articles
  - Search by title keyword (PTT's `/` function)
  - Search by author (PTT's `a` function)
  - Search by push content (custom implementation)
  - Get specific article by index
  - Get articles by date range
- **JSON configuration**: Define crawling tasks in JSON format
- **Flexible output**: Save results to JSON files

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set up credentials

Create `my_private_password.json`:

```json
{
  "account": "your_ptt_account",
  "password": "your_password"
}
```

### 2. Create task configuration

Create a JSON configuration file (see `config_example.json` for full example):

```json
{
  "tasks": [
    {
      "name": "Get latest articles",
      "type": "get_articles",
      "board": "Gossiping",
      "count": 10,
      "output": "latest.json"
    },
    {
      "name": "Search by keyword",
      "type": "search_title",
      "board": "Gossiping",
      "keyword": "台積電",
      "count": 20,
      "output": "search_tsmc.json"
    }
  ],
  "options": {
    "delay_between_requests": 0.5
  }
}
```

## Usage

### Run with configuration file

```bash
python3 run_config.py config_test.json
```

### Run simple crawler

```bash
python3 main.py
```

### Test login

```bash
python3 login.py
```

## Task Types

All task types support optional time-based filtering using `start_time` and `end_time` fields (HH:MM format). When time filters are provided, the crawler uses smart sampling to efficiently locate articles within the specified time range.

### 1. `get_articles`
Get latest N articles from a board.

**Count-based** (get latest N articles):
```json
{
  "type": "get_articles",
  "board": "Gossiping",
  "count": 10,
  "output": "latest.json"
}
```

**Time-based** (get articles in time range):
```json
{
  "type": "get_articles",
  "board": "Gossiping",
  "start_time": "21:00",
  "end_time": "22:00",
  "output": "evening_articles.json"
}
```

### 2. `search_title`
Search articles by title keyword (uses PTT's `/` search).

**Count-based**:
```json
{
  "type": "search_title",
  "board": "Gossiping",
  "keyword": "輝達",
  "count": 20,
  "output": "search_nvidia.json"
}
```

**Time-based**:
```json
{
  "type": "search_title",
  "board": "Gossiping",
  "keyword": "輝達",
  "start_time": "09:00",
  "end_time": "17:00",
  "output": "search_nvidia_daytime.json"
}
```

### 3. `search_author`
Search articles by author (uses PTT's `a` search).

**Count-based**:
```json
{
  "type": "search_author",
  "board": "Gossiping",
  "author": "CodingMan",
  "count": 10,
  "output": "author_search.json"
}
```

**Time-based**:
```json
{
  "type": "search_author",
  "board": "Gossiping",
  "author": "CodingMan",
  "start_time": "18:00",
  "end_time": "23:59",
  "output": "author_search_evening.json"
}
```

### 4. `search_comment`
Search for articles with comments containing keyword (custom implementation, not PTT native).

**Count-based**:
```json
{
  "type": "search_comment",
  "board": "Gossiping",
  "keyword": "推",
  "count": 50,
  "output": "comment_search.json"
}
```

**Time-based**:
```json
{
  "type": "search_comment",
  "board": "Gossiping",
  "keyword": "推",
  "start_time": "20:00",
  "end_time": "21:00",
  "output": "comment_search_evening.json"
}
```

### 5. `search_comments_by_author`
Search for articles where a specific author has commented (custom implementation, not PTT native).

**Time-based**:
```json
{
  "type": "search_comments_by_author",
  "board": "Gossiping",
  "author": "sixigma",
  "start_time": "19:00",
  "end_time": "20:00",
  "output": "author_comments.json"
}
```

**Count-based**:
```json
{
  "type": "search_comments_by_author",
  "board": "Gossiping",
  "author": "CodingMan",
  "count": 100,
  "output": "author_comments.json"
}
```

### 6. `get_article`
Get specific article by index.

```json
{
  "type": "get_article",
  "board": "Gossiping",
  "index": 786786,
  "output": "article.json"
}
```

### 7. `get_articles_by_date`
Get articles within date range.

```json
{
  "type": "get_articles_by_date",
  "board": "Gossiping",
  "start_date": "2025-10-01",
  "end_date": "2025-10-04",
  "output": "october_articles.json"
}
```

## Output Format

All results are saved as JSON arrays containing article objects:

```json
[
  {
    "board": "Gossiping",
    "aid": "1euHv2Aw",
    "index": 786786,
    "author": "a1b2c3d4e5 (阿翔)",
    "date": "Sat Oct  4 21:16:48 2025",
    "title": "[問卦] 新竹關西普發一萬",
    "content": "...",
    "ip": "39.10.10.198",
    "comments": [
      {
        "type": "PUSH",
        "author": "user123",
        "content": "推",
        "time": "10/04 21:20"
      }
    ]
  }
]
```

## Project Structure

```
ptt_parser/
├── main.py              # Simple crawler example
├── run_config.py        # Run tasks from config file
├── login.py             # Login module
├── crawler.py           # Crawler implementation
├── config_example.json  # Full configuration example
├── config_test.json     # Test configuration
├── requirements.txt     # Python dependencies
├── archive/             # Archived experimental code
└── README.md            # This file
```

## Notes

- **PTT Native Search**: Tasks like `search_title` and `search_author` use PTT's built-in search functions (`/` and `a`), which are fast and efficient.
- **Custom Search**: Tasks like `search_comment` and `search_comments_by_author` require fetching articles and filtering manually, which is slower but provides functionality not available in PTT.
- **Time-based Filtering**: All task types support `start_time` and `end_time` parameters (HH:MM format). The crawler uses smart sampling (checks every 100 articles) to efficiently locate the target time range before fetching all articles in that range.
- **Count vs Time**: When both `count` and time filters are provided, time filters take precedence. The `count` parameter is only used as fallback when time filters are not specified.
- **Rate Limiting**: Use `delay_between_requests` option to avoid hammering PTT servers.
- **Date Range Search**: The `get_articles_by_date` task scans articles backwards from newest, may be slow for large date ranges.

## License

This project is for educational purposes only. Please respect PTT's terms of service and do not abuse the crawler.
