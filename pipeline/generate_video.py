"""
Video Generator v4 - Stable
"""

import os
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont
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


def gf(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def pause(text):
    t = re.sub(r"\.(\s)", r". ... \1", text)
    t = re.sub(r"\?(\s)", r"? ... \1", t)
    return t


def tts(text, path):
    text = pause(text)
    t = gTTS(text=text, lang="en", slow=False)
    t.save(path)
    return path


def wrap(text, w=28):
    return "\n".join(textwrap.wrap(text, width=w))


def colors(t):
    c = {
        "news": ((30, 60, 120), (0, 180, 255)),
        "tool": ((20, 80, 60), (0, 255, 150)),
        "research": ((80, 40, 20), (255, 120, 50)),
        "discovery": ((60, 20, 80), (180, 80, 255)),
    }
    return c.get(t, c["news"])


def grad(draw, w, h, c1, c2):
    for y in range(h):
        r = c1[0] + (c2[0] - c1[0]) * y // h
        g = c1[1] + (c2[1] - c1[1]) * y // h
        b = c1[2] + (c2[2] - c1[2]) * y // h
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def dots(draw, w, h, col, n=20):
    import random
    random.seed(42)
    for _ in range(n):
        x = random.randint(0, w)
        y = random.randint(0, h)
        s = random.randint(3, 8)
        draw.ellipse([(x, y), (x+s, y+s)], fill=col)


def frame1(title, src, ct="news"):
    dk, ac = colors(ct)
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img)
    c1 = dk
    c2 = (dk[0]//2, dk[1]//2, dk[2]//2)
    grad(draw, SW, SH, c1, c2)
    gl = (ac[0]//4, ac[1]//4, ac[2]//4)
    dots(draw, SW, SH, gl, 25)
    f0 = gf(FB, 40)
    badge = ct.upper()
    bw = len(badge) * 26 + 30
    draw.rounded_rectangle(
        [(60, 100), (60+bw, 155)],
        radius=15, fill=ac
    )
    draw.text((75, 107), badge, font=f0, fill=(10,10,10))
    f1 = gf(FB, 50)
    draw.text((60, 180), "AI DISCOVERY", font=f1, fill=ac)
    for i in range(5):
        c = (ac[0]//(i+1), ac[1]//(i+1), ac[2]//(i+1))
        draw.line([(50, 260+i), (SW-50, 260+i)], fill=c)
    f2 = gf(FB, 62)
    draw.multiline_text(
        (60, 320), wrap(title, 17),
        font=f2, fill=(255,255,255), spacing=26
    )
    f4 = gf(FB, 32)
    draw.rounded_rectangle(
        [(60, SH-240), (420, SH-180)],
        radius=18, fill=ac
    )
    draw.text((80, SH-230), src[:16], font=f4, fill=(10,10,10))
    f5 = gf(FR, 28)
    draw.text(
        (60, SH-120),
        "Follow for daily AI updates!",
        font=f5, fill=(160,165,180)
    )
    draw.rectangle([(0, SH-8), (SW, SH)], fill=ac)
    return img


def frame2(title, narr, ct="news"):
    dk, ac = colors(ct)
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img)
    c1 = dk
    c2 = (dk[0]//2, dk[1]//2, dk[2]//2)
    grad(draw, SW, SH, c1, c2)
    dots(draw, SW, SH, ac, 12)
    f1 = gf(FB, 44)
    draw.multiline_text(
        (60, 180), wrap(title, 20),
        font=f1, fill=ac, spacing=20
    )
    for i in range(5):
        c = (ac[0]//(i+1), ac[1]//(i+1), ac[2]//(i+1))
        draw.line([(50, 450+i), (SW-50, 450+i)], fill=c)
    clean = re.sub(r"\.\.\.", "", narr)
    f2 = gf(FR, 38)
    draw.multiline_text(
        (60, 520), wrap(clean, 28),
        font=f2, fill=(215,220,230), spacing=20
    )
    draw.rectangle([(0, SH-8), (SW, SH)], fill=ac)
    return img


def build_shorts_video(title, narr, src, out, ct="news"):
    tmp = os.path.dirname(out) or "."
    os.makedirs(tmp, exist_ok=True)
    ap = os.path.join(tmp, "_n.mp3")
    print("  Making voice...")
    tts(narr, ap)
    ac = AudioFileClip(ap)
    dur = min(ac.duration, 59.0)
    half = dur / 2.0
    print("  Making frames...")
    f1 = frame1(title, src, ct)
    p1 = os.path.join(tmp, "_f1.png")
    f1.save(p1)
    f2 = frame2(title, narr, ct)
    p2 = os.path.join(tmp, "_f2.png")
    f2.save(p2)
    c1 = ImageClip(p1).set_duration(half)
    c2 = ImageClip(p2).set_duration(dur - half)
    c2 = c2.set_start(half)
    bg = ColorClip(
        size=(SW, SH), color=(10, 10, 20)
    ).set_duration(dur)
    video = CompositeVideoClip([bg, c1, c2], size=(SW, SH))
    video = video.set_audio(ac.subclip(0, dur))
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
    for f in [ap, p1, p2]:
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
        tts(txt, ap)
        ac = AudioFileClip(ap)
        dur = ac.duration
        img = frame2(t, n, ct)
        fp = os.path.join(tmp, "_f" + str(i) + ".png")
        img.save(fp)
        ic = ImageClip(fp).set_duration(dur)
        bg = ColorClip(
            size=(1920, 1080), color=(15, 20, 35)
        ).set_duration(dur)
        seg = CompositeVideoClip([bg, ic], size=(1920, 1080))
        seg = seg.set_audio(ac)
        clips.append(seg)
        for f in [ap, fp]:
            try:
                os.remove(f)
            except Exception:
                pass
    final = concatenate_videoclips(clips, method="compose")
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
