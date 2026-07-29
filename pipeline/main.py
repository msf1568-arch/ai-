"""
AI News Pipeline v8 - Prompt Generator
"""

import os
import re
import json
import time
import traceback
import requests

from sources import fetch_all_items
from generate_video import build_shorts_video

MKEY = os.environ["MISTRAL_API_KEY"]
TBOT = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TCHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
MAX_S = int(os.environ.get("MAX_SHORTS", "3"))
SEEN_FILE = "seen_links.json"
OUTDIR = "output"
API_URL = "https://api.mistral.ai/v1/chat/completions"


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
        "You are an AI content curator. "
        "Pick TOP " + str(count) + " most viral "
        "from these " + str(len(batch)) + " items. "
        "For each return: "
        "title_short (under 10 words), "
        "narration (exactly 6 sentences, "
        "start with a hook question, "
        "end with call to action), "
        "link, source, type, score. "
        'Return JSON: {"results": [...]}\n'
        "ITEMS:\n"
        + json.dumps(batch, ensure_ascii=False)
    )
    headers = {
        "Authorization": "Bearer " + MKEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
    }
    try:
        r = requests.post(
            API_URL,
            headers=headers,
            json=body,
            timeout=90,
        )
        r.raise_for_status()
        txt = r.json()
        txt = txt["choices"][0]["message"]["content"]
        txt = re.sub(r"```json|```", "", txt)
        txt = txt.strip()
        data = json.loads(txt)
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print("Mistral err: " + str(e))
        return []


def send_tg(text):
    if not TBOT or not TCHAT:
        print("Telegram not configured")
        return
    url = "https://api.telegram.org/bot"
    url = url + TBOT + "/sendMessage"
    chunks = []
    while len(text) > 4000:
        chunks.append(text[:4000])
        text = text[4000:]
    chunks.append(text)
    for chunk in chunks:
        payload = {
            "chat_id": TCHAT,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            r = requests.post(
                url,
                data=payload,
                timeout=30,
            )
            if r.status_code == 200:
                print("  Sent to TG")
            else:
                print("  TG err: " + r.text[:100])
            time.sleep(1)
        except Exception as e:
            print("  TG err: " + str(e))


def send_tg_doc(path, caption):
    if not TBOT or not TCHAT:
        return
    url = "https://api.telegram.org/bot"
    url = url + TBOT + "/sendDocument"
    payload = {
        "chat_id": TCHAT,
        "caption": caption[:1024],
    }
    try:
        with open(path, "rb") as f:
            files = {"document": f}
            r = requests.post(
                url,
                data=payload,
                files=files,
                timeout=60,
            )
        if r.status_code == 200:
            print("  Doc sent to TG")
    except Exception as e:
        print("  TG err: " + str(e))


def main():
    print("=" * 50)
    print("AI NEWS PIPELINE v8 
