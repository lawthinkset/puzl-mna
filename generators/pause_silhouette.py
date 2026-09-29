import os
import math
import random
from typing import Dict, Any, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

from core.ui_renderer import (
    get_font,
    draw_gradient_background,
    draw_header_banner,
    draw_timer_bar,
    draw_bottom_cta,
    draw_fitted_card
)
from generators.base_generator import BaseGenerator

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"

def create_smooth_outline(rgba_img: Image.Image, color_rgb=(56, 189, 248), thickness=8) -> Image.Image:
    """Draws an anti-aliased outline around transparent RGBA sprite."""
    img_np = np.array(rgba_img)
    h, w = img_np.shape[:2]
    alpha = img_np[:, :, 3]
    _, thresh = cv2.threshold(alpha, 35, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    rgba = (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 255)
    cv2.drawContours(canvas, contours, -1, rgba, thickness=thickness, lineType=cv2.LINE_AA)
    return Image.fromarray(canvas, mode="RGBA")

MOTION_PATTERNS = [
    "elliptical_orbit",
    "laser_ricochet",
    "harmonic_pendulum",
    "zoom_pulse",
    "figure_eight"
]

class PauseSilhouetteGenerator(BaseGenerator):
    """
    Generates microsecond 'Pause when it fits the shadow' reflex challenges.
    Employs 5 distinct motion dynamics and rotates across 100+ 3D assets.
    14-second duration. NEVER stops automatically—forces viewers to pause on mobile and comment proof.
    """
    def __init__(self, page_name: str = "BrainFocus Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        pngs = list(ASSETS_DIR.glob("*.png"))
        valid_pngs = [p for p in pngs if not p.stem.endswith("_outline") and not p.stem.endswith("_test")]
        chosen_png = random.choice(valid_pngs) if valid_pngs else None

        sprite_img = None
        outline_img = None
        sprite_name = "Target Item"
        if chosen_png and chosen_png.exists():
            try:
                sprite_name = chosen_png.stem.replace("_", " ").title()
                raw = Image.open(chosen_png).convert("RGBA")
                s_size = 400
                raw.thumbnail((s_size, s_size), Image.Resampling.LANCZOS)
                sprite_img = raw
                outline_color = random.choice([(56, 189, 248), (234, 179, 8), (239, 68, 68), (34, 197, 94)])
                outline_img = create_smooth_outline(raw, color_rgb=outline_color, thickness=8)
            except Exception:
                sprite_img = None
                outline_img = None

        pattern = random.choice(MOTION_PATTERNS)
        speed_factor = random.uniform(0.7, 1.2)

        return {
            "sprite_img": sprite_img,
            "outline_img": outline_img,
            "sprite_name": sprite_name,
            "pattern": pattern,
            "speed": speed_factor,
            "title": f"STOP THE {sprite_name.upper()} IN SHADOW!"
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        if not self.puzzle_data:
            self.puzzle_data = self.generate_puzzle_state()
        state = self.puzzle_data

        # 1. Base gradient
        pil_frame = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(pil_frame)

        # 2. Header and 14s timer
        draw_header_banner(
            draw=draw,
            title=state["title"],
            badge_text="1% REFLEX",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        cx = self.width // 2
        cy = 900

        # Center Target Reticle Rings
        draw.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], outline=(51, 65, 85, 100), width=4)
        draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], fill=(30, 41, 59, 80), outline=(56, 189, 248, 140), width=3)
        draw.line([cx - 310, cy, cx - 240, cy], fill=(56, 189, 248, 180), width=4)
        draw.line([cx + 240, cy, cx + 310, cy], fill=(56, 189, 248, 180), width=4)
        draw.line([cx, cy - 310, cx, cy - 240], fill=(56, 189, 248, 180), width=4)
        draw.line([cx, cy + 240, cx, cy + 310], fill=(56, 189, 248, 180), width=4)

        sprite = state["sprite_img"]
        outline = state["outline_img"]

        if sprite and outline:
            sw, sh = sprite.size
            
            # Stationary Target Outline in center
            target_x = cx - sw // 2
            target_y = cy - sh // 2
            pil_frame.paste(outline, (target_x, target_y), outline)

            # Procedural Motion Dynamics
            pat = state["pattern"]
            spd = state["speed"]
            freq = 0.5 * spd
            
            if pat == "elliptical_orbit":
                dx = 380.0 * math.cos(2 * math.pi * freq * t)
                dy = 240.0 * math.sin(2 * math.pi * freq * t)
            elif pat == "laser_ricochet":
                # Multi-harmonic bounce
                dx = 400.0 * math.sin(2 * math.pi * freq * 1.3 * t)
                dy = 350.0 * math.cos(2 * math.pi * freq * 0.9 * t)
            elif pat == "harmonic_pendulum":
                dx = 420.0 * math.sin(2 * math.pi * freq * t)
                dy = 120.0 * (1.0 - math.cos(4 * math.pi * freq * t))
            elif pat == "figure_eight":
                dx = 380.0 * math.sin(2 * math.pi * freq * t)
                dy = 220.0 * math.sin(4 * math.pi * freq * t)
            else:  # zoom_pulse
                dx = 0.0
                dy = 360.0 * math.sin(2 * math.pi * freq * t)

            curr_x = int(target_x + dx)
            curr_y = int(target_y + dy)

            pil_frame.paste(sprite, (curr_x, curr_y), sprite)

        # 3. Microsecond Precision Callout Card (Guaranteed no overflow)
        draw_fitted_card(
            draw=draw,
            cx=self.width // 2,
            cy=1430,
            text="TAP SCREEN TO PAUSE THE EXACT FRAME!",
            max_font_size=36,
            min_font_size=24,
            max_width=980,
            padding_x=36,
            padding_y=22,
            fill_color=(15, 23, 42, 235),
            border_color=(56, 189, 248),
            border_width=3,
            corner_radius=22,
            text_color=(255, 255, 255)
        )

        # 4. Bottom Viral CTA (Never stops—forces pause!)
        cta_msg = "POST YOUR SCREENSHOT IN COMMENTS!"
        draw_bottom_cta(
            draw=draw,
            t=t,
            duration=duration,
            custom_cta=cta_msg,
            width=self.width,
            height=self.height
        )

        np_frame = np.array(pil_frame)
        return cv2.cvtColor(np_frame[:, :, :3], cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        state = self.puzzle_data
        name = state.get("sprite_name", "Target")

        title = f"Can You Stop The {name} Inside The Shadow? 🎯"
        
        description = (
            f"⚡ Microsecond reaction test!\n"
            f"99% fail to stop the {name} inside the exact glowing outline!\n\n"
            f"1. Tap screen to pause.\n"
            f"2. Take a screenshot.\n"
            f"3. Drop your screenshot in the comments below! 👇\n\n"
            f"Only 1% get a 100% perfect match! 🏆\n\n"
            f"#BrainFocus #PauseChallenge #ReflexTest #Precision #MindGames #ViralReels"
        )
        
        pinned_comment = (
            f"🎯 100% MATCH CHALLENGE:\n"
            f"Tap pause when it aligns and post your screenshot below! 👇\n"
            f"Did you hit it on your 1st try? 🏆"
        )
        
        return title, description, pinned_comment
