"""
Professional Video Generator - AI Voice + Modern UI Card
"""

import os
import asyncio
import textwrap
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
)
import edge_tts

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
    async def _run():
        communicate = edge_tts.Communicate(
            text,
            voice="en-US-ChristopherNeural",
            rate="+4%",
            pitch="+0Hz",
        )
        await communicate.save(out_path)

    asyncio.run(_run())
    return out_path


def wrap(text, w=26):
    return "\n".join(textwrap.wrap(text, width=w))


def type_color(t):
    c = {
        "news": (56, 189, 248),
        "tool": (74, 222, 128),
        "research": (251, 146, 60),
        "discovery": (192, 132, 252),
    }
    return c.get(t, (56, 189, 248))


def make_frame(title, script, source, badge="🔥 BREAKING", ctype="news"):
    img = Image.new("RGB", (SW, SH), color=(10, 14, 23))
    draw = ImageDraw.Draw(img)
    ac = type_color(ctype)

    for i in range(SH):
        shade = int(10 + (i / SH) * 15)
        draw.line(
            [(0, i), (SW, i)],
            fill=(shade, shade + 3, shade + 10),
        )

    draw.rounded_rectangle(
        [(50, 160), (SW - 50, SH - 220)],
        radius=40,
        fill=(18, 24, 38),
        outline=(35, 45, 68),
        width=4,
    )

    draw.rounded_rectangle(
        [(90, 220), (450, 290)],
        radius=20,
        fill=ac,
    )
    f_badge = get_font(FB, 34)
    draw.text(
        (115, 238), badge[:18], font=f_badge, fill=(10, 14, 23)
    )

    f_title = get_font(FB, 62)
    t_text = wrap(title, 19)
    draw.multiline_text(
        (90, 330),
        t_text,
        font=f_title,
        fill=(255, 255, 255),
        spacing=20,
    )

    draw.line(
        [(90, 600), (SW - 90, 600)],
        fill=(35, 45, 68),
        width=3,
    )

    f_body = get_font(FR, 44)
    short_script = script[:350] + ("..." if len(script) > 350 else "")
    s_text = wrap(short_script, 29)
    draw.multiline_text(
        (90, 650),
        s_text,
        font=f_body,
        fill=(209, 213, 219),
        spacing=18,
    )

    f_src = get_font(FB, 36)
    draw.rounded_rectangle(
        [(90, SH - 330), (520, SH - 260)],
        radius=16,
        fill=(28, 36, 56),
    )
    draw.text(
        (120, SH - 315),
        "SOURCE: " + source[:15].upper(),
        font=f_src,
        fill=(148, 163, 184),
    )

    f_cta = get_font(FB, 38)
    draw.text(
        (SW // 2 - 200, SH - 140),
        "⚡ FOLLOW FOR DAILY AI UPDATES",
        font=f_cta,
        fill=ac,
    )

    return img


def build_shorts_video(
    title,
    script,
    source,
    output_path,
    badge="🔥 BREAKING",
    content_type="news",
):
    tmp = os.path.dirname(output_path) or "."
    os.makedirs(tmp, exist_ok=True)

    ap = os.path.join(tmp, "_narration.mp3")

    print("  Generating AI natural voice...")
    make_tts(script, ap)
    ac = AudioFileClip(ap)
    dur = min(ac.duration, 58.0)

    print("  Building modern UI card frame...")
    frame = make_frame(title, script, source, badge, content_type)
    fp = os.path.join(tmp, "_frame.png")
    frame.save(fp)

    ic = ImageClip(fp).set_duration(dur)
    bg = ColorClip(
        size=(SW, SH), color=(10, 14, 23)
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
        s = item.get("script", item.get("summary_short", ""))
        narr = f"Number {i+1}: {t}. {s}"

        ap = os.path.join(tmp, f"_a{i}.mp3")
        make_tts(narr, ap)
        ac = AudioFileClip(ap)
        dur = ac.duration

        img = Image.new("RGB", (LW, LH), (10, 14, 23))
        draw = ImageDraw.Draw(img)

        f1 = get_font(FB, 56)
        draw.multiline_text(
            (80, 150),
            wrap(t, 30),
            font=f1,
            fill=(255, 255, 255),
            spacing=18,
        )

        f2 = get_font(FR, 40)
        draw.multiline_text(
            (80, 450),
            wrap(s, 50),
            font=f2,
            fill=(209, 213, 219),
            spacing=16,
        )

        fp = os.path.join(tmp, f"_f{i}.png")
        img.save(fp)

        ic = ImageClip(fp).set_duration(dur)
        bg = ColorClip(
            size=(LW, LH), color=(10, 14, 23)
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
