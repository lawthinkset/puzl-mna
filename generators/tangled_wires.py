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
    draw_bottom_cta
)
from generators.base_generator import BaseGenerator

def multi_segment_spline(pts: List[Tuple[float, float]], num_samples: int = 100) -> List[Tuple[int, int]]:
    """Generates smooth interpolated spline points through waypoints."""
    samples = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(n - 1, i + 2)]
        
        # Catmull-Rom spline interpolation
        sub_samples = num_samples // (n - 1)
        for s in range(sub_samples):
            t = s / float(sub_samples)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            samples.append((int(x), int(y)))
            
    samples.append((int(pts[-1][0]), int(pts[-1][1])))
    return samples

class TangledWiresGenerator(BaseGenerator):
    """
    Generates high-difficulty tangled wire path maze puzzles.
    6 intricately intertwined, multi-knot cables.
    14-second duration. NEVER reveals the winning wire—forces viewers to trace & comment.
    """
    def __init__(self, page_name: str = "BrainTaps Flow", theme: str = "vibrant_navy"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        num_wires = 6
        wire_labels = ["1", "2", "3", "4", "5", "6"]
        
        wire_colors = [
            {"name": "Electric Cyan", "bgr": (248, 189, 56)},
            {"name": "Neon Yellow", "bgr": (0, 220, 255)},
            {"name": "Crimson Red", "bgr": (68, 68, 239)},
            {"name": "Emerald Green", "bgr": (94, 197, 34)},
            {"name": "Hot Pink", "bgr": (180, 50, 255)},
            {"name": "Bright Orange", "bgr": (30, 140, 255)}
        ]

        top_y = 510
        top_xs = [160, 310, 460, 610, 760, 910]
        
        bot_y = 1440
        bot_xs = [160, 310, 460, 610, 760, 910]

        indices = list(range(num_wires))
        bot_perm = indices.copy()
        while bot_perm == indices:
            random.shuffle(bot_perm)

        target_bot_idx = random.randint(0, num_wires - 1)
        winning_top_idx = bot_perm.index(target_bot_idx)
        winning_number = wire_labels[winning_top_idx]

        # Generate intricate 5-waypoint paths with multiple crossovers
        paths: List[List[Tuple[int, int]]] = []
        for i in range(num_wires):
            start_pt = (float(top_xs[i]), float(top_y))
            end_pt = (float(bot_xs[bot_perm[i]]), float(bot_y))
            
            # 3 intermediate tangled cross-sections
            y1 = top_y + 220
            y2 = top_y + 500
            y3 = top_y + 750
            
            # Randomize x-crossovers to produce complex weaving
            x1 = float(random.randint(140, 940))
            x2 = float(random.randint(140, 940))
            x3 = float(random.randint(140, 940))

            waypoints = [start_pt, (x1, y1), (x2, y2), (x3, y3), end_pt]
            spline_pts = multi_segment_spline(waypoints, num_samples=120)
            paths.append(spline_pts)

        return {
            "num_wires": num_wires,
            "wire_labels": wire_labels,
            "wire_colors": wire_colors,
            "top_xs": top_xs,
            "top_y": top_y,
            "bot_xs": bot_xs,
            "bot_y": bot_y,
            "target_bot_idx": target_bot_idx,
            "winning_top_idx": winning_top_idx,
            "winning_number": winning_number,
            "paths": paths,
            "title": "WHICH CORD CHARGES THE PHONE?"
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
            badge_text="HARD MAZE",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        frame_np = np.array(pil_frame)
        frame_bgr = cv2.cvtColor(frame_np[:, :, :3], cv2.COLOR_RGB2BGR)

        # 3. Draw Tangled Wires (Clean anti-aliased polylines with subtle border shadow)
        paths = state["paths"]
        wire_colors = state["wire_colors"]

        # Draw dark shadow under wires for visual depth
        for i, pts in enumerate(paths):
            pts_np = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame_bgr, [pts_np], isClosed=False, color=(10, 15, 28), thickness=10, lineType=cv2.LINE_AA)

        # Draw colorful cable cores
        for i, pts in enumerate(paths):
            pts_np = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            bgr_c = wire_colors[i]["bgr"]
            cv2.polylines(frame_bgr, [pts_np], isClosed=False, color=bgr_c, thickness=5, lineType=cv2.LINE_AA)

        pil_frame = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_frame)

        # 4. Top Outlets / Plugs (1, 2, 3, 4, 5, 6)
        top_xs = state["top_xs"]
        top_y = state["top_y"]
        wire_labels = state["wire_labels"]
        font_btn = get_font(40)

        for i in range(state["num_wires"]):
            tx = top_xs[i]
            pw, ph = 86, 86
            px1, py1 = tx - pw // 2, top_y - ph
            px2, py2 = tx + pw // 2, top_y
            
            draw.rounded_rectangle([px1 + 2, py1 + 4, px2 + 2, py2 + 4], radius=16, fill=(0, 0, 0, 100))
            draw.rounded_rectangle([px1, py1, px2, py2], radius=16, fill=(30, 41, 59), outline=(56, 189, 248), width=3)
            
            lbl = wire_labels[i]
            lbox = draw.textbbox((0, 0), lbl, font=font_btn)
            draw.text((tx - (lbox[2]-lbox[0])//2, (py1 + py2)//2 - (lbox[3]-lbox[1])//2 - lbox[1]), lbl, fill=(255, 255, 255), font=font_btn)

        # 5. Bottom Phone (Charging target device)
        target_bot_x = state["bot_xs"][state["target_bot_idx"]]
        bot_y = state["bot_y"]
        
        for bi, bx in enumerate(state["bot_xs"]):
            is_phone = (bi == state["target_bot_idx"])
            if is_phone:
                # Realistic smartphone container
                pw, ph = 120, 160
                px1 = bx - pw // 2
                py1 = bot_y
                px2 = bx + pw // 2
                py2 = bot_y + ph
                
                draw.rounded_rectangle([px1 + 3, py1 + 5, px2 + 3, py2 + 5], radius=22, fill=(0, 0, 0, 100))
                draw.rounded_rectangle([px1, py1, px2, py2], radius=22, fill=(15, 23, 42), outline=(56, 189, 248), width=3)
                
                # Screen with pulsing charging indicator
                pulse = math.sin(t * 4.0) * 0.5 + 0.5
                sc_fill = (20, 35, 55) if pulse > 0.4 else (15, 28, 45)
                draw.rounded_rectangle([px1 + 8, py1 + 10, px2 - 8, py2 - 10], radius=14, fill=sc_fill)
                
                status_font = get_font(26)
                msg = "CHARGING"
                sbox = draw.textbbox((0, 0), msg, font=status_font)
                draw.text((bx - (sbox[2]-sbox[0])//2, (py1 + py2)//2 - (sbox[3]-sbox[1])//2 - sbox[1]), msg, fill=(56, 189, 248), font=status_font)
            else:
                sw, sh = 60, 48
                draw.rounded_rectangle([bx - sw//2, bot_y, bx + sw//2, bot_y + sh], radius=10, fill=(30, 41, 59), outline=(71, 85, 105), width=2)

        # 6. Bottom Viral CTA (Never reveals answer!)
        cta_msg = "WHICH WIRE (1 TO 6)? TRACE & COMMENT BELOW!"
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
        title = "Which Cord Charges The Phone? (1 to 6) 🔌"
        
        description = (
            f"⚡ Hardest tangled cable maze!\n"
            f"6 wires are knotted together—only ONE charges the phone!\n\n"
            f"Trace the line carefully with your eyes or finger.\n"
            f"Which number connects to the phone (1, 2, 3, 4, 5, or 6)?\n\n"
            f"Drop your answer in the comments below! 👇\n\n"
            f"#TangledWires #WireMaze #BrainTaps #VisualIQ #BrainTeaser #PuzzleChallenge #ViralReels"
        )
        
        pinned_comment = (
            f"🔌 WHICH WIRE REACHES THE PHONE? (1 TO 6)\n"
            f"Trace it with your finger and comment your answer below! 👇\n"
            f"Did you need to pause the reel? ⏱️"
        )
        
        return title, description, pinned_comment
