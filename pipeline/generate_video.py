"""
Prompt Generator v12 - Full Pro
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
        "max_tokens": 8000,
    }
    try:
        r = requests.post(
            API, headers=headers,
            json=body, timeout=200,
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
Voiceover: Conversational, MAX 14 words per line.
Text overlay: MAX 4 words.

=== CONTENT STRUCTURE ===

**CLIP COUNT: NO LIMIT - decide based on story complexity**
- Simple news: 4-6 clips
- Medium story: 7-10 clips
- Complex story: 11-15 clips
- Breaking news with many facts: up to 20 clips

**EACH CLIP DURATION: exactly 7 seconds**

**STRUCTURE:**
- Clip 1: HOOK (pattern interrupt + emotional stakes)
- Clip 2: CONTEXT (set scene + plant open loop)
- Middle clips: BUILD (one new fact per clip)
- 70% mark: WOW moment (twist/reversal)
- Final clip: PAYOFF (resolve loop + CTA + visual callback to clip 1)

=== GOOGLE FLOW REQUIREMENTS ===

Each video_prompt MUST include:
- Subject (who/what)
- Environment (where)
- Action (doing what)
- Camera angle (low/high/eye-level)
- Camera movement (push in/pull out/static/pan)
- Lighting (mood, direction, color)
- Emotion/mood
- VOICE: [exact words to speak - max 14 words]
- Format: vertical 9:16, 1080x1920, cinematic
- Negative: text, logos, blur, distorted faces, broken hands

=== FACT SAFETY ===

Before writing, categorize:
- CONFIRMED: Can state as fact
- REPORTED: Use "according to...", "reports suggest..."
- UNKNOWN: Use "it's unclear...", "the exact number..."

=== OUTPUT FORMAT ===

Return ONLY valid JSON:

{{
  "story_analysis": {{
    "complexity": "simple/medium/complex",
    "key_facts_count": 0,
    "recommended_clips": 0,
    "reasoning": "why this many clips needed"
  }},
  
  "viral_angle": "strongest dramatic angle",
  "mental_model": "ONE memorable idea viewers remember",
  "open_loop": "question planted early, answered at end",
  
  "why_care": [
    "impact on money/jobs",
    "impact on daily life", 
    "impact on future"
  ],
  
  "fact_check": {{
    "confirmed": ["verified fact 1", "verified fact 2"],
    "reported": ["unverified claim 1"],
    "unknown": ["missing detail 1"]
  }},
  
  "style_guide": {{
    "visual_style": "cinematic/documentary/dramatic",
    "color_palette": "main colors used",
    "mood": "overall emotional tone",
    "pacing": "fast/medium/slow"
  }},
  
  "total_duration": "Xs",
  "clip_count": 0,
  
  "clips": [
    {{
      "clip": 1,
      "time": "0:00-0:07",
      "duration": "7s",
      "role": "HOOK/CONTEXT/BUILD/ESCALATE/PAYOFF",
      "emotional_goal": "what viewer feels",
      "info_goal": "what viewer learns",
      "claim_status": "confirmed/reported/unknown",
      "video_prompt": "Complete prompt: [subject] in [environment], [action], [camera angle], [movement], [lighting], [mood], vertical 9:16, cinematic. VOICE: [exact words max 14]. Negative: text, logos, blur, distorted faces, broken hands, extra fingers.",
      "text_overlay": "MAX 4 WORDS",
      "transition": "cut/zoom in/zoom out/whip pan/match cut",
      "sfx": "sound effect suggestion"
    }}
  ],
  
  "thumbnail": {{
    "prompt": "Detailed prompt: [subject with clear emotion], [composition using rule of thirds], [dramatic lighting], [bold colors], [simple background], no text in image, 16:9 horizontal, high contrast, optimized for mobile CTR",
    "text_to_add": "2-4 WORDS to overlay",
    "emotion": "shock/curiosity/excitement"
  }},
  
  "youtube": {{
    "title": "Catchy title under 60 chars with curiosity hook",
    "caption": "Hook sentence grabbing attention. 2-3 sentences telling the story simply. Source: {source}. Follow for daily AI news you can trust! Emojis.",
    "hashtags": "#shorts #ai #technews #viral #artificialintelligence"
  }},
  
  "seo_keywords": [
    "search phrase 1",
    "search phrase 2",
    "search phrase 3"
  ],
  
  "growth": {{
    "comment_trigger": "specific opinion question",
    "subscribe_reason": "concrete value promise",
    "share_trigger": "why someone sends to friend"
  }},
  
  "retention_hooks": [
    "0:01 - pattern interrupt description",
    "clip 2 - open loop description", 
    "70% - wow moment description",
    "end - payoff description"
  ],
  
  "posting": {{
    "best_time": "day and time",
    "reason": "why this time"
  }},
  
  "voiceover_full": "Complete script combining all VOICE texts in order",
  
  "cta_spoken": "Exact final CTA spoken naturally"
}}"""


def gen(title, narr, src, ct):
    p = PROMPT.format(
        title=title,
        narration=narr,
        source=src,
        content_type=ct,
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


def fmt(data, title, src):
    lines = []
    lines.append("=" * 60)
    lines.append("VIDEO PRODUCTION PACKAGE")
    lines.append("=" * 60)
    lines.append("")
    lines.append("TOPIC: " + title)
    lines.append("SOURCE: " + src)
    lines.append("")
    sa = data.get("story_analysis", {})
    if sa:
        lines.append("STORY ANALYSIS:")
        lines.append("  Complexity: " + sa.get("complexity", ""))
        lines.append("  Key Facts: " + str(sa.get("key_facts_count", "")))
        lines.append("  Clips Needed: " + str(sa.get("recommended_clips", "")))
        lines.append("  Reason: " + sa.get("reasoning", ""))
        lines.append("")
    va = data.get("viral_angle", "")
    if va:
        lines.append("VIRAL ANGLE: " + va)
    mm = data.get("mental_model", "")
    if mm:
        lines.append("MEMORABLE IDEA: " + mm)
    ol = data.get("open_loop", "")
    if ol:
        lines.append("OPEN LOOP: " + ol)
    lines.append("")
    wc = data.get("why_care", [])
    if wc:
        lines.append("WHY VIEWERS CARE:")
        for w in wc:
            lines.append("  - " + w)
        lines.append("")
    fc = data.get("fact_check", {})
    if fc:
        lines.append("FACT CHECK:")
        conf = fc.get("confirmed", [])
        if conf:
            lines.append("  Confirmed:")
            for c in conf:
                lines.append("    * " + c)
        rep = fc.get("reported", [])
        if rep:
            lines.append("  Reported (not verified):")
            for r in rep:
                lines.append("    ? " + r)
        unk = fc.get("unknown", [])
        if unk:
            lines.append("  Unknown:")
            for u in unk:
                lines.append("    - " + u)
        lines.append("")
    sg = data.get("style_guide", {})
    if sg:
        lines.append("STYLE GUIDE:")
        lines.append("  Visual: " + sg.get("visual_style", ""))
        lines.append("  Colors: " + sg.get("color_palette", ""))
        lines.append("  Mood: " + sg.get("mood", ""))
        lines.append("  Pacing: " + sg.get("pacing", ""))
        lines.append("")
    dur = data.get("total_duration", "")
    cn = data.get("clip_count", "")
    lines.append("TOTAL DURATION: " + str(dur))
    lines.append("TOTAL CLIPS: " + str(cn))
    lines.append("")
    lines.append("=" * 60)
    lines.append("VIDEO PROMPTS FOR GOOGLE FLOW")
    lines.append("=" * 60)
    clips = data.get("clips", [])
    for c in clips:
        lines.append("")
        n = c.get("clip", "?")
        lines.append("-" * 50)
        lines.append("CLIP " + str(n) + " | " + c.get("role", ""))
        lines.append("-" * 50)
        lines.append("TIME: " + c.get("time", ""))
        lines.append("DURATION: " + c.get("duration", ""))
        eg = c.get("emotional_goal", "")
        if eg:
            lines.append("EMOTION: " + eg)
        ig = c.get("info_goal", "")
        if ig:
            lines.append("INFO: " + ig)
        cs = c.get("claim_status", "")
        if cs:
            lines.append("STATUS: " + cs)
        lines.append("")
        lines.append(">>> COPY THIS TO GOOGLE FLOW:")
        lines.append("")
        lines.append(c.get("video_prompt", ""))
        lines.append("")
        lines.append("<<<")
        lines.append("")
        to = c.get("text_overlay", "")
        if to:
            lines.append("TEXT OVERLAY: " + to)
        tr = c.get("transition", "")
        if tr:
            lines.append("TRANSITION: " + tr)
        sfx = c.get("sfx", "")
        if sfx:
            lines.append("SFX: " + sfx)
    lines.append("")
    lines.append("=" * 60)
    lines.append("THUMBNAIL")
    lines.append("=" * 60)
    th = data.get("thumbnail", {})
    lines.append("")
    lines.append(">>> COPY THIS TO IMAGE AI:")
    lines.append("")
    lines.append(th.get("prompt", ""))
    lines.append("")
    lines.append("<<<")
    lines.append("")
    tta = th.get("text_to_add", "")
    if tta:
        lines.append("ADD THIS TEXT: " + tta)
    em = th.get("emotion", "")
    if em:
        lines.append("EMOTION: " + em)
    lines.append("")
    lines.append("=" * 60)
    lines.append("YOUTUBE DETAILS")
    lines.append("=" * 60)
    yt = data.get("youtube", {})
    lines.append("")
    lines.append("TITLE:")
    lines.append(yt.get("title", ""))
    lines.append("")
    lines.append("CAPTION:")
    lines.append(yt.get("caption", ""))
    lines.append("")
    lines.append("HASHTAGS:")
    lines.append(yt.get("hashtags", ""))
    lines.append("")
    seo = data.get("seo_keywords", [])
    if seo:
        lines.append("SEO KEYWORDS:")
        for s in seo:
            lines.append("  " + s)
        lines.append("")
    lines.append("=" * 60)
    lines.append("GROWTH STRATEGY")
    lines.append("=" * 60)
    gr = data.get("growth", {})
    lines.append("")
    ct_q = gr.get("comment_trigger", "")
    if ct_q:
        lines.append("ASK: " + ct_q)
    sr = gr.get("subscribe_reason", "")
    if sr:
        lines.append("WHY SUBSCRIBE: " + sr)
    sht = gr.get("share_trigger", "")
    if sht:
        lines.append("WHY SHARE: " + sht)
    lines.append("")
    rh = data.get("retention_hooks", [])
    if rh:
        lines.append("RETENTION HOOKS:")
        for h in rh:
            lines.append("  " + h)
        lines.append("")
    po = data.get("posting", {})
    if po:
        lines.append("BEST TIME: " + po.get("best_time", ""))
        lines.append("REASON: " + po.get("reason", ""))
        lines.append("")
    lines.append("=" * 60)
    lines.append("COMPLETE VOICEOVER SCRIPT")
    lines.append("=" * 60)
    lines.append("")
    vf = data.get("voiceover_full", "")
    if vf:
        lines.append(vf)
    else:
        for c in clips:
            vp = c.get("video_prompt", "")
            vm = re.search(r"VOICE:\s*(.+?)(?:Negative|$)", vp, re.IGNORECASE)
            if vm:
                lines.append(vm.group(1).strip())
    lines.append("")
    cta = data.get("cta_spoken", "")
    if cta:
        lines.append("FINAL CTA: " + cta)
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
