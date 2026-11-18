"""High-contrast numeric badge that stays legible at Windows tray sizes."""

from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont


def render(percent=None, *, online=False, charging=False, threshold=20):
    canvas = Image.new('RGBA', (64, 64))
    draw = ImageDraw.Draw(canvas)
    color = '#96a0ac' if not online else (
        '#33d19b' if charging else '#ff6268' if percent <= 10 else
        '#ffc454' if percent <= threshold else '#63c7ff')
    # A dark backing keeps the digits readable on both light and dark taskbars.
    draw.rounded_rectangle((1, 1, 62, 62), radius=12, fill='#17212e', outline=color, width=2)
    label = '?' if percent is None else str(percent)
    size = 36 if len(label) == 3 else 45
    font = None
    for path in (Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/seguisb.ttf',
                 Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')):
        try:
            font = ImageFont.truetype(str(path), size)
            break
        except OSError:
            pass
    if font is None:
        font = ImageFont.load_default(size=size)
    draw.text((32, 27), label, font=font, fill=color, anchor='mm', stroke_width=0)
    draw.rounded_rectangle((10, 51, 53, 56), radius=2, fill='#394451')
    if percent:
        draw.rounded_rectangle((10, 51, 10 + max(3, round(43 * percent / 100)), 56),
                               radius=2, fill=color)
    if charging:
        draw.polygon([(53, 3), (47, 13), (52, 13), (49, 21), (59, 10), (54, 10)], fill='#ffffff')
    return canvas
