import os
import math
import random
from typing import Dict, Any, Tuple, List
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cv2

from core.ui_renderer import (
    get_font,
    draw_gradient_background,
    draw_header_banner,
    draw_timer_bar,
    draw_bottom_cta
)
from generators.base_generator import BaseGenerator

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"

def make_solid_silhouette(rgba_img: Image.Image) -> Image.Image:
    """Creates a crisp solid black silhouette from transparent RGBA image."""
    alpha = rgba_img.split()[-1]
    black = Image.new("RGBA", rgba_img.size, (15, 23, 42, 255))
    black.putalpha(alpha)
    return black

class ShadowGlitchGenerator(BaseGenerator):
    """
    Generates 'Which Shadow is Wrong?' impostor puzzle reels.
    Center hero asset + 4 silhouette options (A, B, C, D) with 1 subtle anomaly.
    14-second duration. NEVER reveals the impostor shadow—sparks heavy debate.
    """
    def __init__(self, page_name: str = "MindView Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        pngs = list(ASSETS_DIR.glob("*.png"))
        valid_pngs = [p for p in pngs if not p.stem.endswith("_outline") and not p.stem.endswith("_test")]
        chosen_png = random.choice(valid_pngs) if valid_pngs else None

        hero_img = None
        hero_name = "Character"
        if chosen_png and chosen_png.exists():
            try:
                hero_name = chosen_png.stem.replace("_", " ").title()
                raw = Image.open(chosen_png).convert("RGBA")
                raw.thumbnail((320, 320), Image.Resampling.LANCZOS)
                hero_img = raw
            except Exception:
                hero_img = None

        # Shadow options: A, B, C, D
        impostor_idx = random.randint(0, 3)
        glitch_type = random.choice(["mirror_x", "rotate_slight", "vertical_flip", "shear"])

        return {
            "hero_img": hero_img,
            "hero_name": hero_name,
            "impostor_idx": impostor_idx,
            "glitch_type": glitch_type,
            "title": "WHICH SHADOW IS WRONG?"
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        state = self.puzzle_data

        # 1. Base gradient
        pil_frame = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(pil_frame)

        # 2. Header and 14s timer
        draw_header_banner(
            draw=draw,
            title=state["title"],
            badge_text="SHADOW IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Center Hero Object Showcase Box
        cx = self.width // 2
        cy = 620
        box_w = 400
        box_h = 360
        bx1 = cx - box_w // 2
        by1 = cy - box_h // 2
        bx2 = cx + box_w // 2
        by2 = cy + box_h // 2

        draw.rounded_rectangle([bx1 + 3, by1 + 6, bx2 + 3, by2 + 6], radius=28, fill=(0, 0, 0, 100))
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=28, fill=(30, 41, 59, 220), outline=(56, 189, 248), width=3)

        hero = state["hero_img"]
        if hero:
            hw, hh = hero.size
            pil_frame.paste(hero, (cx - hw // 2, cy - hh // 2), hero)

        # Subtitle
        s_font = get_font(34)
        s_txt = "EXAMINE THE 4 SHADOWS BELOW:"
        sbox = draw.textbbox((0, 0), s_txt, font=s_font)
        draw.text(((self.width - (sbox[2]-sbox[0]))//2, by2 + 30), s_txt, fill=(234, 179, 8), font=s_font)

        # 4. 2x2 Grid of 4 Silhouette Options (A, B, C, D)
        opt_labels = ["A", "B", "C", "D"]
        card_w = 420
        card_h = 240
        grid_top = by2 + 80
        
        col_xs = [80, self.width - 80 - card_w]
        row_ys = [grid_top, grid_top + card_h + 30]

        opt_font = get_font(42)

        for i in range(4):
            c_col = i % 2
            c_row = i // 2
            x1 = col_xs[c_col]
            y1 = row_ys[c_row]
            x2 = x1 + card_w
            y2 = y1 + card_h

            is_impostor = (i == state["impostor_idx"])

            # Card body
            draw.rounded_rectangle([x1 + 3, y1 + 5, x2 + 3, y2 + 5], radius=20, fill=(0, 0, 0, 90))
            draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=(245, 248, 255, 240), outline=(148, 163, 184), width=3)

            # Option letter badge (A, B, C, D) in top-left
            draw.rounded_rectangle([x1 + 16, y1 + 16, x1 + 72, y1 + 72], radius=12, fill=(14, 116, 244))
            l_box = draw.textbbox((0, 0), opt_labels[i], font=opt_font)
            draw.text((x1 + 44 - (l_box[2]-l_box[0])//2, y1 + 44 - (l_box[3]-l_box[1])//2 - l_box[1]), opt_labels[i], fill=(255, 255, 255), font=opt_font)

            # Draw silhouette inside card
            if hero:
                sil = make_solid_silhouette(hero)
                # Resize silhouette to fit card
                sil_scaled = sil.copy()
                sil_scaled.thumbnail((card_w - 140, card_h - 40), Image.Resampling.LANCZOS)
                
                # Apply glitch if impostor
                if is_impostor:
                    gt = state["glitch_type"]
                    if gt == "mirror_x":
                        sil_scaled = ImageOps.mirror(sil_scaled)
                    elif gt == "rotate_slight":
                        sil_scaled = sil_scaled.rotate(25, expand=True)
                        sil_scaled.thumbnail((card_w - 140, card_h - 40), Image.Resampling.LANCZOS)
                    elif gt == "vertical_flip":
                        sil_scaled = ImageOps.flip(sil_scaled)

                sw, sh = sil_scaled.size
                sx = x1 + 100 + ((card_w - 120) - sw) // 2
                sy = y1 + (card_h - sh) // 2
                pil_frame.paste(sil_scaled, (sx, sy), sil_scaled)

        # 5. Bottom Viral CTA (Never reveals answer!)
        cta_msg = "WHICH SHADOW IS WRONG? A, B, C OR D? 👇"
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
        name = state.get("hero_name", "Object")

        title = f"Which Shadow Is The Impostor? (A, B, C, or D?) 🕵️"
        
        description = (
            f"🔍 Observation IQ Test!\n\n"
            f"Examine the 4 shadows of the {name} carefully!\n"
            f"Three shadows are completely real, but ONE has a subtle mistake.\n\n"
            f"Which shadow is wrong? A, B, C, or D?\n"
            f"Drop your answer in the comments below! 👇\n\n"
            f"#SpotTheDifference #ShadowPuzzle #VisualIQ #BrainTeaser #MindView #ViralReels"
        )
        
        pinned_comment = (
            f"🕵️ WHICH SHADOW IS FAKE? (A, B, C, OR D)\n"
            f"Look at the angles and details! Comment your choice below! 👇\n"
            f"Only 3% spot the subtle glitch! 🏆"
        )
        
        return title, description, pinned_comment
