"""
اجرای کامل پایپ‌لاین در یک اسکریپت (برای اجرا در GitHub Actions)

مراحل:
1. گرفتن خبر از چند RSS
2. حذف موارد تکراری (بر اساس فایل seen_links.json که در ریپو ذخیره می‌شه)
3. فیلتر و ترجمه هر خبر با Gemini (حداکثر MAX_ITEMS مورد در هر اجرا)
4. ساخت ویدیو برای هر خبر تأییدشده
5. ارسال ویدیو + کپشن به تلگرام
"""

import os
import re
import json
import time
import requests
import feedparser

from generate_video import build_video

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "3"))
SEEN_FILE = "seen_links.json"
OUTPUT_DIR = "output"

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
]

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent?key=" + GEMINI_API_KEY
)


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


def ask_gemini(item):
    prompt = (
        "این خبر هوش مصنوعی رو بررسی کن:\n\n"
        f"تیتر: {item['title']}\nخلاصه: {item['summary']}\n\n"
        "به فارسی پاسخ بده، فقط JSON خام بدون توضیح اضافه و بدون backtick:\n"
        '{"is_relevant": true/false, "title_fa": "تیتر کوتاه و جذاب فارسی", '
        '"summary_fa": "خلاصه ۲-۳ جمله‌ای فارسی برای روایت صوتی"}\n\n'
        "is_relevant باید true باشه فقط اگه خبر واقعاً برای مخاطب عمومی علاقه‌مند "
        "به AI جذاب، دقیق، و بدون ابهام باشه. اگه کوچک‌ترین شکی داری، false بذار."
    )
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(GEMINI_URL, json=body, timeout=60)
    resp.raise_for_status()
    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
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
        print(f"⚠️ خطا در ارسال تلگرام: {resp.text}")
    else:
        print("✅ ویدیو در تلگرام ارسال شد")


def send_text_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=30)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    seen = load_seen()
    candidates = fetch_candidates(seen)
    print(f"{len(candidates)} خبر جدید پیدا شد.")

    made = 0
    for item in candidates:
        if made >= MAX_ITEMS:
            break

        seen.add(item["link"])  # حتی اگه رد بشه، دیگه دوباره چکش نمی‌کنیم

        try:
            result = ask_gemini(item)
        except Exception as e:
            print(f"خطا در فراخوانی Gemini برای «{item['title']}»: {e}")
            continue

        if not result.get("is_relevant"):
            print(f"رد شد (نامرتبط): {item['title']}")
            continue

        title_fa = result["title_fa"]
        summary_fa = result["summary_fa"]
        video_path = os.path.join(OUTPUT_DIR, f"video_{made+1}.mp4")

        try:
            build_video(title_fa, summary_fa, item["link"], video_path)
        except Exception as e:
            print(f"خطا در ساخت ویدیو برای «{title_fa}»: {e}")
            continue

        caption = f"📌 {title_fa}\n\n{summary_fa}\n\n🔗 {item['link']}"
        send_video_to_telegram(video_path, caption)
        made += 1
        time.sleep(2)

    save_seen(seen)

    if made == 0:
        print("هیچ ویدیویی در این اجرا ساخته نشد.")


if __name__ == "__main__":
    main()
