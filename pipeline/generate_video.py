"""
Video Generator v6 - Stock Photos
"""

import os
import re
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
)
from gtts import gTTS

SW, SH = 1080, 1920
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

QUERIES = {
    "news": "technology news",
    "tool": "software coding",
    "research": "science laboratory",
    "discovery": "futuristic technology",
}


def gf(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def pause(text):
    t = re.sub(r"\.(\s)", r". ... \1", text)
    t = re.sub(r"\?(\s)", r"? ... \1", t)
    return t


def make_tts(text, path):
    text = pause(text)
    t = gTTS(text=text, lang="en", slow=False)
    t.save(path)
    return path


def wrap(text, w=28):
    return "\n".join(textwrap.wrap(text, width=w))


def get_stock_photos(query, count=6):
    if not PEXELS:
        return []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS}
    params = {
        "query": query,
        "per_page": count,
        "orientation": "portrait",
        "size": "medium",
    }
    try:
        r = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        photos = data.get("photos", [])
        urls = []
        for p in photos:
            src = p.get("src", {})
            u = src.get("large2x", src.get("large", ""))
            if u:
                urls.append(u)
        return urls
    except Exception as e:
        print("Pexels err: " + str(e))
        return []


def download_photo(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        img = img.convert("RGB")
        img = img.resize((SW, SH))
        return img
    except Exception as e:
        print("Download err: " + str(e))
        return None


def darken(img, factor=0.4):
    from PIL import ImageEnhance
    e = ImageEnhance.Brightness(img)
    return e.enhance(factor)


def blur_bg(img, radius=5):
    return img.filter(ImageFilter.GaussianBlur(radius))


COLORS = [
    (0, 180, 255),
    (255, 50, 150),
    (0, 230, 130),
    (170, 80, 255),
    (255, 160, 30),
    (50, 200, 220),
]


def make_solid_bg(idx=0):
    img = Image.new("RGB", (SW, SH), (15, 20, 35))
    draw = ImageDraw.Draw(img)
    for y in range(SH):
        shade = int(15 + (y / SH) * 25)
        draw.line(
            [(0, y), (SW, y)],
            fill=(shade, shade+5, shade+20)
        )
    return img


def overlay_intro(img, title, src, ct, ac):
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [(0, 0), (SW, SH)],
        fill=(0, 0, 0, 0)
    )
    f0 = gf(FB, 42)
    badge = ct.upper()
    bw = len(badge) * 26 + 30
    draw.rounded_rectangle(
        [(60, 250), (60+bw, 310)],
        radius=15, fill=ac
    )
    draw.text(
        (75, 257), badge,
        font=f0, fill=(10, 10, 10)
    )
    f1 = gf(FB, 52)
    draw.text(
        (60, 350), "AI DISCOVERY",
        font=f1, fill=ac
    )
    for i in range(6):
        c = (ac[0]//(i+1), ac[1]//(i+1), ac[2]//(i+1))
        draw.line(
            [(50, 430+i), (SW-50, 430+i)],
            fill=c, width=2
        )
    f2 = gf(FB, 68)
    draw.multiline_text(
        (60, 500), wrap(title, 15),
        font=f2,
        fill=(255, 255, 255),
        spacing=28
    )
    f3 = gf(FB, 34)
    draw.rounded_rectangle(
        [(60, SH-280), (420, SH-220)],
        radius=18, fill=ac
    )
    draw.text(
        (80, SH-270), src[:16],
        font=f3, fill=(10, 10, 10)
    )
    f4 = gf(FR, 32)
    draw.text(
        (60, SH-150),
        "Follow for daily AI updates!",
        font=f4, fill=(200, 200, 210)
    )
    draw.rectangle(
        [(0, SH-10), (SW, SH)], fill=ac
    )
    return img


def overlay_sentence(img, text, num, total, ac):
    draw = ImageDraw.Draw(img)
    f_num = gf(FB, 120)
    label = str(num) + "/" + str(total)
    draw.text(
        (SW-320, 120), label,
        font=f_num,
        fill=(ac[0]//2, ac[1]//2, ac[2]//2)
    )
    for i in range(6):
        c = (ac[0]//(i+1), ac[1]//(i+1), ac[2]//(i+1))
        draw.line(
            [(50, 350+i), (SW-50, 350+i)],
            fill=c, width=2
        )
    draw.rectangle(
        [(0, SH-40), (SW-120, SH-28)],
        fill=(40, 40, 50)
    )
    pw = int((num / total) * (SW - 120))
    draw.rectangle(
        [(0, SH-40), (pw, SH-28)],
        fill=ac
    )
    f_txt = gf(FB, 52)
    draw.multiline_text(
        (60, 500), wrap(text, 22),
        font=f_txt,
        fill=(255, 255, 255),
        spacing=26
    )
    bw = 8
    draw.rectangle([(0, 0), (bw, SH)], fill=ac)
    draw.rectangle(
        [(0, SH-10), (SW, SH)], fill=ac
    )
    return img


def overlay_outro(img, title, ac):
    draw = ImageDraw.Draw(img)
    f1 = gf(FB, 52)
    draw.multiline_text(
        (60, 400), wrap(title, 18),
        font=f1, fill=ac, spacing=24
    )
    for i in range(6):
        c = (ac[0]//(i+1), ac[1]//(i+1), ac[2]//(i+1))
        draw.line(
            [(50, 700+i), (SW-50, 700+i)],
            fill=c, width=2
        )
    f2 = gf(FB, 64)
    draw.text(
        (60, 800), "FOLLOW",
        font=f2, fill=(255, 255, 255)
    )
    draw.text(
        (60, 900), "for daily AI",
        font=f2, fill=(200, 200, 210)
    )
    draw.text(
        (60, 1000), "updates!",
        font=f2, fill=ac
    )
    draw.rectangle(
        [(0, SH-10), (SW, SH)], fill=ac
    )
    return img


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text)
    result = []
    for p in parts:
        p = p.strip()
        if len(p) > 10:
            result.append(p)
    if not result:
        result = [text]
    return result


def build_shorts_video(title, narr, src, out, ct="news"):
    tmp = os.path.dirname(out) or "."
    os.makedirs(tmp, exist_ok=True)
    ap = os.path.join(tmp, "_n.mp3")
    print("  Making voice...")
    make_tts(narr, ap)
    ac_clip = AudioFileClip(ap)
    dur = min(ac_clip.duration, 59.0)
    sentences = split_sentences(narr)
    n_scenes = len(sentences) + 2
    scene_dur = dur / n_scenes
    q = QUERIES.get(ct, "technology")
    print("  Fetching " + str(n_scenes) + " photos...")
    urls = get_stock_photos(q, n_scenes)
    ci = hash(title) % len(COLORS)
    accent = COLORS[ci]
    clips = []
    paths = []
    for s_idx in range(n_scenes):
        bg = None
        if s_idx < len(urls):
            bg = download_photo(urls[s_idx])
        if bg is None:
            bg = make_solid_bg(s_idx)
        bg = darken(bg, 0.35)
        bg = blur_bg(bg, 3)
        if s_idx == 0:
            bg = overlay_intro(
                bg, title, src, ct, accent
            )
        elif s_idx == n_scenes - 1:
            bg = overlay_outro(bg, title, accent)
        else:
            si = s_idx - 1
            if si < len(sentences):
                txt = sentences[si]
            else:
                txt = title
            bg = overlay_sentence(
                bg, txt, s_idx,
                n_scenes - 2, accent
            )
        fp = os.path.join(
            tmp, "_sc" + str(s_idx) + ".png"
        )
        bg.save(fp)
        paths.append(fp)
        start = scene_dur * s_idx
        c = ImageClip(fp).set_duration(scene_dur)
        c = c.set_start(start)
        clips.append(c)
    bg_clip = ColorClip(
        size=(SW, SH), color=(10, 10, 20)
    ).set_duration(dur)
    all_c = [bg_clip] + clips
    video = CompositeVideoClip(all_c, size=(SW, SH))
    video = video.set_audio(
        ac_clip.subclip(0, dur)
    )
    print("  Rendering...")
    video.write_videofile(
        out,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
        logger=None,
    )
    for f in paths + [ap]:
        try:
            os.remove(f)
        except Exception:
            pass
    print("  Done: " + out)
    return out


def build_long_video(items, out):
    tmp = os.path.dirname(out) or "."
    os.makedirs(tmp, exist_ok=True)
    clips = []
    for i, item in enumerate(items[:5]):
        t = item.get("title_short", "AI")
        n = item.get("narration", "")
        ct = item.get("type", "news")
        txt = "Number " + str(i+1) + ". " + t + ". " + n
        ap = os.path.join(tmp, "_a" + str(i) + ".mp3")
        make_tts(txt, ap)
        ac = AudioFileClip(ap)
        dur = ac.duration
        bg = make_solid_bg(i)
        ci = i % len(COLORS)
        bg = overlay_sentence(
            bg, n, i+1, 5, COLORS[ci]
        )
        fp = os.path.join(tmp, "_f" + str(i) + ".png")
        bg.save(fp)
        ic = ImageClip(fp).set_duration(dur)
        bgc = ColorClip(
            size=(1920, 1080), color=(15, 20, 35)
        ).set_duration(dur)
        seg = CompositeVideoClip(
            [bgc, ic], size=(1920, 1080)
        )
        seg = seg.set_audio(ac)
        clips.append(seg)
        for f in [ap, fp]:
            try:
                os.remove(f)
            except Exception:
                pass
    final = concatenate_videoclips(
        clips, method="compose"
    )
    final.write_videofile(
        out,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
        logger=None,
    )
    print("  Done: " + out)
    return out
