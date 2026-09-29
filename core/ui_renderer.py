import os
import math
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
FONT_PATH = BASE_DIR / "assets" / "fonts" / "font_bold.ttf"

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Loads bold font with Windows/system fallbacks."""
    if FONT_PATH.exists():
        try:
            return ImageFont.truetype(str(FONT_PATH), size)
        except Exception:
            pass
    for win_font in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\impact.ttf"]:
        if os.path.exists(win_font):
            try:
                return ImageFont.truetype(win_font, size)
            except Exception:
                pass
    return ImageFont.load_default()

def clean_ascii_text(text: str) -> str:
    """Strips non-ascii emojis that produce missing-glyph square boxes in fonts."""
    clean = "".join(c for c in text if ord(c) < 128).strip()
    return clean if clean else text

def draw_gradient_background(
    width: int = 1080,
    height: int = 1920,
    theme: str = "dark_slate"
) -> Image.Image:
    """
    Renders high-end studio gradient backgrounds:
    - 'dark_slate': Modern tech dark mode (slate to deep charcoal)
    - 'vibrant_navy': Deep navy to cosmic indigo
    - 'clean_light': Studio vignette off-white to cool gray
    - 'deep_purple': Premium dark violet gradient
    """
    y, x = np.ogrid[:height, :width]
    
    if theme == "clean_light":
        y, x = np.ogrid[:height, :width]
        cx, cy = width / 2, height * 0.45
        dist = np.clip(np.hypot(x - cx, y - cy) / (height * 0.7), 0.0, 1.0)
        c_center = np.array([255, 255, 255], dtype=np.float32)
        c_edge = np.array([220, 226, 238], dtype=np.float32)
        bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    else:
        if theme == "vibrant_navy":
            c_top = np.array([12, 18, 38], dtype=np.float32)       # Deep navy
            c_bot = np.array([24, 34, 68], dtype=np.float32)       # Indigo
        elif theme == "deep_purple":
            c_top = np.array([18, 10, 32], dtype=np.float32)
            c_bot = np.array([38, 16, 64], dtype=np.float32)
        else:  # dark_slate (default)
            c_top = np.array([15, 23, 42], dtype=np.float32)       # Slate 900
            c_bot = np.array([2, 6, 23], dtype=np.float32)         # Slate 950

        col = np.linspace(c_top, c_bot, height, dtype=np.float32)
        bg_np = np.repeat(col[:, np.newaxis, :], width, axis=1).astype(np.uint8)

    return Image.fromarray(bg_np, mode="RGB").convert("RGBA")

def draw_header_banner(
    draw: ImageDraw.ImageDraw,
    title: str,
    badge_text: str = "99% FAIL",
    page_name: Optional[str] = None,
    width: int = 1080
):
    """Draws top title card, viral badges, and optional page tag."""
    top_y = 110
    card_h = 135
    card_w = width - 80
    card_x1 = 40
    card_x2 = card_x1 + card_w
    
    # Glow/Shadow
    draw.rounded_rectangle([card_x1 + 3, top_y + 6, card_x2 + 3, top_y + card_h + 6], radius=24, fill=(0, 0, 0, 100))
    # Card surface
    draw.rounded_rectangle([card_x1, top_y, card_x2, top_y + card_h], radius=24, fill=(255, 255, 255, 250), outline=(226, 232, 240, 255), width=3)
    
    # Title Text
    clean_title = title.upper()
    font_size = 50
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), clean_title, font=font)
    tw = bbox[2] - bbox[0]
    while tw > (card_w - 60) and font_size > 32:
        font_size -= 2
        font = get_font(font_size)
        bbox = draw.textbbox((0, 0), clean_title, font=font)
        tw = bbox[2] - bbox[0]
        
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = top_y + (card_h - th) // 2 - bbox[1]
    draw.text((tx, ty), clean_title, fill=(15, 23, 42), font=font)
    
    # Sub-badges below card
    badge_y = top_y + card_h + 18
    b_font = get_font(30)
    
    # Left Badge (e.g. 99% FAIL)
    bw1 = 250
    draw.rounded_rectangle([42, badge_y, 42 + bw1, badge_y + 54], radius=16, fill=(225, 29, 72))
    b1_box = draw.textbbox((0, 0), badge_text, font=b_font)
    draw.text((42 + (bw1 - (b1_box[2]-b1_box[0]))//2, badge_y + (54 - (b1_box[3]-b1_box[1]))//2 - b1_box[1]), badge_text, fill=(255, 255, 255), font=b_font)
    
    # Right Badge (e.g. page name or "FIND IT FAST")
    right_text = page_name.upper() if page_name else "COMMENT YOUR ANSWER"
    b2_box = draw.textbbox((0, 0), right_text, font=b_font)
    bw2 = max(290, (b2_box[2] - b2_box[0]) + 40)
    bx2 = width - 42 - bw2
    draw.rounded_rectangle([bx2, badge_y, bx2 + bw2, badge_y + 54], radius=16, fill=(14, 116, 244))
    draw.text((bx2 + (bw2 - (b2_box[2]-b2_box[0]))//2, badge_y + (54 - (b2_box[3]-b2_box[1]))//2 - b2_box[1]), right_text, fill=(255, 255, 255), font=b_font)

def draw_timer_bar(
    draw: ImageDraw.ImageDraw,
    t: float,
    duration: float = 14.0,
    width: int = 1080,
    bar_y: int = 345,
    bar_h: int = 18,
    margin_x: int = 50
):
    """Draws a smooth animated neon countdown progress bar across duration."""
    bar_w = width - (margin_x * 2)
    # Background track
    draw.rounded_rectangle([margin_x, bar_y, margin_x + bar_w, bar_y + bar_h], radius=bar_h//2, fill=(51, 65, 85, 200))
    
    # Remaining percentage
    ratio = max(0.0, min(1.0, 1.0 - (t / duration)))
    fill_w = int(bar_w * ratio)
    
    if fill_w > 4:
        # Dynamic color shift: Cyan -> Yellow -> Intense Red
        if ratio > 0.4:
            bar_color = (6, 182, 212)       # Cyan
        elif ratio > 0.2:
            bar_color = (234, 179, 8)       # Amber / Yellow
        else:
            # Pulsing red urgency in final 20% of time
            pulse = math.sin(t * 14) * 0.5 + 0.5
            bar_color = (239, 68, 68) if pulse > 0.4 else (220, 38, 38)
            
        draw.rounded_rectangle([margin_x, bar_y, margin_x + fill_w, bar_y + bar_h], radius=bar_h//2, fill=bar_color)

def draw_bottom_cta(
    draw: ImageDraw.ImageDraw,
    t: float = 0.0,
    duration: float = 14.0,
    custom_cta: Optional[str] = None,
    width: int = 1080,
    height: int = 1920
):
    """
    Draws bottom viral engagement CTA bar.
    Dynamically shifts to high-urgency callout in the final 3.5 seconds.
    """
    bot_y = height - 210
    font = get_font(36)
    
    if t > (duration - 3.5):
        # High urgency final callout
        cta_text = "TIME IS UP! COMMENT YOUR ANSWER BELOW!"
        border_c = (239, 68, 68)
        pill_fill = (35, 15, 20, 245)
    else:
        cta_text = custom_cta or "COMMENT YOUR ANSWER BEFORE TIME RUNS OUT!"
        border_c = (56, 189, 248)
        pill_fill = (15, 23, 42, 240)

    clean_cta = clean_ascii_text(cta_text).upper()
    bbox = draw.textbbox((0, 0), clean_cta, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    bar_w = min(width - 80, tw + 80)
    bar_h = 76
    bx1 = (width - bar_w) // 2
    bx2 = bx1 + bar_w
    
    # Drop shadow
    draw.rounded_rectangle([bx1 + 3, bot_y + 4, bx2 + 3, bot_y + bar_h + 4], radius=22, fill=(0, 0, 0, 90))
    # Pill
    draw.rounded_rectangle([bx1, bot_y, bx2, bot_y + bar_h], radius=22, fill=pill_fill, outline=border_c, width=3)
    # Text
    draw.text((bx1 + (bar_w - tw) // 2, bot_y + (bar_h - th) // 2 - bbox[1]), clean_cta, fill=(255, 255, 255), font=font)

def draw_multiple_choice_options(
    draw: ImageDraw.ImageDraw,
    options: List[str],
    width: int = 1080,
    center_y: int = 1480
):
    """
    Renders 4 distinct multiple-choice option cards:
    Options: [opt0, opt1, opt2, opt3].
    Maintains clean interactive challenge buttons throughout the entire video.
    """
    n = len(options)
    btn_w = 210
    btn_h = 100
    spacing = 24
    total_w = n * btn_w + (n - 1) * spacing
    start_x = (width - total_w) // 2
    font = get_font(44)
    
    for i, opt in enumerate(options):
        bx1 = start_x + i * (btn_w + spacing)
        bx2 = bx1 + btn_w
        by1 = center_y - btn_h // 2
        by2 = by1 + btn_h
        
        fill_color = (30, 41, 59, 235)  # Slate dark
        border_color = (100, 116, 139, 180)
        text_color = (241, 245, 249)
            
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=18, fill=fill_color, outline=border_color, width=3)
        
        tbox = draw.textbbox((0, 0), opt, font=font)
        otw = tbox[2] - tbox[0]
        oth = tbox[3] - tbox[1]
        draw.text((bx1 + (btn_w - otw) // 2, by1 + (btn_h - oth) // 2 - tbox[1]), opt, fill=text_color, font=font)
