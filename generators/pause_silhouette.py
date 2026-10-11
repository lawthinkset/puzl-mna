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

def make_solid_silhouette(rgba_img: Image.Image, color_rgba=(15, 23, 42, 240)) -> Image.Image:
    """Creates a crisp solid dark shadow silhouette from transparent RGBA sprite."""
    alpha = rgba_img.split()[-1]
    silhouette = Image.new("RGBA", rgba_img.size, color_rgba)
    silhouette.putalpha(alpha)
    return silhouette

MOTION_PATTERNS = [
    "orbital_crossing",
    "figure_eight",
    "laser_sweep",
    "harmonic_pendulum",
    "spiral_cycloid"
]

class PauseSilhouetteGenerator(BaseGenerator):
    """
    Generates microsecond 'Pause when it fits the shadow' reflex challenges.
    Employs 5 dynamic motion trajectories that revolve and sweep directly through the center silhouette.
    14-second duration. NEVER stops automatically—forces viewers to pause on mobile and comment proof.
    """
    def __init__(self, page_name: str = "BrainFocus Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        EXCLUDED_STEMS = {
            "japanese_here_button", "japanese_open_for_business_button",
            "keycap_5", "one_oclock", "empty_nest", "parrot_outline_test",
            "pause_button", "upwards_button", "green_square", "wilted_flower"
        }
        pngs = list(ASSETS_DIR.glob("*.png"))
        valid_pngs = [
            p for p in pngs 
            if not p.stem.endswith("_outline") 
            and not p.stem.endswith("_test")
            and p.stem.lower() not in EXCLUDED_STEMS
        ]
        chosen_png = random.choice(valid_pngs) if valid_pngs else None

        sprite_img = None
        shadow_img = None
        outline_img = None
        sprite_name = "Target Item"
        if chosen_png and chosen_png.exists():
            try:
                sprite_name = chosen_png.stem.replace("_", " ").title()
                raw = Image.open(chosen_png).convert("RGBA")
                s_size = 380
                raw.thumbnail((s_size, s_size), Image.Resampling.LANCZOS)
                sprite_img = raw
                outline_color = random.choice([(56, 189, 248), (234, 179, 8), (34, 197, 94), (244, 63, 94)])
                outline_img = create_smooth_outline(raw, color_rgb=outline_color, thickness=8)
                shadow_img = make_solid_silhouette(raw, color_rgba=(12, 18, 32, 235))
            except Exception:
                sprite_img = None
                shadow_img = None
                outline_img = None

        pattern = random.choice(MOTION_PATTERNS)
        speed_factor = random.uniform(0.9, 1.1)

        return {
            "sprite_img": sprite_img,
            "shadow_img": shadow_img,
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
        draw.ellipse([cx - 310, cy - 310, cx + 310, cy + 310], outline=(51, 65, 85, 100), width=4)
        draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], fill=(20, 28, 48, 120), outline=(56, 189, 248, 140), width=3)
        draw.line([cx - 320, cy, cx - 240, cy], fill=(56, 189, 248, 200), width=4)
        draw.line([cx + 240, cy, cx + 320, cy], fill=(56, 189, 248, 200), width=4)
        draw.line([cx, cy - 320, cx, cy - 240], fill=(56, 189, 248, 200), width=4)
        draw.line([cx, cy + 240, cx, cy + 320], fill=(56, 189, 248, 200), width=4)

        sprite = state["sprite_img"]
        outline = state["outline_img"]

        if sprite and outline:
            sw, sh = sprite.size
            
            # Stationary Target Outline in center
            target_x = cx - sw // 2
            target_y = cy - sh // 2

            # Compute procedural trajectory guaranteed to repeatedly pass through center (dx=0, dy=0)
            pat = state["pattern"]
            spd = state["speed"]
            freq = 0.35 * spd
            
            if pat == "orbital_crossing":
                # Orbiting while pulsing radius through 0 (passes directly through shadow)
                f_spin = 0.7 * spd
                f_pulse = 0.35 * spd
                R = 380.0 * math.sin(2 * math.pi * f_pulse * t)
                theta = 2 * math.pi * f_spin * t
                dx = R * math.cos(theta)
                dy = R * math.sin(theta)
            elif pat == "figure_eight":
                # Lissajous infinity curve passing directly through (0, 0)
                dx = 380.0 * math.sin(2 * math.pi * freq * t)
                dy = 240.0 * math.sin(4 * math.pi * freq * t)
            elif pat == "laser_sweep":
                # Multi-angle linear sweep cutting through center (0, 0)
                angle = 0.4 * math.pi * math.floor(freq * 2 * t)
                sweep = 400.0 * math.sin(2 * math.pi * freq * t)
                dx = sweep * math.cos(angle)
                dy = sweep * math.sin(angle)
            elif pat == "harmonic_pendulum":
                # Pendulum swing passing through (0, 0) at apex of swing
                max_angle = 0.75
                theta = max_angle * math.sin(2 * math.pi * freq * t)
                L = 400.0
                dx = L * math.sin(theta)
                dy = -L * (1.0 - math.cos(theta))
            else:  # spiral_cycloid
                # Multi-petal rose curve looping through center (0, 0)
                R = 360.0 * math.sin(3 * 2 * math.pi * (freq / 2) * t)
                theta = 2 * math.pi * freq * t
                dx = R * math.cos(theta)
                dy = R * math.sin(theta)

            dist_to_center = math.hypot(dx, dy)
            
            # Draw shadow outline (with alignment flash if sprite is inside target)
            if dist_to_center < 35.0:
                # Brief subtle glowing pulse at the exact moment of alignment
                draw.ellipse([cx - 250, cy - 250, cx + 250, cy + 250], outline=(234, 179, 8, 180), width=6)

            shadow = state.get("shadow_img")
            if shadow:
                pil_frame.paste(shadow, (target_x, target_y), shadow)
            pil_frame.paste(outline, (target_x, target_y), outline)

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
