"""
ساخت ویدیوی کوتاه از یک خبر (تیتر + خلاصه)
خروجی: MP4 عمودی 1080x1920 با صدای TTS و متن روی صفحه
"""

import os
import textwrap
import pyttsx3
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, ColorClip

WIDTH, HEIGHT = 1080, 1920
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def generate_tts(text: str, out_path: str) -> str:
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path


def wrap_text(text: str, width: int = 28) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def build_frame(title: str, summary: str, source: str) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(12, 18, 30))
    draw = ImageDraw.Draw(img)

    for i in range(HEIGHT):
        shade = int(12 + (i / HEIGHT) * 15)
        draw.line([(0, i), (WIDTH, i)], fill=(shade, shade + 6, shade + 18))

    font_header = ImageFont.truetype(FONT_PATH_BOLD, 42)
    draw.text((60, 90), "AI DAILY", font=font_header, fill=(232, 89, 60))

    font_title = ImageFont.truetype(FONT_PATH_BOLD, 64)
    draw.multiline_text(
        (60, 300), wrap_text(title, 20), font=font_title, fill=(255, 255, 255), spacing=18
    )

    draw.line([(60, 620), (WIDTH - 60, 620)], fill=(255, 255, 255, 60), width=2)

    font_body = ImageFont.truetype(FONT_PATH_REGULAR, 42)
    draw.multiline_text(
        (60, 680), wrap_text(summary, 34), font=font_body, fill=(220, 224, 230), spacing=16
    )

    font_small = ImageFont.truetype(FONT_PATH_REGULAR, 32)
    draw.text((60, HEIGHT - 100), f"source: {source}", font=font_small, fill=(150, 155, 165))

    return img


def build_video(title: str, summary: str, source: str, output_path: str):
    tmp_dir = os.path.dirname(output_path) or "."
    os.makedirs(tmp_dir, exist_ok=True)

    narration_text = f"{title}. {summary}"
    audio_path = os.path.join(tmp_dir, "_narration.wav")
    generate_tts(narration_text, audio_path)
    audio_clip = AudioFileClip(audio_path)
    duration = max(audio_clip.duration + 1.0, 6.0)

    frame = build_frame(title, summary, source)
    frame_path = os.path.join(tmp_dir, "_frame.png")
    frame.save(frame_path)

    image_clip = (
        ImageClip(frame_path)
        .set_duration(duration)
        .resize(lambda t: 1 + 0.03 * (t / duration))
        .set_position("center")
    )
    background = ColorClip(size=(WIDTH, HEIGHT), color=(12, 18, 30)).set_duration(duration)

    video = CompositeVideoClip([background, image_clip], size=(WIDTH, HEIGHT))
    video = video.set_audio(audio_clip.set_duration(duration))

    video.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac", threads=2, preset="medium",
        logger=None,
    )

    os.remove(audio_path)
    os.remove(frame_path)
    return output_path
