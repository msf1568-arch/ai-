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


def generate_tts(text, out_path):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(out_path)
    return out_path


def wrap_text(text, width=28):
    return "\n".join(textwrap.wrap(text, width=width))


def get_type_color(content_type):
    colors = {
        "news": (100, 200, 255),
        "tool": (100, 255, 150),
        "research": (255, 150, 100),
        "discovery": (200, 100, 255),
    }
    return colors.get(content_type, (100, 200, 255))


def build_shorts_frame(title, summary, source, content_type="news"):
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
    draw.multiline_text((60, 800), wrap_text(summary, 30), font=font_body, fill=(200, 210
