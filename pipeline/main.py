"""
Full pipeline (English output, Mistral for filtering/summarizing):
1. Fetch news from RSS feeds
2. Skip already-seen links (tracked in seen_links.json)
3. Filter + summarize each item with Mistral (max MAX_ITEMS per run)
4. Generate a short vertical video for each approved item
5. Send the video + caption to Telegram
"""

import os
import re
import json
import time
import requests
import feedparser

from generate_video import build_video

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "3"))
SEEN_FILE = "seen_links.json"
OUTPUT_DIR = "output"

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
]

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def fetch_candidates(seen):
    candidates = []
    for url in RSS_FEEDS:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            link = entry.get("link")
            if not link or link in seen:
                continue
            candidates.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": link,
            })
    return candidates


def ask_mistral(item):
    prompt = (
        "Review this AI news item:\n\n"
        f"Title: {item['title']}\nSummary: {item['summary']}\n\n"
        "Respond with raw JSON only, no extra text, no markdown/backticks:\n"
        '{"is_relevant": true/false, "title_short": "short catchy title (under 12 words)", '
        '"summary_short": "2-3 sentence summary suitable for a voiceover narration"}\n\n'
        "Set is_relevant to true ONLY if this news is genuinely interesting and understandable "
        "for a general audience interested in AI (not overly technical/academic, not a rumor). "
        "If in doubt, set it to false."
    )
    body = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
    }
    resp = requests.post(MISTRAL_URL, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)


def send_video_to_telegram(video_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
            files={"video": f},
            timeout=180,
        )
    if resp.status_code != 200:
        print(f"Telegram send error: {resp.text}")
    else:
        print("Video sent to Telegram successfully.")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    seen = load_seen()
    candidates = fetch_candidates(seen)
    print(f"{len(candidates)} new candidate item(s) found.")

made = 0
    for item in candidates:
        if made >= MAX_ITEMS:
            break

        try:
            result = ask_mistral(item)
        except Exception as e:
            print(f"Mistral error for '{item['title']}': {e}")
            continue

        if not result.get("is_relevant"):
            print(f"Skipped (not relevant): {item['title']}")
            seen.add(item["link"])
            continue

        title_short = result["title_short"]
        summary_short = result["summary_short"]
        video_path = os.path.join(OUTPUT_DIR, f"video_{made+1}.mp4")

        try:
            build_video(title_short, summary_short, item["link"], video_path)
        except Exception as e:
            print(f"Video build error for '{title_short}': {e}")
            continue

        caption = f"{title_short}\n\n{summary_short}\n\nSource: {item['link']}"
        send_video_to_telegram(video_path, caption)
        seen.add(item["link"])
        made += 1
        time.sleep(2)

    save_seen(seen)

    if made == 0:
        print("No video was generated in this run.")


if __name__ == "__main__":
    main()
