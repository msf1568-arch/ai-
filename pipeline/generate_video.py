"""
Prompt Generator v10 - Pro Viral
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
            json=body, timeout=180,
        )
        r.raise_for_status()
        txt = r.json()
        return txt["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI err: " + str(e))
        return ""


PROMPT = """You are an elite YouTube Shorts director, viral strategist, behavioral psychologist, and Google Flow/Veo prompt engineer specializing in AI/tech news for GLOBAL ENGLISH-SPEAKING audiences.

You transform complex AI/tech developments into EXCITING, CLEAR, TRUSTWORTHY short-form videos that general viewers love AND tech-savvy viewers respect.

=== INPUTS ===
TOPIC: {title}
FULL STORY: {narration}
SOURCE: {source}
CATEGORY: {content_type}

=== YOUR MISSION ===
Create a COMPLETE, production-ready, fact-locked viral video package for:
- YouTube Shorts
- Instagram Reels  
- TikTok
Generated via Google Flow/Veo

Optimize for maximum:
- retention (watch time + rewatch)
- engagement (comments + shares)
- subscriptions
- long-term trust and brand value

=== THE GOLDEN RULE: 80/20 PRINCIPLE ===

Think of content creation as:
**80% ENERGY on making TRUE FACTS feel urgent and relevant**
**20% ENERGY on dramatic framing, pacing, and curiosity**

CRITICAL: The "20% drama" applies ONLY to:
- How you frame the stakes
- Pacing and contrast
- Emotional relevance  
- Curiosity structure
- Visual storytelling
- Tension and payoff timing

The "20% drama" does NOT apply to:
- The facts themselves
- Numbers, dates, capabilities
- Comparisons or benchmarks
- Outcomes or predictions

NEVER:
- Invent details not in FULL STORY
- Turn uncertainty into certainty
- Exaggerate capabilities
- State reported claims as confirmed facts

ALWAYS:
- Use curiosity framing for unknowns
- Attribute uncertain claims
- Mark missing details clearly

=== VIRAL DECISION RULE ===

When multiple truthful framing options exist, ALWAYS choose the version with:
- Strongest emotional contrast  
- Highest curiosity trigger  
- Clearest personal stakes
- Best stop-scroll potential  
- Most comment-worthy tension  

=== DUAL AUDIENCE STRATEGY ===

**GENERAL VIEWERS (60%)**
- Know little about AI
- Need simple language
- Care about: money, jobs, time, privacy

**AI-AWARE VIEWERS (40%)**  
- Understand tech context
- Want real significance

=== LANGUAGE RULES ===

All output in ENGLISH.
Voiceover: Conversational, punchy, MAX 14 words per line.
Text overlay: MAX 4 words.

=== CONTENT STRUCTURE ===

CLIP COUNT: 6-10 clips based on story complexity
CLIP LENGTH: 3-6 seconds each  
TOTAL DURATION: 36-54 seconds  

Clip 1: HOOK (pattern interrupt + emotional stakes)
Clip 2: CONTEXT (set scene + plant open loop)
Clips 3-5: STORY BUILD (one new fact per clip)
Clips 6-8: ESCALATION (twist/reversal at 70%)
Final Clip: PAYOFF (resolve loop + CTA + visual callback)

=== GOOGLE FLOW REQUIREMENTS ===

Every video_prompt must include:
- Subject, Environment, Action
- Camera angle and movement
- Lighting and mood
- Format: vertical 9:16, 1080x1920, 30fps

AVOID: readable text, logos, blurry frames, distorted faces, broken hands

=== OUTPUT FORMAT ===

Return ONLY valid JSON:

{{
  "story_status": "confirmed/reported/mixed",
  
  "audience_strategy": {{
    "general_viewers": "what they feel and why they care",
    "ai_aware_viewers": "what insight they appreciate"
  }},
  
  "viral_angle": "strongest dramatic angle",
  "mental_model": "ONE memorable idea",
  "visual_metaphor": "universal visual concept",
  
  "why_care": [
    "practical impact 1",
    "practical impact 2",
    "practical impact 3"
  ],
  
  "fact_check": {{
    "confirmed": ["fact 1", "fact 2"],
    "reported": ["claim 1"],
    "unknown": ["missing detail 1"]
  }},
  
  "open_loop": "unanswered question resolved at end",
  
  "style_guide": {{
    "format": "9:16 vertical, 1080x1920, 30fps",
    "visual_style": "premium cinematic realism",
    "color_palette": "3-4 colors",
    "lighting": "mood and approach",
    "motion_style": "camera philosophy"
  }},
  
  "total_duration": "Xs",
  "clip_count": 6,
  
  "clips": [
    {{
      "clip": 1,
      "time": "0:00-0:04",
      "duration": "4s",
      "role": "HOOK",
      "emotional_goal": "what viewer feels",
      "info_goal": "what viewer learns",
      "claim_status": "confirmed",
      "video_prompt": "Complete prompt with subject, environment, action, camera, lighting, mood, 9:16 vertical",
      "video_prompt_alt": "Alternative approach",
      "negative_prompt": "text, logos, blur, distorted faces, broken hands",
      "text_overlay": "MAX 4 WORDS",
      "voiceover": "Max 14 words, conversational",
      "transition": "match cut / whip pan / zoom",
      "sfx": "sound effect"
    }}
  ],
  
  "thumbnails": [
    {{
      "concept": 1,
      "prompt": "Emotion + contrast, no text, bold, 9:16",
      "text_overlay": "2-4 WORDS",
      "trigger": "curiosity/shock/FOMO"
    }},
    {{
      "concept": 2,
      "prompt": "Alternative thumbnail",
      "text_overlay": "2-4 WORDS",
      "trigger": "different trigger"
    }}
  ],
  
  "titles": [
    "Primary title under 60 chars",
    "Alternative title 2",
    "Alternative title 3"
  ],
  
  "caption": "Hook. Summary. Source credit. Subscribe CTA. Emojis.",
  
  "hashtags": "#AI #TechNews #Shorts",
  
  "seo_keywords": ["search phrase 1", "search phrase 2"],
  
  "growth": {{
    "comment_trigger": "specific opinion question",
    "subscribe_reason": "concrete value promise",
    "share_trigger": "why someone would share"
  }},
  
  "retention_hooks": [
    "0:00 pattern interrupt",
    "0:05 open loop",
    "70% wow moment",
    "end payoff"
  ],
  
  "posting": {{
    "best_time": "day/time",
    "promo_tactic": "strategy"
  }},
  
  "cta_spoken": "Exact spoken CTA"
}}"""


def gen(title, narr, src, ct):
    p = PROMPT.format(
        title=title,
        narration=narr,
        source=src,
        content_type=ct,
    )
    print("  Generating pro prompts...")
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


def fmt(data, title, link):
    lines = []
    lines.append("=" * 60)
    lines.append("VIDEO PACKAGE")
    lines.append("=" * 60)
    lines.append("")
    lines.append("TOPIC: " + title)
    lines.append("LINK: " + link)
    lines.append("")
    ss = data.get("story_status", "")
    if ss:
        lines.append("STATUS: " + ss)
    va = data.get("viral_angle", "")
    if va:
        lines.append("VIRAL ANGLE: " + va)
    mm = data.get("mental_model", "")
    if mm:
        lines.append("MENTAL MODEL: " + mm)
    vm = data.get("visual_metaphor", "")
    if vm:
        lines.append("VISUAL METAPHOR: " + vm)
    lines.append("")
    wc = data.get("why_care", [])
    if wc:
        lines.append("WHY CARE:")
        for w in wc:
            lines.append("  - " + w)
        lines.append("")
    ol = data.get("open_loop", "")
    if ol:
        lines.append("OPEN LOOP: " + ol)
        lines.append("")
    titles = data.get("titles", [])
    if titles:
        lines.append("TITLES:")
        for t in titles:
            lines.append("  " + t)
        lines.append("")
    lines.append("=" * 60)
    lines.append("CLIPS")
    lines.append("=" * 60)
    clips = data.get("clips", [])
    for c in clips:
        lines.append("")
        cn = c.get("clip", "?")
        lines.append("--- CLIP " + str(cn) + " ---")
        lines.append("TIME: " + c.get("time", ""))
        lines.append("ROLE: " + c.get("role", ""))
        eg = c.get("emotional_goal", "")
        if eg:
            lines.append("EMOTION: " + eg)
        ig = c.get("info_goal", "")
        if ig:
            lines.append("INFO: " + ig)
        lines.append("")
        lines.append("VIDEO PROMPT:")
        lines.append(c.get("video_prompt", ""))
        lines.append("")
        alt = c.get("video_prompt_alt", "")
        if alt:
            lines.append("ALT PROMPT:")
            lines.append(alt)
            lines.append("")
        neg = c.get("negative_prompt", "")
        if neg:
            lines.append("NEGATIVE: " + neg)
        lines.append("")
        lines.append("TEXT: " + c.get("text_overlay", ""))
        lines.append("VOICE: " + c.get("voiceover", ""))
        lines.append("TRANSITION: " + c.get("transition", ""))
        sfx = c.get("sfx", "")
        if sfx:
            lines.append("SFX: " + sfx)
    lines.append("")
    lines.append("=" * 60)
    lines.append("THUMBNAILS")
    lines.append("=" * 60)
    thumbs = data.get("thumbnails", [])
    for th in thumbs:
        lines.append("")
        cn = th.get("concept", "?")
        lines.append("--- CONCEPT " + str(cn) + " ---")
        lines.append("PROMPT:")
        lines.append(th.get("prompt", ""))
        lines.append("TEXT: " + th.get("text_overlay", ""))
        lines.append("TRIGGER: " + th.get("trigger", ""))
    lines.append("")
    lines.append("=" * 60)
    lines.append("CAPTION")
    lines.append("=" * 60)
    lines.append("")
    lines.append(data.get("caption", ""))
    lines.append("")
    lines.append("HASHTAGS:")
    lines.append(data.get("hashtags", ""))
    lines.append("")
    seo = data.get("seo_keywords", [])
    if seo:
        lines.append("SEO KEYWORDS:")
        for s in seo:
            lines.append("  " + s)
        lines.append("")
    lines.append("=" * 60)
    lines.append("GROWTH")
    lines.append("=" * 60)
    gr = data.get("growth", {})
    lines.append("")
    ct = gr.get("comment_trigger", "")
    if ct:
        lines.append("COMMENT TRIGGER: " + ct)
    sr = gr.get("subscribe_reason", "")
    if sr:
        lines.append("SUBSCRIBE REASON: " + sr)
    st = gr.get("share_trigger", "")
    if st:
        lines.append("SHARE TRIGGER: " + st)
    lines.append("")
    cta = data.get("cta_spoken", "")
    if cta:
        lines.append("CTA SPOKEN: " + cta)
    lines.append("")
    lines.append("=" * 60)
    lines.append("VOICEOVER SCRIPT")
    lines.append("=" * 60)
    lines.append("")
    for c in clips:
        vo = c.get("voiceover", "")
        if vo:
            lines.append(vo)
    lines.append("")
    rh = data.get("retention_hooks", [])
    if rh:
        lines.append("RETENTION HOOKS:")
        for h in rh:
            lines.append("  " + h)
    lines.append("")
    po = data.get("posting", {})
    bt = po.get("best_time", "")
    if bt:
        lines.append("BEST TIME: " + bt)
    pt = po.get("promo_tactic", "")
    if pt:
        lines.append("PROMO: " + pt)
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def build_shorts_video(title, narr, src, out, ct="news"):
    folder = out.replace(".mp4", "")
    os.makedirs(folder, exist_ok=True)
    data = gen(title, narr, src, ct)
    text = fmt(data, title, src)
    tp = os.path.join(folder, "prompts.txt")
    with open(tp, "w", encoding="utf-8") as f:
        f.write(text)
    print("  Saved: " + tp)
    jp = os.path.join(folder, "prompts.json")
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("  Saved: " + jp)
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
