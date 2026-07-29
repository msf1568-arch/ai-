"""
AI News Pipeline v9
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
API = "https://api.mistral.ai/v1/chat/completions"


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
        "You are an AI content curator "
        "for a YouTube Shorts channel. "
        "Pick TOP " + str(count) + " MOST "
        "ENGAGING and INTERESTING items "
        "from these " + str(len(batch)) + " items. "
        "Choose items that: "
        "1) Shock or surprise the audience "
        "2) Reveal something new or unknown "
        "3) Have real impact on peoples lives "
        "4) Create curiosity or debate "
        "5) Are trending right now. "
        "AVOID boring corporate announcements. "
        "For each return: "
        "title_short (catchy, under 10 words), "
        "narration (6-8 sentences, "
        "start with a powerful hook question, "
        "build tension, reveal the story, "
        "end with mind-blowing fact and CTA), "
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
            API, headers=headers,
            json=body, timeout=90,
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
        print("TG not configured")
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
        }
        try:
            r = requests.post(
                url, data=payload, timeout=30,
            )
            if r.status_code == 200:
                print("  Sent to TG")
            else:
                print("  TG: " + r.text[:100])
            time.sleep(1)
        except Exception as e:
            print("  TG: " + str(e))


def send_doc(path, cap):
    if not TBOT or not TCHAT:
        return
    url = "https://api.telegram.org/bot"
    url = url + TBOT + "/sendDocument"
    try:
        with open(path, "rb") as f:
            r = requests.post(
                url,
                data={"chat_id": TCHAT, "caption": cap},
                files={"document": f},
                timeout=60,
            )
        if r.status_code == 200:
            print("  Doc sent")
    except Exception as e:
        print("  Doc: " + str(e))


def main():
    print("=" * 40)
    print("AI NEWS v9")
    print("=" * 40)
    os.makedirs(OUTDIR, exist_ok=True)
    seen = load_seen()
    print(str(len(seen)) + " seen")
    print("Fetching...")
    items = fetch_all_items(seen)
    if not items:
        print("No items.")
        return
    print("Ranking...")
    ranked = rank(items, count=MAX_S)
    if not ranked:
        print("No ranked.")
        return
    print(str(len(ranked)) + " selected")
    ok = 0
    for i, item in enumerate(ranked):
        t = item.get("title_short", "AI")
        narr = item.get("narration", "")
        s = item.get("source", "AI")
        lk = item.get("link", "")
        ct = item.get("type", "news")
        vp = os.path.join(OUTDIR, "p" + str(i+1) + ".mp4")
        print("#" + str(i+1) + ": " + t)
        try:
            folder, text, data = build_shorts_video(
                t, narr, s, vp, ct
            )
            send_tg(text[:4000])
            jp = os.path.join(folder, "prompts.json")
            if os.path.exists(jp):
                send_doc(jp, t)
            seen.add(lk)
            ok += 1
        except Exception as e:
            print("ERR: " + str(e))
            traceback.print_exc()
        time.sleep(3)
    save_seen(seen)
    print("Done! " + str(ok) + "/" + str(len(ranked)))


if __name__ == "__main__":
    main()
