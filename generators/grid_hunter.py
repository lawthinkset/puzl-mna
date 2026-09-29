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
    draw_bottom_cta
)
from generators.base_generator import BaseGenerator

# Vast infinite pool of confusing pairs (base, intruder)
CONFUSING_PAIRS = [
    # Highly deceptive numbers
    ("88", "80"), ("43", "34"), ("69", "96"), ("52", "25"),
    ("71", "17"), ("38", "83"), ("99", "66"), ("06", "09"),
    ("25", "52"), ("10", "01"), ("89", "98"), ("33", "88"),
    ("77", "11"), ("55", "22"), ("68", "86"), ("48", "84"),
    ("18", "81"), ("78", "87"), ("91", "19"), ("32", "23"),
    ("58", "85"), ("36", "63"), ("79", "97"), ("27", "72"),
    ("49", "94"), ("15", "51"), ("35", "53"), ("28", "82"),
    ("46", "64"), ("13", "31"), ("93", "39"), ("62", "26"),
    ("57", "75"), ("74", "47"), ("83", "38"), ("08", "80"),
    # Highly deceptive letters
    ("E", "F"), ("O", "Q"), ("B", "8"), ("C", "G"),
    ("P", "R"), ("M", "N"), ("V", "U"), ("D", "O"),
    ("K", "X"), ("S", "5"), ("Z", "2"), ("I", "1"),
    ("W", "M"), ("H", "N"), ("T", "7"), ("Y", "V"),
    ("A", "4"), ("J", "L"), ("Q", "O"), ("F", "E"),
    # Highly deceptive 2/3-letter alphanumeric pairs
    ("RN", "M"), ("CL", "D"), ("VV", "W"), ("NN", "M"),
    ("DO", "DD"), ("BB", "88"), ("CO", "CC"), ("EF", "EE"),
    ("888", "808"), ("707", "777"), ("909", "999"), ("101", "111")
]

class GridHunterGenerator(BaseGenerator):
    """
    Generates high-difficulty 'Find the Odd One Out' matrix puzzles with column/row coordinates.
    14-second duration. NEVER reveals the answer—forces viewers to comment coordinates.
    """
    def __init__(self, page_name: str = "MindQuiz Focus", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        base_item, target_item = random.choice(CONFUSING_PAIRS)
        
        # High difficulty 9 rows × 7 columns = 63 cells
        cols = 7
        rows = 9
        col_labels = ["A", "B", "C", "D", "E", "F", "G"]
        row_labels = [str(r + 1) for r in range(rows)]
        
        target_col = random.randint(0, cols - 1)
        target_row = random.randint(0, rows - 1)
        target_coord = f"{col_labels[target_col]}{row_labels[target_row]}"

        return {
            "base_item": base_item,
            "target_item": target_item,
            "cols": cols,
            "rows": rows,
            "col_labels": col_labels,
            "row_labels": row_labels,
            "target_col": target_col,
            "target_row": target_row,
            "target_coord": target_coord,
            "title": f"FIND '{target_item}' AMONG '{base_item}'"
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        if not self.puzzle_data:
            self.puzzle_data = self.generate_puzzle_state()
        state = self.puzzle_data
        
        # 1. Base gradient background
        pil_frame = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(pil_frame)

        # 2. Header banner and 14s timer bar
        draw_header_banner(
            draw=draw,
            title=state["title"],
            badge_text="HARD IQ TEST",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Clean Grid Layout (Strictly calibrated to avoid any overlap)
        grid_top = 460
        grid_bottom = 1620
        grid_left = 135
        grid_right = self.width - 65
        grid_w = grid_right - grid_left
        grid_h = grid_bottom - grid_top
        
        cols = state["cols"]
        rows = state["rows"]
        cell_w = grid_w / cols
        cell_h = grid_h / rows

        axis_font = get_font(32)
        # Font size adapted for single character vs 2 digits
        is_long = len(state["base_item"]) > 1
        item_font = get_font(38 if is_long else 44)

        # Column Axis Labels (A, B, C, D, E, F, G)
        col_y = grid_top - 46
        for c, lbl in enumerate(state["col_labels"]):
            cx = grid_left + c * cell_w + cell_w / 2
            bbox = draw.textbbox((0, 0), lbl, font=axis_font)
            bw = bbox[2] - bbox[0]
            draw.text((cx - bw / 2, col_y - bbox[1]), lbl, fill=(148, 163, 184), font=axis_font)

        # Row Axis Labels (1, 2, 3, 4, 5, 6, 7, 8, 9)
        row_x = grid_left - 50
        for r, lbl in enumerate(state["row_labels"]):
            cy = grid_top + r * cell_h + cell_h / 2
            bbox = draw.textbbox((0, 0), lbl, font=axis_font)
            bw = bbox[2] - bbox[0]
            draw.text((row_x - bw / 2, cy - (bbox[3] - bbox[1]) / 2 - bbox[1]), lbl, fill=(148, 163, 184), font=axis_font)

        # Draw Grid Matrix Cells & Text (NEVER reveals target cell styling!)
        for r in range(rows):
            for c in range(cols):
                cx = grid_left + c * cell_w + cell_w / 2
                cy = grid_top + r * cell_h + cell_h / 2
                is_target = (r == state["target_row"] and c == state["target_col"])
                
                # Cell card background (identical for all cells to maintain genuine difficulty)
                pad = 4
                bx1 = grid_left + c * cell_w + pad
                by1 = grid_top + r * cell_h + pad
                bx2 = grid_left + (c + 1) * cell_w - pad
                by2 = grid_top + (r + 1) * cell_h - pad
                
                draw.rounded_rectangle([bx1, by1, bx2, by2], radius=10, fill=(30, 41, 59, 185), outline=(51, 65, 85, 120), width=1)
                text_fill = (241, 245, 249)

                item_str = state["target_item"] if is_target else state["base_item"]
                ibox = draw.textbbox((0, 0), item_str, font=item_font)
                iw = ibox[2] - ibox[0]
                ih = ibox[3] - ibox[1]
                draw.text((cx - iw / 2, cy - ih / 2 - ibox[1]), item_str, fill=text_fill, font=item_font)

        # 4. Viral Bottom Call To Action (Never reveals answer!)
        cta_msg = "COMMENT COORDINATES (E.G. D5) BEFORE TIME IS UP!"
        draw_bottom_cta(
            draw=draw,
            t=t,
            duration=duration,
            custom_cta=cta_msg,
            width=self.width,
            height=self.height
        )

        # Convert PIL RGBA to OpenCV BGR
        np_frame = np.array(pil_frame)
        return cv2.cvtColor(np_frame[:, :, :3], cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        state = self.puzzle_data
        target = state.get("target_item", "the odd one")
        base = state.get("base_item", "the rest")

        title = f"Hardest Eye Test: Find '{target}' Among '{base}'! 🔍"
        
        description = (
            f"👀 Only 1% of people can spot the hidden '{target}' among '{base}' in 14 seconds!\n\n"
            f"Row (1-9) or Column (A-G)?\n"
            f"Comment your exact coordinate below before time runs out! 👇\n\n"
            f"#GridPuzzle #OddOneOut #MindQuiz #BrainTeaser #VisualIQ #ViralReels #PuzzleChallenge"
        )
        
        pinned_comment = (
            f"📌 COMMENT YOUR COORDINATE (ROW + COL)!\n"
            f"Did you find it? Be honest: How many seconds did it take? ⏱️👇\n"
            f"Tag someone with sharp eyes to test them! 👁️"
        )
        
        return title, description, pinned_comment
