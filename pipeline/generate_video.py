"""
Prompt Generator v9 - Dynamic Clips
"""

import os
import re
import json
import requests

MKEY = os.environ.get("MISTRAL_API_KEY", "")
API = "https://api.mistral.ai/v1/chat/completions"


def call_ai(prompt):
    if not MKEY:
        return ""
    headers = {
        "Authorization": "Bearer " + MKEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    try:
        r = requests.post(
            API, headers=headers,
            json=body, timeout=120,
        )
        r.raise_for_status()
        txt = r.json()
        return txt["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI err: " + str(e))
        return ""


PROMPT = """You are a world-class YouTube Shorts video director and viral content strategist.

TOPIC: {title}
FULL STORY: {narration}
SOURCE: {source}
CATEGORY: {ctype}

YOUR JOB: Create a COMPLETE video production package.

=== IMPORTANT RULES ===
1. Decide how many 8-second clips are needed to tell the FULL story (minimum 4, maximum 8)
2. First clip MUST be a pattern interrupt + hook
3. Each clip must have a NEW visual that moves the story forward
4. Last clip MUST loop back visually to clip 1
5. Content must be INTERESTING and ENGAGING for general audience
6. Avoid boring corporate language
7. Use emotional triggers: surprise, fear, curiosity, excitement
8. Every text overlay must be SHORT and PUNCHY (max 6 words)

=== VIDEO CLIP STRUCTURE ===
Clip 1: HOOK (shock/question/unexpected visual)
Clip 2: CONTEXT (set the scene)
Clip 3-N: STORY (reveal details one by one)
Last clip: CTA + LOOP TRIGGER

=== RETURN ONLY VALID JSON ===

Return this exact JSON structure:

{{"total_duration": "48 seconds",
"clip_count": 6,
"video_clips": [
{{"clip": 1,
"time": "0:00-0:08",
"role": "HOOK",
"video_prompt": "Detailed cinematic prompt for AI video generator. Include: exact camera angle and movement, lighting style, color palette, environment details, action happening, mood and atmosphere. Be very specific and visual.",
"text_overlay": "SHORT PUNCHY TEXT",
"voiceover_line": "What narrator says during this clip",
"transition": "cut/zoom/glitch/fade"}}
],
"thumbnail": {{
"image_prompt": "Detailed prompt for AI image generator: subject, expression, composition, lighting, colors, text placement. Optimized for CTR.",
"text": "2-4 WORDS MAX",
"style": "describe visual style"
}},
"youtube_title": "Catchy title under 60 chars with hook",
"caption": "Full YouTube description with hook line first then story summary then CTA with emojis",
"hashtags": "all hashtags in one line separated by spaces",
"posting_tip": "Best day and time to post",
"hooks": ["0:01 hook description", "0:15 mid hook", "0:40 end hook"]
}}"""


def generate_prompts(title, narr, src, ct):
    p = PROMPT.format(
        title=title,
        narration=narr,
        source=src,
        ctype=ct,
    )
    print("  Generating prompts...")
    resp = call_ai(p)
    cleaned = re.sub(r"```json|```", "", resp)
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
        return data
    except Exception:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"raw": resp}


def fmt(data, title, narr, link):
    lines = []
    lines.append("=" * 50)
    lines.append("VIDEO PACKAGE")
    lines.append("=" * 50)
    lines.append("")
    lines.append("TOPIC: " + title)
    lines.append("LINK: " + link)
    lines.append("")
    yt = data.get("youtube_title", "")
    if yt:
        lines.append("YT TITLE: " + yt)
        lines.append("")
    n = data.get("clip_count", "?")
    dur = data.get("total_duration", "?")
    lines.append("CLIPS: " + str(n))
    lines.append("DURATION: " + str(dur))
    lines.append("")
    lines.append("=" * 50)
    lines.append("VIDEO PROMPTS")
    lines.append("=" * 50)
    clips = data.get("video_clips", [])
    for c in clips:
        lines.append("")
        cn = c.get("clip", "?")
        lines.append("-- CLIP " + str(cn) + " --")
        lines.append("TIME: " + c.get("time", ""))
        lines.append("ROLE: " + c.get("role", ""))
        lines.append("")
        lines.append("PROMPT:")
        lines.append(c.get("video_prompt", ""))
        lines.append("")
        lines.append("TEXT: " + c.get("text_overlay", ""))
        lines.append("VOICE: " + c.get("voiceover_line", ""))
        lines.append("TRANS: " + c.get("transition", ""))
    lines.append("")
    lines.append("=" * 50)
    lines.append("THUMBNAIL")
    lines.append("=" * 50)
    th = data.get("thumbnail", {})
    lines.append("")
    lines.append("PROMPT:")
    lines.append(th.get("image_prompt", ""))
    lines.append("TEXT: " + th.get("text", ""))
    lines.append("STYLE: " + th.get("style", ""))
    lines.append("")
    lines.append("=" * 50)
    lines.append("CAPTION")
    lines.append("=" * 50)
    lines.append("")
    lines.append(data.get("caption", ""))
    lines.append("")
    lines.append("HASHTAGS:")
    lines.append(data.get("hashtags", ""))
    lines.append("")
    lines.append("POST TIP: " + data.get("posting_tip", ""))
    lines.append("")
    lines.append("HOOKS:")
    for h in data.get("hooks", []):
        lines.append("  " + h)
    lines.append("")
    lines.append("=" * 50)
    lines.append("VOICEOVER SCRIPT")
    lines.append("=" * 50)
    lines.append("")
    for c in clips:
        vo = c.get("voiceover_line", "")
        if vo:
            lines.append(vo)
    lines.append("")
    lines.append("=" * 50)
    return "\n".join(lines)


def build_shorts_video(title, narr, src, out, ct="news"):
    folder = out.replace(".mp4", "")
    os.makedirs(folder, exist_ok=True)
    data = generate_prompts(title, narr, src, ct)
    text = fmt(data, title, narr, src)
    tp = os.path.join(folder, "prompts.txt")
    with open(tp, "w", encoding="utf-8") as f:
        f.write(text)
    print("  Text saved: " + tp)
    jp = os.path.join(folder, "prompts.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("  JSON saved: " + jp)
    return folder, text, data


def build_long_video(items, out):
    all_t = []
    for i, item in enumerate(items[:5]):
        t = item.get("title_short", "AI")
        n = item.get("narration", "")
        s = item.get("source", "")
        ct = item.get("type", "news")
        p = out.replace(".mp4", "_" + str(i+1) + ".mp4")
        folder, text, data = build_shorts_video(
            t, n, s, p, ct
        )
        all_t.append(text)
    return "\n\n".join(all_t)
