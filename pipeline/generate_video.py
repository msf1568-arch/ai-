"""
Video Generator - YouTube Shorts and Long format
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from gtts import gTTS

SHORTS_WIDTH, SHORTS_HEIGHT = 1080, 1920
LONG_WIDTH, LONG_HEIGHT = 1920, 1080
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def generate_tts(text: str, out_path: str) -> str:
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(out_path)
    return out_path


def wrap_text(text: str, width: int = 28) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def get_type_color(content_type: str) -> tuple:
    colors = {
        "news": (100, 200, 255),
        "tool": (100, 255, 150),
        "research": (255, 150, 100),
        "discovery": (200, 100, 255),
    }
    return colors.get(content_type, (100, 200, 255))


def build_shorts_frame(title: str, summary: str, source: str, content_type: str = "news") -> Image.Image:
    img = Image.new("RGB", (SHORTS_WIDTH, SHORTS_HEIGHT), color=(15, 20, 35))
    draw = ImageDraw.Draw(img)
    for i in range(SHORTS_HEIGHT):
        shade = int(15 + (i / SHORTS_HEIGHT) * 25)
        draw.line([(0, i), (SHORTS_WIDTH, i)], fill=(shade, shade + 5, shade + 20))
    accent_color = get_type_color(content_type)
    font_header = get_font(FONT_PATH_BOLD, 52)
    draw.text((60, 100), "AI DISCOVERY", font=font_header, fill=accent_color)
    draw.line([(60, 190), (SHORTS_WIDTH - 60, 190)], fill=accent_color, width=4)
    font_title = get_font(FONT_PATH_BOLD, 68)
    draw.multiline_text((60, 300), wrap_text(title, 18), font=font_title, fill=(255, 255, 255), spacing=22)
    font_body = get_font(FONT_PATH_REGULAR, 46)
    draw.multiline_text((60, 800), wrap_text(summary, 30), font=font_body, fill=(200, 210, 220), spacing=18)
    font_source = get_font(FONT_PATH_BOLD, 36)
    draw.rounded_rectangle([(60, SHORTS_HEIGHT - 200), (500, SHORTS_HEIGHT - 130)], radius=20, fill=accent_color)
    draw.text((90, SHORTS_HEIGHT - 185), source[:20], font=font_source, fill=(20, 20, 30))
    font_cta = get_font(FONT_PATH_REGULAR, 32)
    draw.text((60, SHORTS_HEIGHT - 80), "Follow for more AI updates!", font=font_cta, fill=(150, 160, 180))
    return img


def build_shorts_video(title: str, summary: str, source: str, output_path: str, content_type: str = "news"):
    tmp_dir = os.path.dirname(output_path) or "."
    os.makedirs(tmp_dir, exist_ok=True)
    narration = f"{title}. {summary}"
    audio_path = os.path.join(tmp_dir, "_narration.mp3")
    print("  Generating voice...")
    generate_tts(narration, audio_path)
    audio_clip = AudioFileClip(audio_path)
    duration = min(audio_clip.duration + 1.5, 58.0)
    print("  Building frame...")
    frame = build_shorts_frame(title, summary, source, content_type)
    frame_path = os.path.join(tmp_dir, "_frame.png")
    frame.save(frame_path)
    image_clip = (
        ImageClip(frame_path)
        .set_duration(duration)
        .resize(lambda t: 1 + 0.03 * (t / duration))
        .set_position("center")
    )
    background = ColorClip(size=(SHORTS_WIDTH, SHORTS_HEIGHT), color=(15, 20, 35)).set_duration(duration)
    video = CompositeVideoClip([background, image_clip], size=(SHORTS_WIDTH, SHORTS_HEIGHT))
    video = video.set_audio(audio_clip.set_duration(duration))
    print("  Rendering video...")
    video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", threads=2, preset="medium", logger=None)
    for f in [audio_path, frame_path]:
        try:
            os.remove(f)
        except:
            pass
    print(f"  Saved: {output_path}")
    return output_path


def build_long_video(items: list, output_path: str):
    tmp_dir = os.path.dirname(output_path) or "."
    os.makedirs(tmp_dir, exist_ok=True)
    clips = []
    for i, item in enumerate(items[:5]):
        title = item.get("title_short", item.get("title", "AI Update"))
        summary = item.get("summary_short", item.get("description", ""))
        narration = f"Number {i+1}: {title}. {summary}"
        audio_path = os.path.join(tmp_dir, f"_audio_{i}.mp3")
        generate_tts(narration, audio_path)
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration + 1.0
        img = Image.new("RGB", (LONG_WIDTH, LONG_HEIGHT), color=(15, 20, 35))
        draw = ImageDraw.Draw(img)
        for j in range(LONG_HEIGHT):
            shade = int(15 + (j / LONG_HEIGHT) * 20)
            draw.line([(0, j), (LONG_WIDTH, j)], fill=(shade, shade + 5, shade + 20))
        font_title = get_font(FONT_PATH_BOLD, 56)
        draw.multiline_text((80, 150), wrap_text(title, 30), font=font_title, fill=(255, 255, 255), spacing=18)
        font_body = get_font(FONT_PATH_REGULAR, 40)
        draw.multiline_text((80, 450), wrap_text(summary, 50), font=font_body, fill=(200, 210, 220), spacing=16)
        frame_path = os.path.join(tmp_dir, f"_frame_{i}.png")
        img.save(frame_path)
        image_clip = ImageClip(frame_path).set_duration(duration).set_position("center")
        background = ColorClip(size=(LONG_WIDTH, LONG_HEIGHT), color=(15, 20, 35)).set_duration(duration)
        segment = CompositeVideoClip([background, image_clip], size=(LONG_WIDTH, LONG_HEIGHT))
        segment = segment.set_audio(audio_clip)
        clips.append(segment)
        for f in [audio_path, frame_path]:
            try:
                os.remove(f)
            except:
                pass
    print(f"  Combining {len(clips)} segments...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", threads=2, preset="medium", logger=None)
    print(f"  Saved: {output_path}")
    return output_path
