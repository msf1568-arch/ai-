"""
AI News Pipeline v3
"""

import os
import re
import json
import time
import traceback
import requests

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
        "start with hook question, "
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
        print("Mistral error: " + str(e))
        return []


def send_tg(vpath, caption):
    if not TBOT or not TCHAT:
        print("Telegram not configured")
        return
    url = "https://api.telegram.org/bot"
    url = url + TBOT + "/sendVideo"
    payload = {
        "chat_id": TCHAT,
        "caption": caption[:1024],
        "parse_mode": "HTML",
    }
    try:
        with open(vpath, "rb") as f:
            files = {"video": f}
            r = requests.post(
                url,
                data=payload,
                files=files,
                timeout=300,
            )
        if r.status_code == 200:
            print("Sent to Telegram!")
        else:
            print("TG err: " + r.text[:200])
    except Exception as e:
        print("TG err: " + str(e))


def main():
    print("=" * 50)
    print("AI NEWS PIPELINE v3")
    print("=" * 50)
    os.makedirs(OUTDIR, exist_ok=True)
    seen = load_seen()
    print(str(len(seen)) + " seen")

    print("\nFETCHING...")
    items = fetch_all_items(seen)
    if not items:
        print("No items.")
        return

    print("\nRANKING...")
    ranked = rank(items, count=MAX_S)
    if not ranked:
        print("No ranked.")
        return
    print(str(len(ranked)) + " selected")

    n = len(ranked)
    print("\nMAKING " + str(n) + " SHORTS...")
    ok = 0
    for i, item in enumerate(ranked):
        t = item.get("title_short", "AI Update")
        narr = item.get("narration", "")
        s = item.get("source", "AI")
        lk = item.get("link", "")
        ct = item.get("type", "news")
        vp = os.path.join(OUTDIR, "s" + str(i+1) + ".mp4")
        print("\n#" + str(i+1) + ": " + t)
        try:
            build_shorts_video(t, narr, s, vp, ct)
            cap = "<b>" + t + "</b>"
            cap = cap + "\n\n" + narr[:400]
            cap = cap + "\n\n" + lk
            send_tg(vp, cap)
            seen.add(lk)
            ok += 1
        except Exception as e:
            print("ERR: " + str(e))
            traceback.print_exc()
        time.sleep(2)

    save_seen(seen)
    msg = "DONE! " + str(ok) + "/" + str(n)
    print("\n" + msg)


if __name__ == "__main__":
    main()
