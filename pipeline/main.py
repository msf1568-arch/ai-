"""
AI News & Discovery Pipeline - Main
"""

import os
import re
import json
import time
import requests
import google.generativeai as genai

from sources import fetch_all_items
from generate_video import build_shorts_video, build_long_video

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

MAX_SHORTS = int(os.environ.get("MAX_SHORTS", "3"))
MAKE_LONG_VIDEO = os.environ.get("MAKE_LONG_VIDEO", "false").lower() == "true"

SEEN_FILE = "seen_links.json"
OUTPUT_DIR = "output"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def rank_with_gemini(items, count=10):
    if not items:
        return []
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    items_to_check = items[:30]
    prompt = f"""You are an AI content curator. Analyze these {len(items_to_check)} items.
Select TOP {count} most viral/important ones.
For each create: title_short (under 10 words), summary_short (2-3 sentences).
Return ONLY valid JSON array:
[{{"title_short": "...", "summary_short": "...", "link": "...", "source": "...", "type": "...", "score": 95}}]
ITEMS:
{json.dumps(items_to_check, ensure_ascii=False)}
"""
    try:
        response = model.generate_content(prompt)
        cleaned = re.sub(r'```json|```', '', response.text).strip()
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(cleaned)
    except Exception as e:
        print(f"Gemini error: {e}")
        return []


def send_to_telegram(video_path, caption):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    try:
        with open(video_path, "rb") as f:
            resp = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption[:1024], "parse_mode": "HTML"}, files={"video": f}, timeout=300)
        if resp.status_code == 200:
            print("Sent to Telegram!")
        else:
            print(f"Telegram error: {resp.text}")
    except Exception as e:
        print(f"Telegram error: {e}")


def main():
    print("=" * 50)
    print("AI NEWS & DISCOVERY PIPELINE")
    print("=" * 50)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    seen = load_seen()
    print(f"{len(seen)} previously processed")

    print("\nFETCHING FROM ALL SOURCES...")
    all_items = fetch_all_items(seen)
    if not all_items:
        print("No new items. Exiting.")
        return

    print("\nRANKING WITH GEMINI AI...")
    total_needed = MAX_SHORTS + (5 if MAKE_LONG_VIDEO else 0)
    ranked_items = rank_with_gemini(all_items, count=total_needed)
    if not ranked_items:
        print("No items passed ranking. Exiting.")
        return
    print(f"{len(ranked_items)} items selected")

    shorts_items = ranked_items[:MAX_SHORTS]
    long_items = ranked_items[MAX_SHORTS:MAX_SHORTS + 5] if MAKE_LONG_VIDEO else []

    print(f"\nCREATING {len(shorts_items)} YOUTUBE SHORTS...")
    shorts_created = 0
    for i, item in enumerate(shorts_items):
        title = item.get("title_short", "AI Update")
        summary = item.get("summary_short", "")
        source = item.get("source", "AI News")
        link = item.get("link", "")
        content_type = item.get("type", "news")
        video_path = os.path.join(OUTPUT_DIR, f"shorts_{i+1}.mp4")
        print(f"\nShorts {i+1}: {title}")
        try:
            build_shorts_video(title, summary, source, video_path, content_type)
            caption = f"<b>{title}</b>\n\n{summary}\n\n{link}"
            send_to_telegram(video_path, caption)
            seen.add(link)
            shorts_created += 1
        except Exception as e:
            print(f"Error: {e}")
            continue
        time.sleep(2)

    if MAKE_LONG_VIDEO and long_items:
        print("\nCREATING LONG VIDEO...")
        long_video_path = os.path.join(OUTPUT_DIR, "long_video.mp4")
        try:
            build_long_video(long_items, long_video_path)
            for item in long_items:
                seen.add(item.get("link", ""))
        except Exception as e:
            print(f"Long video error: {e}")

    save_seen(seen)
    print("\n" + "=" * 50)
    print(f"DONE! Shorts created: {shorts_created}")
    print("=" * 50)


if __name__ == "__main__":
    main()
