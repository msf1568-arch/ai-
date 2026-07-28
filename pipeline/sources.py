"""
All data sources for AI news and discoveries
"""

import requests
import feedparser
from typing import List, Dict

RSS_FEEDS = [
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "news"},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "news"},
    {"url": "https://www.artificialintelligence-news.com/feed/", "type": "news"},
    {"url": "https://venturebeat.com/category/ai/feed/", "type": "news"},
    {"url": "https://www.wired.com/feed/tag/ai/latest/rss", "type": "news"},
    {"url": "https://huggingface.co/blog/feed.xml", "type": "tool"},
    {"url": "https://openai.com/blog/rss/", "type": "research"},
    {"url": "https://blog.google/technology/ai/rss/", "type": "research"},
]

SUBREDDITS = [
    "artificial", "MachineLearning", "ChatGPT", "LocalLLaMA",
    "StableDiffusion", "singularity", "OpenAI", "ClaudeAI", "midjourney", "AItools",
]


def fetch_rss_items(seen: set) -> List[Dict]:
    items = []
    for feed_info in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_info["url"])
            for entry in parsed.entries[:10]:
                link = entry.get("link", "")
                if not link or link in seen:
                    continue
                items.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", ""))[:500],
                    "link": link,
                    "source": parsed.feed.get("title", "RSS"),
                    "type": feed_info["type"],
                    "platform": "rss"
                })
        except Exception as e:
            print(f"RSS error {feed_info['url']}: {e}")
    return items


def fetch_reddit_items(seen: set) -> List[Dict]:
    items = []
    headers = {"User-Agent": "AINewsPipeline/1.0"}
    for subreddit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                post_data = post.get("data", {})
                link = f"https://reddit.com{post_data.get('permalink', '')}"
                if link in seen:
                    continue
                score = post_data.get("score", 0)
                if score < 50:
                    continue
                items.append({
                    "title": post_data.get("title", ""),
                    "description": post_data.get("selftext", "")[:500] or post_data.get("title", ""),
                    "link": link,
                    "source": f"r/{subreddit}",
                    "type": "discovery",
                    "platform": "reddit",
                    "score": score,
                })
        except Exception as e:
            print(f"Reddit error r/{subreddit}: {e}")
    return items


def fetch_hackernews_items(seen: set) -> List[Dict]:
    items = []
    ai_keywords = ['ai', 'gpt', 'llm', 'openai', 'claude', 'gemini', 'model', 'neural',
                   'machine learning', 'deep learning', 'chatbot', 'diffusion', 'transformer']
    try:
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:50]
        for story_id in story_ids:
            try:
                story_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
                story = story_resp.json()
                if not story:
                    continue
                title = story.get("title", "").lower()
                link = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                if link in seen:
                    continue
                if not any(kw in title for kw in ai_keywords):
                    continue
                items.append({
                    "title": story.get("title", ""),
                    "description": story.get("title", ""),
                    "link": link,
                    "source": "Hacker News",
                    "type": "discovery",
                    "platform": "hackernews",
                    "score": story.get("score", 0),
                })
            except:
                continue
    except Exception as e:
        print(f"HN error: {e}")
    return items


def fetch_producthunt_items(seen: set) -> List[Dict]:
    items = []
    ai_keywords = ['ai', 'gpt', 'llm', 'chatbot', 'automation', 'machine learning', 'assistant', 'generate']
    try:
        parsed = feedparser.parse("https://www.producthunt.com/feed")
        for entry in parsed.entries[:20]:
            title = entry.get("title", "").lower()
            link = entry.get("link", "")
            if link in seen:
                continue
            if not any(kw in title for kw in ai_keywords):
                continue
            items.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", "")[:500],
                "link": link,
                "source": "Product Hunt",
                "type": "tool",
                "platform": "producthunt",
            })
    except Exception as e:
        print(f"PH error: {e}")
    return items


def fetch_all_items(seen: set) -> List[Dict]:
    all_items = []
    print("Fetching from RSS feeds...")
    all_items.extend(fetch_rss_items(seen))
    print("Fetching from Reddit...")
    all_items.extend(fetch_reddit_items(seen))
    print("Fetching from Hacker News...")
    all_items.extend(fetch_hackernews_items(seen))
    print("Fetching from Product Hunt...")
    all_items.extend(fetch_producthunt_items(seen))
    print(f"Total items collected: {len(all_items)}")
    return all_items
