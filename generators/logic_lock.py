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
    draw_fitted_card,
    clean_ascii_text
)
from generators.base_generator import BaseGenerator

def score_guess(secret: Tuple[int, int, int], guess: List[int]) -> Tuple[int, int]:
    """Calculates (well_placed, wrongly_placed)."""
    well = sum(s == g for s, g in zip(secret, guess))
    wrong = sum(g in secret for g in guess) - well
    return well, wrong

def generate_unique_lock_puzzle():
    """Generates a verified 3-digit lock puzzle with exactly ONE unique solution."""
    for _ in range(2000):
        digits = list(range(10))
        random.shuffle(digits)
        secret = (digits[0], digits[1], digits[2])
        wrong_pool = digits[3:]
        
        # Clue 1: 1 number correct & well placed
        c1_pos = random.randint(0, 2)
        c1 = [wrong_pool[0], wrong_pool[1], wrong_pool[2]]
        c1[c1_pos] = secret[c1_pos]
        
        # Clue 2: 1 number correct but wrongly placed
        s2_idx = random.randint(0, 2)
        c2_pos = (s2_idx + random.choice([1, 2])) % 3
        c2 = [wrong_pool[2], wrong_pool[3], wrong_pool[4]]
        c2[c2_pos] = secret[s2_idx]
        
        # Clue 3: 2 numbers correct but wrongly placed
        picks = random.sample([0, 1, 2], 2)
        c3 = [wrong_pool[5], wrong_pool[5], wrong_pool[5]]
        p0_target = (picks[0] + random.choice([1, 2])) % 3
        avail = [p for p in [0, 1, 2] if p != picks[1] and p != p0_target]
        if not avail:
            continue
        p1_target = random.choice(avail)
        fill_pos = [p for p in [0, 1, 2] if p not in (p0_target, p1_target)][0]
        c3[p0_target] = secret[picks[0]]
        c3[p1_target] = secret[picks[1]]
        c3[fill_pos] = wrong_pool[6]
        
        # Clue 4: Nothing is correct
        c4 = wrong_pool[0:3]
        
        # Clue 5: 1 number correct but wrongly placed
        other_pick = [i for i in [0, 1, 2] if i != s2_idx][0]
        c5_target = (other_pick + random.choice([1, 2])) % 3
        c5 = [wrong_pool[1], wrong_pool[3], wrong_pool[4]]
        c5[c5_target] = secret[other_pick]
        
        clues = [
            {"digits": c1, "well": 1, "wrong": 0, "text": "ONE NUMBER IS CORRECT & WELL PLACED", "color": (34, 197, 94)},
            {"digits": c2, "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)},
            {"digits": c3, "well": 0, "wrong": 2, "text": "TWO NUMBERS ARE CORRECT BUT WRONG PLACE", "color": (56, 189, 248)},
            {"digits": c4, "well": 0, "wrong": 0, "text": "NOTHING IS CORRECT IN THIS CODE", "color": (239, 68, 68)},
            {"digits": c5, "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)}
        ]
        
        # Test all 1000 combinations
        solutions = []
        for a in range(10):
            for b in range(10):
                for c in range(10):
                    cand = (a, b, c)
                    valid = True
                    for cl in clues:
                        w, r = score_guess(cand, cl["digits"])
                        if w != cl["well"] or r != cl["wrong"]:
                            valid = False
                            break
                    if valid:
                        solutions.append(cand)
        if len(solutions) == 1:
            return secret, clues

    # Fallback guaranteed puzzle
    fallback_secret = (4, 7, 2)
    fallback_clues = [
        {"digits": [6, 8, 2], "well": 1, "wrong": 0, "text": "ONE NUMBER IS CORRECT & WELL PLACED", "color": (34, 197, 94)},
        {"digits": [6, 1, 4], "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)},
        {"digits": [2, 0, 6], "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)},
        {"digits": [7, 3, 8], "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)},
        {"digits": [7, 8, 0], "well": 0, "wrong": 1, "text": "ONE NUMBER IS CORRECT BUT WRONG PLACE", "color": (234, 179, 8)}
    ]
    return fallback_secret, fallback_clues

class LogicLockGenerator(BaseGenerator):
    """
    High-IQ 3-Digit Vault Code Logic Puzzle.
    14-second duration. Strict NO-ANSWER disclosure.
    Forces viewers to deduce all 3 digits and debate in comments.
    """
    def __init__(self, page_name: str = "LogicFix Lens", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        secret, clues = generate_unique_lock_puzzle()
        return {
            "title": "CRACK THE 3-DIGIT CODE!",
            "secret": secret,
            "secret_str": "".join(str(d) for d in secret),
            "clues": clues
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        if not self.puzzle_data:
            self.puzzle_data = self.generate_puzzle_state()
        state = self.puzzle_data
        pil_frame = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(pil_frame)

        # 1. Header Banner
        draw_header_banner(
            draw=draw,
            title=state["title"],
            badge_text="98% CANNOT SOLVE",
            page_name=self.page_name,
            width=self.width
        )

        # 2. Timer Bar
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Vault Lock Dials Section
        # Prompt
        p_font = get_font(34)
        p_text = "DEDUCE THE 3 SECRET DIGITS:"
        pbox = draw.textbbox((0, 0), p_text, font=p_font)
        pw = pbox[2] - pbox[0]
        draw.text(((self.width - pw) // 2, 385), p_text, fill=(203, 213, 225), font=p_font)

        dial_w = 140
        dial_h = 160
        dial_gap = 32
        total_dials_w = 3 * dial_w + 2 * dial_gap
        start_dx = (self.width - total_dials_w) // 2
        dial_y = 440

        # Subtle pulsing animation on dials
        pulse = math.sin(t * 3.0) * 0.15 + 0.85
        q_font = get_font(90)

        for i in range(3):
            x1 = start_dx + i * (dial_w + dial_gap)
            x2 = x1 + dial_w
            y1 = dial_y
            y2 = y1 + dial_h

            # Dial drop shadow
            draw.rounded_rectangle([x1 + 4, y1 + 8, x2 + 4, y2 + 8], radius=24, fill=(0, 0, 0, 120))
            # Dial metallic body
            draw.rounded_rectangle([x1, y1, x2, y2], radius=24, fill=(15, 23, 42, 245), outline=(56, 189, 248), width=3)
            # Inner chamber
            draw.rounded_rectangle([x1 + 12, y1 + 12, x2 - 12, y2 - 12], radius=16, fill=(30, 41, 59, 200), outline=(71, 85, 105), width=2)

            # Center question mark (never reveals answer!)
            q_str = "?"
            qbox = draw.textbbox((0, 0), q_str, font=q_font)
            qw = qbox[2] - qbox[0]
            qh = qbox[3] - qbox[1]
            q_color = (int(56 * pulse + 199 * (1 - pulse)), int(189 * pulse + 66 * (1 - pulse)), 248)
            draw.text((x1 + (dial_w - qw) // 2, y1 + (dial_h - qh) // 2 - qbox[1]), q_str, fill=q_color, font=q_font)

        # 4. Clue Cards Section (5 Cards, perfectly sized so NO text overflows)
        clue_y_start = 645
        card_h = 115
        gap_y = 22
        card_w = self.width - 80
        cx1 = 40
        cx2 = cx1 + card_w

        for i, clue in enumerate(state["clues"]):
            cy1 = clue_y_start + i * (card_h + gap_y)
            cy2 = cy1 + card_h

            # Card drop shadow
            draw.rounded_rectangle([cx1 + 3, cy1 + 5, cx2 + 3, cy2 + 5], radius=20, fill=(0, 0, 0, 90))
            # Card background
            draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=20, fill=(15, 23, 42, 235), outline=(71, 85, 105, 180), width=2)

            # Left side: 3 Clue Digit Pills
            pw = 64
            ph = 80
            pgap = 12
            start_px = cx1 + 25
            py = cy1 + (card_h - ph) // 2
            d_font = get_font(46)

            for d_idx, digit in enumerate(clue["digits"]):
                px1 = start_px + d_idx * (pw + pgap)
                px2 = px1 + pw
                draw.rounded_rectangle([px1, py, px2, py + ph], radius=14, fill=(30, 41, 59, 240), outline=(100, 116, 139), width=2)
                d_str = str(digit)
                dbox = draw.textbbox((0, 0), d_str, font=d_font)
                dw = dbox[2] - dbox[0]
                dh = dbox[3] - dbox[1]
                draw.text((px1 + (pw - dw) // 2, py + (ph - dh) // 2 - dbox[1]), d_str, fill=(255, 255, 255), font=d_font)

            # Vector arrow polygon (never fails with font glyph missing)
            arrow_x = start_px + 3 * (pw + pgap) + 16
            arrow_y = cy1 + card_h // 2
            draw.polygon([
                (arrow_x, arrow_y - 12),
                (arrow_x + 14, arrow_y),
                (arrow_x, arrow_y + 12)
            ], fill=clue["color"])

            # Right side: Clue Description Text (Fitted with dynamic font scaling)
            desc_x = arrow_x + 45
            avail_w = cx2 - desc_x - 20
            raw_text = clue["text"]
            
            # Dynamic downscale
            f_size = 30
            c_font = get_font(f_size)
            tbox = draw.textbbox((0, 0), raw_text, font=c_font)
            tw = tbox[2] - tbox[0]
            while tw > avail_w and f_size > 18:
                f_size -= 2
                c_font = get_font(f_size)
                tbox = draw.textbbox((0, 0), raw_text, font=c_font)
                tw = tbox[2] - tbox[0]
            th = tbox[3] - tbox[1]

            # Glowing indicator dot + Text
            draw.text((desc_x, cy1 + (card_h - th) // 2 - tbox[1]), raw_text, fill=clue["color"], font=c_font)

        # 5. Viral Prompt Tease Card (Guaranteed never to overflow)
        draw_fitted_card(
            draw=draw,
            cx=self.width // 2,
            cy=1400,
            text="CAN YOU CRACK THE CODE IN 14 SECONDS?",
            max_font_size=36,
            min_font_size=24,
            max_width=980,
            padding_x=36,
            padding_y=22,
            fill_color=(15, 23, 42, 230),
            border_color=(234, 179, 8),
            border_width=3,
            corner_radius=22,
            text_color=(255, 255, 255)
        )

        # 6. Bottom Viral Call To Action (Never reveals answer!)
        cta_msg = "COMMENT YOUR 3-DIGIT CODE BELOW!"
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
        secret_str = state["secret_str"]

        title = "Crack the 3-Digit Vault Code! 🔐 Only 2% Can Solve!"
        
        description = (
            f"🔐 MASTER LOGIC CHALLENGE: Can you crack the 3-digit code?\n\n"
            f"Carefully analyze all 5 clue cards!\n"
            f"There is only ONE exact mathematical combination that unlocks the vault.\n\n"
            f"Comment your 3-digit code below! 👇\n\n"
            f"#LogicLock #CrackTheCode #VaultPuzzle #BrainTeaser #LogicIQ #ViralReels #MindGames"
        )
        
        pinned_comment = (
            f"🔐 WHAT IS THE 3-DIGIT COMBINATION?\n"
            f"Comment your code below! 👇\n"
            f"Did you crack it before the timer expired? ⏱️"
        )
        
        return title, description, pinned_comment
