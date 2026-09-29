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

# Expanded high-engagement library of rhyme & rebus equations
REBUS_PUZZLES = [
    {
        "asset_name": "crown.png",
        "symbol_label": "👑",
        "rows": [("K", "KING"), ("R", "RING"), ("W", "WING")],
        "rhyme": "ING"
    },
    {
        "asset_name": "soccer_ball.png",
        "symbol_label": "⚽",
        "rows": [("B", "BALL"), ("F", "FALL"), ("W", "WALL")],
        "rhyme": "ALL"
    },
    {
        "asset_name": "tree.png",
        "symbol_label": "🌳",
        "rows": [("T", "TREE"), ("F", "FREE"), ("S", "SEE")],
        "rhyme": "EE"
    },
    {
        "asset_name": "automobile.png",
        "symbol_label": "🚗",
        "rows": [("C", "CAR"), ("B", "BAR"), ("J", "JAR")],
        "rhyme": "AR"
    },
    {
        "asset_name": "cat.png",
        "symbol_label": "🐱",
        "rows": [("C", "CAT"), ("B", "BAT"), ("H", "HAT")],
        "rhyme": "AT"
    },
    {
        "asset_name": "owl.png",
        "symbol_label": "🦉",
        "rows": [("B", "BOWL"), ("H", "HOWL"), ("F", "FOWL")],
        "rhyme": "OWL"
    },
    {
        "asset_name": "duck.png",
        "symbol_label": "🦆",
        "rows": [("D", "DUCK"), ("L", "LUCK"), ("T", "TRUCK")],
        "rhyme": "UCK"
    },
    {
        "asset_name": "bell.png",
        "symbol_label": "🔔",
        "rows": [("B", "BELL"), ("T", "TELL"), ("Y", "YELL")],
        "rhyme": "ELL"
    },
    {
        "asset_name": "fish.png",
        "symbol_label": "🐟",
        "rows": [("F", "FISH"), ("D", "DISH"), ("W", "WISH")],
        "rhyme": "ISH"
    },
    {
        "asset_name": "pig.png",
        "symbol_label": "🐷",
        "rows": [("P", "PIG"), ("B", "BIG"), ("D", "DIG")],
        "rhyme": "IG"
    },
    {
        "asset_name": "fox.png",
        "symbol_label": "🦊",
        "rows": [("F", "FOX"), ("B", "BOX"), ("P", "POX")],
        "rhyme": "OX"
    },
    {
        "asset_name": "bear.png",
        "symbol_label": "🐻",
        "rows": [("B", "BEAR"), ("P", "PEAR"), ("T", "TEAR")],
        "rhyme": "EAR"
    },
    {
        "asset_name": "key.png",
        "symbol_label": "🔑",
        "rows": [("K", "KEY"), ("S", "SEA"), ("T", "TEA")],
        "rhyme": "EY"
    }
]

class RebusPuzzleGenerator(BaseGenerator):
    """
    Generates viral emoji + letter word formula equations (e.g. B + ⚽ = BALL, W + ⚽ = ?).
    14-second duration. NEVER reveals the 3rd word equation—forces viewers to comment.
    """
    def __init__(self, page_name: str = "PlanView Lens", theme: str = "vibrant_navy"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        puzzle = random.choice(REBUS_PUZZLES)
        rows = puzzle["rows"]
        
        asset_path = ASSETS_DIR / puzzle["asset_name"]
        asset_img = None
        if asset_path.exists():
            try:
                asset_img = Image.open(asset_path).convert("RGBA")
            except Exception:
                asset_img = None

        return {
            "puzzle": puzzle,
            "asset_img": asset_img,
            "row1": rows[0],
            "row2": rows[1],
            "row3": rows[2],
            "target_letter": rows[2][0],
            "title": "CAN YOU SOLVE THE 3RD WORD?"
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
            badge_text="REBUS LOGIC",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Main Rebus Board
        board_y1 = 440
        board_h = 980
        board_w = self.width - 80
        board_x1 = 40
        board_x2 = board_x1 + board_w

        draw.rounded_rectangle([board_x1 + 4, board_y1 + 8, board_x2 + 4, board_y1 + board_h + 8], radius=32, fill=(0, 0, 0, 110))
        draw.rounded_rectangle([board_x1, board_y1, board_x2, board_y1 + board_h], radius=32, fill=(15, 23, 42, 240), outline=(56, 189, 248, 180), width=4)

        rows = [state["row1"], state["row2"], state["row3"]]
        row_y_starts = [board_y1 + 50, board_y1 + 355, board_y1 + 660]
        row_h = 245

        asset_img = state["asset_img"]
        font_large = get_font(74)
        font_symbol = get_font(84)

        for idx, (letter, word) in enumerate(rows):
            ry = row_y_starts[idx]
            is_target_row = (idx == 2)
            
            rc_x1 = board_x1 + 25
            rc_x2 = board_x2 - 25
            rc_y1 = ry
            rc_y2 = ry + row_h
            
            if is_target_row:
                # Pulsing golden accent border around the riddle equation
                pulse = math.sin(t * 5.0) * 0.5 + 0.5
                b_color = (234, 179, 8) if pulse > 0.4 else (202, 138, 4)
                draw.rounded_rectangle([rc_x1, rc_y1, rc_x2, rc_y2], radius=22, fill=(28, 25, 43, 230), outline=b_color, width=3)
            else:
                draw.rounded_rectangle([rc_x1, rc_y1, rc_x2, rc_y2], radius=20, fill=(30, 41, 59, 180), outline=(51, 65, 85, 120), width=2)

            x_letter = rc_x1 + 60
            x_plus = rc_x1 + 175
            x_icon = rc_x1 + 270
            x_eq = rc_x1 + 460
            x_word = rc_x1 + 560

            cy = rc_y1 + row_h // 2

            # 1. Letter
            l_box = draw.textbbox((0, 0), letter, font=font_large)
            draw.text((x_letter, cy - (l_box[3] - l_box[1]) // 2 - l_box[1]), letter, fill=(255, 255, 255), font=font_large)

            # 2. Plus sign
            draw.text((x_plus, cy - 45), "+", fill=(56, 189, 248), font=font_symbol)

            # 3. 3D Icon
            icon_size = 145
            if asset_img:
                icon_resized = asset_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                pil_frame.paste(icon_resized, (x_icon, cy - icon_size // 2), icon_resized)
            else:
                sym = state["puzzle"]["symbol_label"]
                draw.text((x_icon, cy - 50), sym, font=font_symbol)

            # 4. Equals sign
            draw.text((x_eq, cy - 45), "=", fill=(255, 255, 255), font=font_symbol)

            # 5. Result Word or Question Marks (NEVER shows answer!)
            if is_target_row:
                q_text = "?  ?  ?"
                q_box = draw.textbbox((0, 0), q_text, font=font_large)
                draw.text((x_word, cy - (q_box[3] - q_box[1]) // 2 - q_box[1]), q_text, fill=(234, 179, 8), font=font_large)
            else:
                w_box = draw.textbbox((0, 0), word, font=font_large)
                draw.text((x_word, cy - (w_box[3] - w_box[1]) // 2 - w_box[1]), word, fill=(255, 255, 255), font=font_large)

        # 4. Engagement Prompt Card (Guaranteed no overflow)
        draw_fitted_card(
            draw=draw,
            cx=self.width // 2,
            cy=1530,
            text="FIGURE OUT THE PATTERN & SOLVE LINE 3!",
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

        # 5. Bottom CTA (Never reveals answer!)
        cta_msg = "SOLVE LINE 3 AND COMMENT YOUR ANSWER!"
        draw_bottom_cta(
            draw=draw,
            t=t,
            duration=duration,
            custom_cta=cta_msg,
            width=self.width,
            height=self.height
        )

        # Convert to OpenCV BGR
        np_frame = np.array(pil_frame)
        return cv2.cvtColor(np_frame[:, :, :3], cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        state = self.puzzle_data
        r1_l, r1_w = state["row1"]
        r2_l, r2_w = state["row2"]
        r3_l = state["target_letter"]

        title = f"Rebus Equation: {r3_l} + {state['puzzle']['symbol_label']} = ? 💡"
        
        description = (
            f"🧠 95% fail to solve this emoji word formula in 14 seconds!\n\n"
            f"{r1_l} + {state['puzzle']['symbol_label']} = {r1_w}\n"
            f"{r2_l} + {state['puzzle']['symbol_label']} = {r2_w}\n"
            f"{r3_l} + {state['puzzle']['symbol_label']} = ?\n\n"
            f"Can you solve line 3 before time is up?\n"
            f"Drop your answer in the comments below! 👇\n\n"
            f"#RebusPuzzle #WordGame #BrainTeaser #EmojiPuzzle #VisualIQ #ViralReels #Riddles"
        )
        
        pinned_comment = (
            f"💡 WHAT IS THE 3RD WORD?\n"
            f"Drop your answer in the comments below! 👇\n"
            f"How fast did your brain connect the pattern? ⏱️"
        )
        
        return title, description, pinned_comment
