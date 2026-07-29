"""
AI News Pipeline - v3
"""

import os
import re
import json
import time
import requests
import traceback

from sources import fetch_all_items
from generate_video import (
    build_shorts_video,
    build_long_video,
)

MKEY = os.environ["MISTRAL_API_KEY"]
TBOT = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TCHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
MAX_S = int(os.environ.get("MAX_SHORTS", "3"))
SEEN_FILE = "seen_links.json"
OUTDIR = "output"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def rank(items, count=10):
    if not items:
        return []
    batch = items[:30]
    prompt = (
        "You are an AI content curator.\n"
        f"From these {len(batch)} items, "
        f"pick TOP {count} most viral.\n"
        "For each return:\n"
        "- title_short: under 10 words\n"
        "- narration: exactly 6 sentences. "
        "Start with a hook question. "
        "End with call to action.\n"
        "- link, source, type, score\n"
        'Return JSON: {"results": [...]}\n'
        "ITEMS:\n"
        + json.dumps(batch, ensure_ascii=False)
    )
    try:
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MKEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {
                    "type": "json_object"
                },
            },
            timeout=90,
