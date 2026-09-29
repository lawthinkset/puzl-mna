import math
import random
from typing import Dict, Any, Tuple, List
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

MATCHSTICK_EQUATIONS = [
    {"expr": "6 + 4 = 4", "hint": "Move 1 stick to make it true!"},
    {"expr": "8 + 3 = 14", "hint": "Move 1 stick to make it true!"},
    {"expr": "9 - 3 = 8", "hint": "Move 1 stick to make it true!"},
    {"expr": "5 + 7 = 2", "hint": "Move 1 stick to make it true!"},
    {"expr": "0 + 3 = 9", "hint": "Move 1 stick to make it true!"},
    {"expr": "3 - 7 = 4", "hint": "Move 1 stick to make it true!"},
    {"expr": "4 + 9 = 8", "hint": "Move 1 stick to make it true!"},
    {"expr": "7 - 4 = 8", "hint": "Move 1 stick to make it true!"},
    {"expr": "1 + 8 = 7", "hint": "Move 1 stick to make it true!"},
    {"expr": "6 - 1 = 8", "hint": "Move 1 stick to make it true!"}
]

# Standard 7-segment display mapping for digits 0-9
# Segments: a (top), b (top-right), c (bottom-right), d (bottom), e (bottom-left), f (top-left), g (middle)
DIGIT_SEGMENTS = {
    '0': ['a', 'b', 'c', 'd', 'e', 'f'],
    '1': ['b', 'c'],
    '2': ['a', 'b', 'g', 'e', 'd'],
    '3': ['a', 'b', 'g', 'c', 'd'],
    '4': ['f', 'g', 'b', 'c'],
    '5': ['a', 'f', 'g', 'c', 'd'],
    '6': ['a', 'f', 'g', 'e', 'c', 'd'],
    '7': ['a', 'b', 'c'],
    '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    '9': ['a', 'b', 'c', 'd', 'f', 'g']
}

def draw_matchstick(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, thickness: int = 14):
    """Draws a realistic wooden matchstick with a red sulfur tip."""
    # Wooden shaft (tan/amber)
    draw.line([x1, y1, x2, y2], fill=(234, 197, 130), width=thickness)
    # Red match head at (x1, y1)
    head_r = thickness // 2 + 3
    draw.ellipse([x1 - head_r, y1 - head_r, x1 + head_r, y1 + head_r], fill=(225, 29, 72))

def draw_7segment_matchsticks(draw: ImageDraw.ImageDraw, char: str, ox: int, oy: int, w: int = 120, h: int = 220):
    """Renders digit using wooden matchsticks."""
    if char not in DIGIT_SEGMENTS:
        return
    active = DIGIT_SEGMENTS[char]
    th = 12
    margin = 8

    # Coordinates for segments
    # a: top horizontal
    if 'a' in active:
        draw_matchstick(draw, ox + margin, oy, ox + w - margin, oy, th)
    # b: top right vertical
    if 'b' in active:
        draw_matchstick(draw, ox + w, oy + margin, ox + w, oy + h//2 - margin, th)
    # c: bottom right vertical
    if 'c' in active:
        draw_matchstick(draw, ox + w, oy + h//2 + margin, ox + w, oy + h - margin, th)
    # d: bottom horizontal
    if 'd' in active:
        draw_matchstick(draw, ox + margin, oy + h, ox + w - margin, oy + h, th)
    # e: bottom left vertical
    if 'e' in active:
        draw_matchstick(draw, ox, oy + h//2 + margin, ox, oy + h - margin, th)
    # f: top left vertical
    if 'f' in active:
        draw_matchstick(draw, ox, oy + margin, ox, oy + h//2 - margin, th)
    # g: middle horizontal
    if 'g' in active:
        draw_matchstick(draw, ox + margin, oy + h//2, ox + w - margin, oy + h//2, th)

class MatchstickPuzzleGenerator(BaseGenerator):
    """
    Generates viral matchstick equation puzzles ('Move 1 stick to fix the equation').
    14-second duration. NEVER reveals the solution—viewers must comment their solution!
    """
    def __init__(self, page_name: str = "MindMath Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        item = random.choice(MATCHSTICK_EQUATIONS)
        return {
            "expr": item["expr"],
            "hint": item["hint"],
            "title": "MOVE 1 STICK TO FIX THIS!"
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
            badge_text="LOGIC IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Main Matchstick Table / Felt Mat
        mat_y1 = 440
        mat_h = 440
        mat_w = self.width - 80
        mx1 = 40
        mx2 = mx1 + mat_w

        draw.rounded_rectangle([mx1 + 4, mat_y1 + 8, mx2 + 4, mat_y1 + mat_h + 8], radius=32, fill=(0, 0, 0, 110))
        draw.rounded_rectangle([mx1, mat_y1, mx2, mat_y1 + mat_h], radius=32, fill=(24, 32, 47, 245), outline=(56, 189, 248, 180), width=4)

        # Render matchstick characters: tokens in expression
        tokens = state["expr"].split()  # e.g. ["6", "+", "4", "=", "4"]
        # Render horizontally centered
        total_tokens_w = 0
        token_widths = []
        for tok in tokens:
            tw = 110 if tok.isdigit() else 70
            token_widths.append(tw)
            total_tokens_w += tw
        
        spacing = 35
        total_eq_w = total_tokens_w + (len(tokens) - 1) * spacing
        start_x = mx1 + (mat_w - total_eq_w) // 2
        cy = mat_y1 + (mat_h - 220) // 2

        curr_x = start_x
        op_font = get_font(90)
        for i, tok in enumerate(tokens):
            w = token_widths[i]
            if tok.isdigit():
                # Render matchstick digit
                draw_7segment_matchsticks(draw, tok, curr_x, cy, w=w, h=210)
            else:
                # Operator symbol (+, -, =)
                bbox = draw.textbbox((0, 0), tok, font=op_font)
                ow = bbox[2] - bbox[0]
                oh = bbox[3] - bbox[1]
                draw.text((curr_x + (w - ow)//2, cy + (210 - oh)//2 - bbox[1]), tok, fill=(56, 189, 248), font=op_font)

            curr_x += w + spacing

        # 4. Challenge Rule Banner (Guaranteed no overflow)
        draw_fitted_card(
            draw=draw,
            cx=self.width // 2,
            cy=990,
            text="MOVE EXACTLY 1 MATCHSTICK!",
            max_font_size=38,
            min_font_size=24,
            max_width=980,
            padding_x=36,
            padding_y=22,
            fill_color=(15, 23, 42, 235),
            border_color=(234, 179, 8),
            border_width=3,
            corner_radius=22,
            text_color=(234, 179, 8)
        )

        # 5. Explanatory Provocation Board
        exp_y = 1100
        exp_w = self.width - 80
        exp_h = 340
        ex1 = 40
        ex2 = ex1 + exp_w
        draw.rounded_rectangle([ex1, exp_y, ex2, exp_y + exp_h], radius=28, fill=(15, 23, 42, 240), outline=(51, 65, 85), width=2)
        
        eh_font = get_font(42)
        e1 = "CAN YOU SEE THE SOLUTION?"
        eb = draw.textbbox((0, 0), e1, font=eh_font)
        draw.text((ex1 + (exp_w - (eb[2]-eb[0]))//2, exp_y + 40), e1, fill=(255, 255, 255), font=eh_font)

        sub_font = get_font(36)
        s1 = "1. Pick up 1 matchstick from any digit."
        s2 = "2. Place it anywhere to make it correct."
        s3 = "3. Only 2% can solve it in 14 seconds!"
        
        draw.text((ex1 + 50, exp_y + 120), s1, fill=(203, 213, 225), font=sub_font)
        draw.text((ex1 + 50, exp_y + 180), s2, fill=(203, 213, 225), font=sub_font)
        draw.text((ex1 + 50, exp_y + 245), s3, fill=(239, 68, 68), font=sub_font)

        # 6. Bottom Viral CTA (Never reveals answer!)
        cta_msg = "WHICH STICK DO YOU MOVE? COMMENT YOUR ANSWER!"
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
        expr = state.get("expr", "")

        title = f"Move 1 Matchstick To Fix: {expr} 🥢"
        
        description = (
            f"🔥 Hardest matchstick equation challenge!\n\n"
            f"Current Equation: {expr}\n"
            f"Rule: Move ONLY 1 matchstick to make the equation completely true!\n\n"
            f"Can you visualize the move in 14 seconds?\n"
            f"Comment which stick you move and the new equation below! 👇\n\n"
            f"#MatchstickPuzzle #LogicPuzzle #BrainTeaser #MathRiddle #MindMath #ViralReels"
        )
        
        pinned_comment = (
            f"🥢 MOVE 1 MATCHSTICK TO MAKE IT TRUE!\n"
            f"Which digit do you take the stick from, and where does it go?\n"
            f"Comment your solution below! 👇"
        )
        
        return title, description, pinned_comment
