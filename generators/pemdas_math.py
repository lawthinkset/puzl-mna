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

# Curated viral debate templates plus infinite procedural generator
MATH_TEMPLATES = [
    {"expr": "40 ÷ 10 × 4 - 4", "opt1": "12", "opt2": "0", "debate": "Is it 12 or 0?"},
    {"expr": "60 ÷ 5(7 - 5)", "opt1": "24", "opt2": "6", "debate": "Is it 24 or 6?"},
    {"expr": "8 ÷ 2(2 + 2)", "opt1": "16", "opt2": "1", "debate": "Is it 16 or 1?"},
    {"expr": "50 - 5 × 0 + 2 + 2", "opt1": "54", "opt2": "4", "debate": "Is it 54 or 4?"},
    {"expr": "20 + 20 × 0 + 20", "opt1": "40", "opt2": "20", "debate": "Is it 40 or 20?"},
    {"expr": "10 - 3 × 3 + 1", "opt1": "2", "opt2": "0", "debate": "Is it 2 or 0?"},
    {"expr": "30 ÷ 5 × 3 + 2", "opt1": "20", "opt2": "4", "debate": "Is it 20 or 4?"},
    {"expr": "100 - 25 × 2 + 10", "opt1": "60", "opt2": "160", "debate": "Is it 60 or 160?"},
    {"expr": "12 + 6 ÷ 3 - 2", "opt1": "12", "opt2": "4", "debate": "Is it 12 or 4?"},
    {"expr": "9 - 3 ÷ 1/3 + 1", "opt1": "9", "opt2": "1", "debate": "Is it 9 or 1?"},
    {"expr": "6 ÷ 2(1 + 2)", "opt1": "9", "opt2": "1", "debate": "Is it 9 or 1?"},
    {"expr": "7 + 7 ÷ 7 + 7 × 7 - 7", "opt1": "50", "opt2": "56", "debate": "Is it 50 or 56?"},
    {"expr": "18 ÷ 3 × 2 + (4 - 2)", "opt1": "14", "opt2": "5", "debate": "Is it 14 or 5?"},
    {"expr": "15 - 3 × 4 + 6 ÷ 2", "opt1": "6", "opt2": "27", "debate": "Is it 6 or 27?"},
    {"expr": "36 ÷ 6(2 + 1)", "opt1": "18", "opt2": "2", "debate": "Is it 18 or 2?"},
    {"expr": "24 ÷ 4 × 2 - 2", "opt1": "10", "opt2": "1", "debate": "Is it 10 or 1?"},
    {"expr": "80 - 8 × 0 + 4 + 4", "opt1": "88", "opt2": "8", "debate": "Is it 88 or 8?"},
    {"expr": "10 + 10 × 10 - 10", "opt1": "100", "opt2": "190", "debate": "Is it 100 or 190?"},
    {"expr": "48 ÷ 2(9 + 3)", "opt1": "288", "opt2": "2", "debate": "Is it 288 or 2?"},
    {"expr": "25 - 5 ÷ 5 + 5", "opt1": "29", "opt2": "9", "debate": "Is it 29 or 9?"},
    {"expr": "16 ÷ 4 × 4 ÷ 4", "opt1": "4", "opt2": "1", "debate": "Is it 4 or 1?"},
    {"expr": "9 + 9 ÷ 9 + 9 × 9 - 9", "opt1": "82", "opt2": "90", "debate": "Is it 82 or 90?"},
    {"expr": "5 + 5 × 5 - 5 ÷ 5", "opt1": "29", "opt2": "5", "debate": "Is it 29 or 5?"},
    {"expr": "100 ÷ 10 × 10 ÷ 10", "opt1": "10", "opt2": "1", "debate": "Is it 10 or 1?"},
    {"expr": "30 - 3 × 3 + 3", "opt1": "24", "opt2": "84", "debate": "Is it 24 or 84?"}
]

def generate_procedural_math_puzzle() -> Dict[str, str]:
    """Generates procedurally synthesized high-debate order-of-operation equations."""
    archetype = random.choice([
        "zero_trap",
        "div_mult_debate",
        "implicit_bracket",
        "mdas_hierarchy",
        "recursive_ident",
        "fraction_div_trap"
    ])
    
    if archetype == "zero_trap":
        a = random.choice([20, 30, 40, 50, 60, 70, 80, 90, 100])
        b = random.randint(2, 9)
        c = random.randint(2, 8)
        d = random.randint(1, 6)
        expr = f"{a} - {b} × 0 + {c} + {d}"
        correct = a + c + d
        trap = c + d
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

    elif archetype == "div_mult_debate":
        b = random.choice([2, 3, 4, 5, 6])
        k = random.randint(3, 9)
        a = b * k
        c = random.choice([2, 3, 4, 5])
        expr = f"{a} ÷ {b} × {c}"
        correct = (a // b) * c
        trap = a // (b * c) if (a % (b * c) == 0) else (b * c)
        if trap == correct:
            trap = correct + random.choice([-2, 2])
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

    elif archetype == "implicit_bracket":
        b = random.choice([2, 3, 4, 5])
        c = random.randint(1, 4)
        d = random.randint(1, 4)
        sum_cd = c + d
        a = b * sum_cd * random.choice([1, 2])
        expr = f"{a} ÷ {b}({c} + {d})"
        correct = (a // b) * sum_cd
        trap = a // (b * sum_cd)
        if trap == correct:
            trap = 1
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

    elif archetype == "mdas_hierarchy":
        b = random.randint(2, 6)
        c = random.randint(2, 6)
        e = random.choice([2, 3, 4])
        d = e * random.randint(1, 4)
        a = random.choice([5, 10, 15, 20, 25])
        expr = f"{a} + {b} × {c} - {d} ÷ {e}"
        correct = a + (b * c) - (d // e)
        trap = ((a + b) * c - d) // e
        if trap == correct:
            trap = correct + 5
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

    elif archetype == "recursive_ident":
        n = random.randint(2, 9)
        expr = f"{n} + {n} ÷ {n} + {n} × {n} - {n}"
        correct = 1 + (n * n)
        trap = ((n + n) // n + n) * n - n
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

    else:
        c = random.choice([2, 3, 4, 5])
        b = random.randint(1, 3)
        b_div_inv = b * c
        a = b_div_inv + random.choice([5, 10, 15])
        d = random.randint(1, 5)
        expr = f"{a} - {b} ÷ (1/{c}) + {d}"
        correct = a - b_div_inv + d
        trap = a - 1 + d
        return {"expr": expr, "opt1": str(correct), "opt2": str(trap), "debate": f"Is it {correct} or {trap}?"}

class PemdasMathGenerator(BaseGenerator):
    """
    Generates viral math equation reels with conflicting options A vs B.
    100+ unique procedural variations. 14-second duration. NEVER reveals the answer—triggers heated comment wars.
    """
    def __init__(self, page_name: str = "MindMath Taps", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        # 50% curated classic debate equations, 50% fresh procedural equations
        if random.random() < 0.5:
            item = random.choice(MATH_TEMPLATES)
        else:
            item = generate_procedural_math_puzzle()
        
        # 50% random order for A vs B
        swap = random.choice([True, False])
        val_a = item["opt2"] if swap else item["opt1"]
        val_b = item["opt1"] if swap else item["opt2"]

        return {
            "expr": item["expr"],
            "opt_a": f"A )   {val_a}",
            "opt_b": f"B )   {val_b}",
            "debate": item["debate"],
            "title": "99% FAIL THIS MATH TEST!"
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
            badge_text="MATH IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Main Equation Board
        eq_y1 = 440
        eq_h = 340
        eq_w = self.width - 80
        eq_x1 = 40
        eq_x2 = eq_x1 + eq_w
        
        draw.rounded_rectangle([eq_x1 + 4, eq_y1 + 8, eq_x2 + 4, eq_y1 + eq_h + 8], radius=32, fill=(0, 0, 0, 110))
        draw.rounded_rectangle([eq_x1, eq_y1, eq_x2, eq_y1 + eq_h], radius=32, fill=(30, 41, 59, 245), outline=(56, 189, 248, 200), width=4)

        eq_str = f"{state['expr']} = ?"
        font_size = 72
        eq_font = get_font(font_size)
        bbox = draw.textbbox((0, 0), eq_str, font=eq_font)
        ew = bbox[2] - bbox[0]
        
        while ew > (eq_w - 60) and font_size > 44:
            font_size -= 4
            eq_font = get_font(font_size)
            bbox = draw.textbbox((0, 0), eq_str, font=eq_font)
            ew = bbox[2] - bbox[0]

        eh = bbox[3] - bbox[1]
        ex = eq_x1 + (eq_w - ew) // 2
        ey = eq_y1 + (eq_h - eh) // 2 - bbox[1]
        draw.text((ex, ey), eq_str, fill=(255, 255, 255), font=eq_font)

        # 4. Large Debate Option Cards: Option A vs Option B
        btn_y1 = 840
        btn_h = 140
        btn_w = (self.width - 120) // 2
        
        bx_a1 = 50
        bx_a2 = bx_a1 + btn_w
        bx_b1 = self.width - 50 - btn_w
        bx_b2 = bx_b1 + btn_w

        opt_font = get_font(52)

        # Option A Card
        draw.rounded_rectangle([bx_a1 + 3, btn_y1 + 5, bx_a2 + 3, btn_y1 + btn_h + 5], radius=24, fill=(0, 0, 0, 90))
        draw.rounded_rectangle([bx_a1, btn_y1, bx_a2, btn_y1 + btn_h], radius=24, fill=(15, 23, 42, 240), outline=(56, 189, 248), width=3)
        box_a = draw.textbbox((0, 0), state["opt_a"], font=opt_font)
        draw.text((bx_a1 + (btn_w - (box_a[2]-box_a[0])) // 2, btn_y1 + (btn_h - (box_a[3]-box_a[1])) // 2 - box_a[1]),
                  state["opt_a"], fill=(255, 255, 255), font=opt_font)

        # Option B Card
        draw.rounded_rectangle([bx_b1 + 3, btn_y1 + 5, bx_b2 + 3, btn_y1 + btn_h + 5], radius=24, fill=(0, 0, 0, 90))
        draw.rounded_rectangle([bx_b1, btn_y1, bx_b2, btn_y1 + btn_h], radius=24, fill=(15, 23, 42, 240), outline=(56, 189, 248), width=3)
        box_b = draw.textbbox((0, 0), state["opt_b"], font=opt_font)
        draw.text((bx_b1 + (btn_w - (box_b[2]-box_b[0])) // 2, btn_y1 + (btn_h - (box_b[3]-box_b[1])) // 2 - box_b[1]),
                  state["opt_b"], fill=(255, 255, 255), font=opt_font)

        # 5. Debate Provocation Board (Stimulates intense commenting)
        prov_y1 = 1040
        prov_h = 360
        prov_w = self.width - 80
        px1 = 40
        px2 = px1 + prov_w
        
        draw.rounded_rectangle([px1 + 3, prov_y1 + 5, px2 + 3, prov_y1 + prov_h + 5], radius=28, fill=(0, 0, 0, 90))
        draw.rounded_rectangle([px1, prov_y1, px2, prov_y1 + prov_h], radius=28, fill=(24, 18, 43, 235), outline=(234, 179, 8), width=3)

        d_font = get_font(46)
        d_txt = "WHICH ONE IS CORRECT?"
        dbox = draw.textbbox((0, 0), d_txt, font=d_font)
        draw.text((px1 + (prov_w - (dbox[2]-dbox[0]))//2, prov_y1 + 45), d_txt, fill=(234, 179, 8), font=d_font)

        sub_font = get_font(38)
        s1 = "50% OF PEOPLE SAY A"
        s2 = "50% OF PEOPLE SAY B"
        s3 = "DO NOT USE A CALCULATOR!"
        
        sb1 = draw.textbbox((0, 0), s1, font=sub_font)
        sb2 = draw.textbbox((0, 0), s2, font=sub_font)
        sb3 = draw.textbbox((0, 0), s3, font=sub_font)

        draw.text((px1 + (prov_w - (sb1[2]-sb1[0]))//2, prov_y1 + 130), s1, fill=(241, 245, 249), font=sub_font)
        draw.text((px1 + (prov_w - (sb2[2]-sb2[0]))//2, prov_y1 + 195), s2, fill=(241, 245, 249), font=sub_font)
        draw.text((px1 + (prov_w - (sb3[2]-sb3[0]))//2, prov_y1 + 270), s3, fill=(239, 68, 68), font=sub_font)

        # 6. Viral Bottom CTA (Never reveals answer!)
        cta_msg = "IS IT A OR B? COMMENT WITH YOUR CALCULATION!"
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
        expr = state.get("expr", "")
        opt_a = state.get("opt_a", "A")
        opt_b = state.get("opt_b", "B")

        title = f"Math Debate: {expr} = ? (A or B?) 🤔"
        
        description = (
            f"🔥 99% fail this order of operations test!\n\n"
            f"What is the correct answer?\n"
            f"{opt_a}\n"
            f"{opt_b}\n\n"
            f"Do not use a calculator!\n"
            f"Drop your answer 'A' or 'B' in the comments below! 👇\n\n"
            f"#MathPuzzle #PEMDAS #BODMAS #MindMath #ViralMath #BrainTeaser #MathDebate #ViralReels"
        )
        
        pinned_comment = (
            f"🤔 A OR B? WHAT IS YOUR FINAL ANSWER?\n"
            f"Drop your answer and explain your calculation below! 👇\n"
            f"Let's see who remembers the order of operations! 🧠"
        )
        
        return title, description, pinned_comment
