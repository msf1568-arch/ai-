"""
Prompt Generator v8 - Pro Video Prompts
"""

import os
import re
import json
import requests

MKEY = os.environ.get("MISTRAL_API_KEY", "")
API = "https://api.mistral.ai/v1/chat/completions"


def call_mistral(prompt):
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
            API,
            headers=headers,
            json=body,
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Mistral err: " + str(e))
        return ""


MASTER_PROMPT = '''You are an elite YouTube Shorts strategist and AI video prompt engineer.

TOPIC: {title}
NARRATION: {narration}
SOURCE: {source}
TYPE: {content_type}

Create a VIRAL YouTube Shorts content package.

=== RULES ===
- First 0.5 second = PATTERN INTERRUPT (zoom, flash, unexpected visual)
- Second 1-2 = HOOK (question, shock, curiosity gap)
- Every 8 seconds = NEW VISUAL STIMULUS
- Last 3 seconds = CTA + LOOP TRIGGER
- Use CONTRAST, MOVEMENT, FACES when possible
- Colors: High saturation, neon accents on dark backgrounds

=== OUTPUT FORMAT (JSON) ===
Return ONLY valid JSON:

{{
  "video_prompts": [
    {{
      "clip_number": 1,
      "duration": "0:00-0:08",
      "purpose": "HOOK - Grab attention instantly",
      "prompt": "[Detailed 8-second video prompt for AI generator. Include: camera movement, lighting, colors, mood, action, text overlay suggestion]",
      "text_overlay": "[Bold text to show on screen]",
      "transition_to_next": "[cut/zoom/fade/glitch]"
    }},
    {{
      "clip_number": 2,
      "duration": "0:08-0:16",
      "purpose": "PROBLEM/TENSION - Create curiosity",
      "prompt": "[Detailed prompt]",
      "text_overlay": "[Text]",
      "transition_to_next": "[transition]"
    }},
    {{
      "clip_number": 3,
      "duration": "0:16-0:24",
      "purpose": "REVEAL - Show the main content",
      "prompt": "[Detailed prompt]",
      "text_overlay": "[Text]",
      "transition_to_next": "[transition]"
    }},
    {{
      "clip_number": 4,
      "duration": "0:24-0:32",
      "purpose": "PROOF/DETAIL - Add credibility",
      "prompt": "[Detailed prompt]",
      "text_overlay": "[Text]",
      "transition_to_next": "[transition]"
    }},
    {{
      "clip_number": 5,
      "duration": "0:32-0:40",
      "purpose": "IMPACT - Why it matters",
      "prompt": "[Detailed prompt]",
      "text_overlay": "[Text]",
      "transition_to_next": "[transition]"
    }},
    {{
      "clip_number": 6,
      "duration": "0:40-0:48",
      "purpose": "CTA + LOOP - Drive action, make them rewatch",
      "prompt": "[Detailed prompt with loop element that
