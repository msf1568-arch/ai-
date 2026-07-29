"""
Video Generator
"""

import os
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

SW = 1080
SH = 1920
LW = 1920
LH = 1080
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def make_tts(text, out_path):
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(out_path)
    return out_path


def wrap(text, w=28):
    return "\n".join(textwrap.wrap(text, width=w))


def type_color(t):
    c = {
        "news": (100, 200, 255),
        "tool": (100, 255, 150),
        "research": (255, 150, 100),
        "discovery": (200, 100, 255),
    }
    return c.get(t, (100, 200, 255))


def make_frame(title, summary, source, ctype="news"):
    bg = (15, 20, 35)
    img = Image.new("RGB", (SW, SH), color=bg)
    draw = ImageDraw.Draw(img)
    ac = type_color(ctype)

    f1 = get_font(FB, 52)
    draw.text((60, 100), "AI DISCOVERY", font=f1, fill=ac)
    draw.line([(60, 190), (SW - 60, 190)], fill=ac, width=4)

    f2 = get_font(FB, 68)
    t_text = wrap(title, 18)
    draw.multiline_text(
        (60, 300), t_text,
        font=f2, fill=(255, 255, 255), spacing=22
    )

    f3 = get_font(FR, 46)
    s_text = wrap(summary, 30)
    draw.multiline_text(
        (60, 800), s_text,
        font=f3, fill=(200, 210, 220), spacing=18
    )

    f4 = get_font(FB, 36)
    draw.rounded_rectangle(
        [(60, SH - 200), (500, SH - 130)],
        radius=20, fill=ac
    )
    draw.text(
        (90, SH - 185), source[:20],
        font=f4, fill=(20, 20, 30)
    )

    f5 = get_font(FR, 32)
    draw.text(
        (60, SH - 80),
        "Follow for more AI updates!",
        font=f5, fill=(150, 160, 180)
    )
    return img


def build_shorts_video(
    title, summary, source, output_path,
    content_type="news"
):
    tmp = os.path.dirname(output_path) or "."
    os.makedirs(tmp, exist_ok=True)

    narration = title + ". " + summary
    ap = os.path.join(tmp, "_narration.mp3")

    print("  Generating voice...")
    make_tts(narration, ap)
    ac = AudioFileClip(ap)
    dur = min(ac.duration + 1.5, 58.0)

    print("  Building frame...")
    frame = make_frame(
        title, summary, source, content_type
    )
    fp = os.path.join(tmp, "_frame.png")
    frame.save(fp)

    ic = ImageClip(fp).set_duration(dur)
    bg = ColorClip(
        size=(SW, SH), color=(15, 20, 35)
    ).set_duration(dur)
    video = CompositeVideoClip(
        [bg, ic], size=(SW, SH)
    )
    video = video.set_audio(ac.set_duration(dur))

    print("  Rendering video...")
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
        logger=None,
    )

    for f in [ap, fp]:
        try:
            os.remove(f)
        except Exception:
            pass

    print("  Saved: " + output_path)
    return output_path


def build_long_video(items, output_path):
    tmp = os.path.dirname(output_path) or "."
    os.makedirs(tmp, exist_ok=True)
    clips = []

    for i, item in enumerate(items[:5]):
        t = item.get("title_short", "AI Update")
        s = item.get("summary_short", "")
        narr = f"Number {i+1}: {t}. {s}"

        ap = os.path.join(tmp, f"_a{i}.mp3")
        make_tts(narr, ap)
        ac = AudioFileClip(ap)
        dur = ac.duration + 1.0

        img = Image.new("RGB", (LW, LH), (15, 20, 35))
        draw = ImageDraw.Draw(img)

        f1 = get_font(FB, 56)
        draw.multiline_text(
            (80, 150), wrap(t, 30),
            font=f1, fill=(255, 255, 255),
            spacing=18
        )

        f2 = get_font(FR, 40)
        draw.multiline_text(
            (80, 450), wrap(s, 50),
            font=f2, fill=(200, 210, 220),
            spacing=16
        )

        fp = os.path.join(tmp, f"_f{i}.png")
        img.save(fp)

        ic = ImageClip(fp).set_duration(dur)
        bg = ColorClip(
            size=(LW, LH), color=(15, 20, 35)
        ).set_duration(dur)
        seg = CompositeVideoClip(
            [bg, ic], size=(LW, LH)
        )
        seg = seg.set_audio(ac)
        clips.append(seg)

        for f in [ap, fp]:
            try:
                os.remove(f)
            except Exception:
                pass

    print(f"  Combining {len(clips)} segments...")
    final = concatenate_videoclips(
        clips, method="compose"
    )
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
        logger=None,
    )
    print("  Saved: " + output_path)
    return output_path
