"""
AI News & Discovery Pipeline - Main (Mistral Version)
"""

import os
import re
import json
import time
import requests

from sources import fetch_all_items
from generate_video import build_shorts_video, build_long_video

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

MAX_SHORTS = int(os.environ.get("MAX_SHORTS", "3"))
MAKE_LONG_VIDEO = os.environ.get("MAKE_LONG_VIDEO", "false").lower() == "true"

SEEN_FILE = "seen_links.json"
OUTPUT_DIR = "output"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def rank_with_mistral(items, count=10):
    if not items:
        return []
    items_to_check = items[:30]
    prompt = f"""You are an AI content curator. Analyze these {len(items_to_check)} items.
Select TOP {count} most viral/important ones.
For each create: title_short (under 10 words), summary_short (2-3 sentences).
Return ONLY valid JSON array, no markdown:
[{{"title_short": "...", "summary_short": "...", "link": "...", "source": "...", "type": "...", "score": 95}}]
ITEMS:
{json.dumps(items_to_check, ensure_ascii=False)}
"""
    body = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
    }
    try:
        resp = requests.post(MISTRAL_URL, json=body, headers=headers, timeout=90)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        cleaned = re.sub(r'```json|```', '
