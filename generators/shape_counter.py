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
    draw_multiple_choice_options
)
from generators.base_generator import BaseGenerator

class ShapeCounterGenerator(BaseGenerator):
    """
    Generates viral visual counting challenges ('How many 8s do you see?', 'Count the triangles').
    14-second duration. NEVER reveals the true count—drives fierce debates in comments.
    """
    def __init__(self, page_name: str = "Buildings Bountsy", theme: str = "clean_light"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        # Target digit to count
        target_char = random.choice(["8", "3", "7", "9", "B", "O"])
        decoy_char = random.choice(["0", "6", "5", "1", "D", "C"])
        
        # Exact number of targets to scatter
        target_count = random.randint(14, 24)
        decoy_count = random.randint(8, 14)
        
        # Generate 4 multiple choice count options
        correct = target_count
        step = 2
        options = [str(correct - step), str(correct), str(correct + step), str(correct + 2*step)]
        random.shuffle(options)

        # Generate positions inside circular diagram
        cx = 540
        cy = 920
        radius = 350
        
        items: List[Dict[str, Any]] = []
        for _ in range(target_count):
            r = radius * math.sqrt(random.uniform(0.05, 0.95))
            theta = random.uniform(0, 2 * math.pi)
            ix = int(cx + r * math.cos(theta))
            iy = int(cy + r * math.sin(theta))
            f_size = random.choice([38, 46, 54, 62])
            alpha = random.choice([160, 220, 255])
            items.append({"char": target_char, "x": ix, "y": iy, "size": f_size, "alpha": alpha})

        for _ in range(decoy_count):
            r = radius * math.sqrt(random.uniform(0.05, 0.95))
            theta = random.uniform(0, 2 * math.pi)
            ix = int(cx + r * math.cos(theta))
            iy = int(cy + r * math.sin(theta))
            f_size = random.choice([38, 46, 54])
            alpha = random.choice([120, 180, 220])
            items.append({"char": decoy_char, "x": ix, "y": iy, "size": f_size, "alpha": alpha})

        random.shuffle(items)

        return {
            "target_char": target_char,
            "target_count": target_count,
            "options": options,
            "items": items,
            "title": f"HOW MANY '{target_char}' DO YOU SEE?"
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
            badge_text="COUNTING IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        cx = 540
        cy = 920
        radius = 360

        # 3. Geometric Reticle / Concentric Lens Container
        # Overlapping concentric rings
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     fill=(245, 248, 255, 220), outline=(56, 189, 248), width=5)
        draw.ellipse([cx - (radius - 80), cy - (radius - 80), cx + (radius - 80), cy + (radius - 80)],
                     outline=(148, 163, 184, 140), width=2)
        draw.ellipse([cx - (radius - 180), cy - (radius - 180), cx + (radius - 180), cy + (radius - 180)],
                     outline=(148, 163, 184, 100), width=2)

        # Crosshairs
        draw.line([cx - radius - 20, cy, cx - radius + 30, cy], fill=(56, 189, 248), width=3)
        draw.line([cx + radius - 30, cy, cx + radius + 20, cy], fill=(56, 189, 248), width=3)
        draw.line([cx, cy - radius - 20, cx, cy - radius + 30], fill=(56, 189, 248), width=3)
        draw.line([cx, cy + radius - 30, cx, cy + radius + 20], fill=(56, 189, 248), width=3)

        # Draw scattered items inside circular lens
        for it in state["items"]:
            f = get_font(it["size"])
            ch = it["char"]
            bbox = draw.textbbox((0, 0), ch, font=f)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            c_val = 15 if self.theme != "clean_light" else 20
            color = (c_val, c_val, c_val, it["alpha"])
            draw.text((it["x"] - w//2, it["y"] - h//2 - bbox[1]), ch, fill=color, font=f)

        # 4. Multiple Choice Buttons at bottom
        draw_multiple_choice_options(
            draw=draw,
            options=state["options"],
            width=self.width,
            center_y=1480
        )

        # 5. Bottom Viral CTA (Never reveals answer!)
        cta_msg = "COUNT CAREFULLY AND COMMENT YOUR NUMBER!"
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
        char = state.get("target_char", "8")
        options_str = " | ".join(state.get("options", []))

        title = f"Counting Test: How Many '{char}' Do You See? 🔢"
        
        description = (
            f"👀 Observation IQ Test!\n\n"
            f"How many '{char}' are scattered inside the circle?\n"
            f"Choices: {options_str}\n\n"
            f"95% miss at least two of them!\n"
            f"Pause the reel if you need to count carefully.\n"
            f"Drop your count in the comments below! 👇\n\n"
            f"#CountingTest #ObservationIQ #BrainTeaser #VisualPuzzle #MindGames #ViralReels"
        )
        
        pinned_comment = (
            f"🔢 HOW MANY '{char}' DID YOU COUNT?\n"
            f"Look closely at the faint ones! Drop your answer below! 👇\n"
            f"What was your final count? ⏱️"
        )
        
        return title, description, pinned_comment
