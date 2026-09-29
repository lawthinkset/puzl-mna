import math
import random
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

from core.ui_renderer import (
    get_font,
    draw_gradient_background,
    draw_header_banner,
    draw_timer_bar,
    draw_bottom_cta,
    draw_multiple_choice_options
)
from generators.base_generator import BaseGenerator

class OpticalSwirlGenerator(BaseGenerator):
    """
    Hypnotic optical illusion puzzle generator.
    Embeds a 3-digit secret number inside rotating procedural spirals.
    14-second duration. NEVER reveals the number—maximizes watch time and replays.
    """
    def __init__(self, page_name: str = "MindView Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        val = random.randint(100, 999)
        secret_str = str(val)
        
        similars = {
            '0': ['8', '6'], '1': ['7', '4'], '2': ['7', '3'], '3': ['8', '5'],
            '4': ['1', '9'], '5': ['6', '3'], '6': ['5', '8'], '7': ['1', '2'],
            '8': ['3', '0'], '9': ['8', '6']
        }
        
        decoys = set()
        for idx in range(3):
            d_list = list(secret_str)
            orig_char = d_list[idx]
            alt = random.choice(similars.get(orig_char, ['0', '8']))
            d_list[idx] = alt
            cand = "".join(d_list)
            if cand != secret_str:
                decoys.add(cand)

        while len(decoys) < 3:
            cand = str(random.randint(100, 999))
            if cand != secret_str:
                decoys.add(cand)

        options = list(decoys)[:3] + [secret_str]
        random.shuffle(options)

        spiral_turns = random.choice([20, 24, 28])
        spiral_dir = random.choice([1, -1])

        return {
            "secret_str": secret_str,
            "options": options,
            "spiral_turns": spiral_turns,
            "spiral_dir": spiral_dir,
            "title": "WHAT NUMBER DO YOU SEE?"
        }

    def _render_swirl_canvas(self, t: float, size: int = 780) -> np.ndarray:
        """Procedurally computes mathematical rotating spiral with low-contrast number mask."""
        state = self.puzzle_data
        turns = state["spiral_turns"]
        s_dir = state["spiral_dir"]
        secret_str = state["secret_str"]

        half = size // 2
        y, x = np.ogrid[-half:half, -half:half]
        r = np.hypot(x, y)
        theta = np.arctan2(y, x)

        rot_speed = 0.9 * s_dir
        phase = turns * (r / half) + theta - (t * rot_speed * 2 * np.pi)
        spiral_raw = np.sin(phase)
        
        stripes = np.where(spiral_raw > 0, 240.0, 20.0)

        # Create number mask with PIL
        mask_img = Image.new("L", (size, size), 0)
        m_draw = ImageDraw.Draw(mask_img)
        font_size = 270
        num_font = get_font(font_size)
        bbox = m_draw.textbbox((0, 0), secret_str, font=num_font)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        nx = (size - nw) // 2
        ny = (size - nh) // 2 - bbox[1]
        m_draw.text((nx, ny), secret_str, fill=255, font=num_font)
        mask_np = np.array(mask_img, dtype=np.float32) / 255.0

        circle_mask = np.clip(1.0 - (r / (half * 0.96)) ** 4, 0.0, 1.0)

        # Subtle low-contrast embedding: slightly modulate stripe luminance inside number
        # Optical illusion: only readable when pausing or squinting closely!
        mod = stripes.copy()
        mod = np.where(mask_np > 0.5, 255.0 - mod * 0.60, mod)
        swirl_gray = mod * circle_mask
        bgr = np.stack([swirl_gray, swirl_gray, swirl_gray], axis=-1).astype(np.uint8)

        return bgr

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        state = self.puzzle_data

        # 1. Base gradient
        pil_frame = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(pil_frame)

        # 2. Header & 14s Timer
        draw_header_banner(
            draw=draw,
            title=state["title"],
            badge_text="OPTICAL IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Multiple Choice Buttons at bottom (Interactive throughout full 14s)
        draw_multiple_choice_options(
            draw=draw,
            options=state["options"],
            width=self.width,
            center_y=1490
        )

        # 4. Bottom Viral CTA
        cta_msg = "CHOOSE A, B, C OR D IN COMMENTS!"
        draw_bottom_cta(
            draw=draw,
            t=t,
            duration=duration,
            custom_cta=cta_msg,
            width=self.width,
            height=self.height
        )

        frame_np = np.array(pil_frame)
        frame_bgr = cv2.cvtColor(frame_np[:, :, :3], cv2.COLOR_RGB2BGR)

        # 5. Composite Rotating Swirl in Center
        swirl_size = 780
        swirl_bgr = self._render_swirl_canvas(t, size=swirl_size)

        cx = self.width // 2
        cy = 880
        x1 = cx - swirl_size // 2
        y1 = cy - swirl_size // 2
        x2 = x1 + swirl_size
        y2 = y1 + swirl_size

        # Circular outer decorative metallic rings
        cv2.circle(frame_bgr, (cx, cy), swirl_size // 2 + 6, (56, 189, 248), 6, lineType=cv2.LINE_AA)
        cv2.circle(frame_bgr, (cx, cy), swirl_size // 2 + 12, (30, 41, 59), 4, lineType=cv2.LINE_AA)

        half = swirl_size // 2
        sy, sx = np.ogrid[-half:half, -half:half]
        circ_alpha = np.clip((half - np.hypot(sx, sy)) / 2.0, 0.0, 1.0)[:, :, None]
        
        roi = frame_bgr[y1:y2, x1:x2]
        frame_bgr[y1:y2, x1:x2] = (roi * (1.0 - circ_alpha) + swirl_bgr * circ_alpha).astype(np.uint8)

        return frame_bgr

    def get_metadata(self) -> Tuple[str, str, str]:
        state = self.puzzle_data
        options_str = " | ".join(state.get("options", []))

        title = f"Optical Illusion: What Number Do You See? 👁️"
        
        description = (
            f"🌀 99% of people fail to spot the number in this rotating vortex!\n\n"
            f"Options: {options_str}\n\n"
            f"Squint or pause if you need extra focus!\n"
            f"Drop your guess (A, B, C, or D) in the comments below! 👇\n\n"
            f"#OpticalIllusion #MindView #MindGames #MagicEye #BrainTeaser #ViralReels #Hypnotic"
        )
        
        pinned_comment = (
            f"👁️ WHAT NUMBER DID YOU SPOT FIRST?\n"
            f"Drop your answer below! 👇\n"
            f"Did you need to pause or squint your eyes? Be honest! 🏆"
        )
        
        return title, description, pinned_comment
