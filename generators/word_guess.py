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

# Curated rich library of high-interest vocabulary words for scrambles
SCRAMBLE_WORDS = [
    # 5-Letter Words
    {"word": "BREAD", "hint": "Food / Bakery"},
    {"word": "TIGER", "hint": "Wild Animal"},
    {"word": "EARTH", "hint": "Our Planet"},
    {"word": "PLANT", "hint": "Nature / Flora"},
    {"word": "CROWN", "hint": "Royalty Symbol"},
    {"word": "MAGIC", "hint": "Fantasy / Mystery"},
    {"word": "BRAIN", "hint": "Human Organ"},
    {"word": "RIVER", "hint": "Water Body"},
    {"word": "STORM", "hint": "Weather Phenomenon"},
    {"word": "LIGHT", "hint": "Opposite of Dark"},
    {"word": "PIZZA", "hint": "Italian Dish"},
    {"word": "HONEY", "hint": "Sweet / Golden"},
    {"word": "APPLE", "hint": "Popular Fruit"},
    {"word": "SMILE", "hint": "Happy Facial Expression"},
    {"word": "GHOST", "hint": "Spooky / Spirit"},
    {"word": "CHESS", "hint": "Strategy Board Game"},
    {"word": "MONEY", "hint": "Currency / Wealth"},
    {"word": "SHARK", "hint": "Ocean Predator"},
    {"word": "HEART", "hint": "Symbol of Love"},
    # 6-Letter Words
    {"word": "PLANET", "hint": "Orbits the Sun"},
    {"word": "SILVER", "hint": "Precious Metal"},
    {"word": "CASTLE", "hint": "Medieval Fortress"},
    {"word": "GARDEN", "hint": "Flowers and Trees"},
    {"word": "MONKEY", "hint": "Playful Primate"},
    {"word": "FLOWER", "hint": "Colorful Bloom"},
    {"word": "ORANGE", "hint": "Color and Citrus"},
    {"word": "ROCKET", "hint": "Space Traveler"},
    {"word": "BRIDGE", "hint": "Crosses Over Water"},
    {"word": "GUITAR", "hint": "Musical Instrument"},
    {"word": "CANDLE", "hint": "Wax Light Source"},
    {"word": "FOREST", "hint": "Dense Wilderness"},
    {"word": "PUZZLE", "hint": "Brain Teaser"},
    {"word": "DRAGON", "hint": "Mythical Creature"},
    {"word": "KNIGHT", "hint": "Armored Hero"},
    {"word": "ISLAND", "hint": "Surrounded by Sea"},
    {"word": "MIRROR", "hint": "Reflects Your Face"},
    {"word": "SHADOW", "hint": "Dark Silhouette"}
]

class WordGuessGenerator(BaseGenerator):
    """
    Generates viral Word Scramble anagram puzzles.
    Presents jumbled letters in animated floating cards with category hints.
    14-second duration. NEVER reveals the unscrambled word—forces viewer commenting.
    """
    def __init__(self, page_name: str = "BrainFog Taps", theme: str = "deep_purple"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        item = random.choice(SCRAMBLE_WORDS)
        word = item["word"]
        letters = list(word)
        
        # Scramble letters ensuring it's not identical to original
        scrambled = letters.copy()
        while scrambled == letters and len(letters) > 1:
            random.shuffle(scrambled)

        return {
            "target_word": word,
            "scrambled_letters": scrambled,
            "hint": item["hint"],
            "length": len(word),
            "title": f"UNSCRAMBLE THE {len(word)}-LETTER WORD!"
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
            badge_text="WORD IQ",
            page_name=self.page_name,
            width=self.width
        )
        draw_timer_bar(draw=draw, t=t, duration=duration, width=self.width)

        # 3. Category / Clue Card
        clue_y1 = 440
        clue_h = 240
        clue_w = self.width - 80
        clue_x1 = 40
        clue_x2 = clue_x1 + clue_w

        draw.rounded_rectangle([clue_x1 + 4, clue_y1 + 8, clue_x2 + 4, clue_y1 + clue_h + 8], radius=28, fill=(0, 0, 0, 110))
        draw.rounded_rectangle([clue_x1, clue_y1, clue_x2, clue_y1 + clue_h], radius=28, fill=(24, 18, 43, 245), outline=(168, 85, 247, 200), width=3)

        c_font = get_font(42)
        c_title = "CLUE & HINT"
        tbox = draw.textbbox((0, 0), c_title, font=c_font)
        draw.text((clue_x1 + (clue_w - (tbox[2]-tbox[0]))//2, clue_y1 + 40), c_title, fill=(234, 179, 8), font=c_font)

        hint_font_size = 52
        hint_font = get_font(hint_font_size)
        hint_text = f"\"{state['hint'].upper()}\""
        hbox = draw.textbbox((0, 0), hint_text, font=hint_font)
        while (hbox[2] - hbox[0]) > (clue_w - 60) and hint_font_size > 28:
            hint_font_size -= 2
            hint_font = get_font(hint_font_size)
            hbox = draw.textbbox((0, 0), hint_text, font=hint_font)
        draw.text((clue_x1 + (clue_w - (hbox[2]-hbox[0]))//2, clue_y1 + 120), hint_text, fill=(255, 255, 255), font=hint_font)

        # 4. Scrambled Floating Letter Cards (with subtle organic floating oscillation)
        letters = state["scrambled_letters"]
        n_letters = len(letters)
        card_w = 120 if n_letters <= 5 else 110
        card_h = 140
        gap = 18
        total_w = n_letters * card_w + (n_letters - 1) * gap
        start_x = (self.width - total_w) // 2
        base_y = 820
        l_font = get_font(68)

        for i, char in enumerate(letters):
            # Subtle smooth floating wave animation
            float_dy = math.sin(t * 2.5 + i * 1.0) * 12.0
            
            bx1 = start_x + i * (card_w + gap)
            bx2 = bx1 + card_w
            by1 = int(base_y + float_dy)
            by2 = by1 + card_h

            # Card drop shadow
            draw.rounded_rectangle([bx1 + 3, by1 + 6, bx2 + 3, by2 + 6], radius=20, fill=(0, 0, 0, 100))
            # Card body
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=20, fill=(14, 116, 244), outline=(56, 189, 248), width=3)

            cbox = draw.textbbox((0, 0), char, font=l_font)
            cw = cbox[2] - cbox[0]
            ch = cbox[3] - cbox[1]
            draw.text((bx1 + (card_w - cw)//2, by1 + (card_h - ch)//2 - cbox[1]), char, fill=(255, 255, 255), font=l_font)

        # 5. Empty Target Slots (Stimulates user's brain to mentally place letters)
        slot_y = 1140
        slot_font = get_font(54)
        
        prompt_font = get_font(38)
        p_str = "RE-ARRANGE TO FIND THE SECRET WORD:"
        p_box = draw.textbbox((0, 0), p_str, font=prompt_font)
        draw.text(((self.width - (p_box[2]-p_box[0]))//2, slot_y - 70), p_str, fill=(203, 213, 225), font=prompt_font)

        for i in range(n_letters):
            sx1 = start_x + i * (card_w + gap)
            sx2 = sx1 + card_w
            sy1 = slot_y
            sy2 = sy1 + card_h

            draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=18, fill=(30, 41, 59, 200), outline=(71, 85, 105), width=2)
            # Slot underline placeholder
            draw.line([sx1 + 25, sy2 - 30, sx2 - 25, sy2 - 30], fill=(148, 163, 184), width=4)

        # 6. Viral Tension Tease Card (Guaranteed never to overflow)
        draw_fitted_card(
            draw=draw,
            cx=self.width // 2,
            cy=1430,
            text="CAN YOU UNSCRAMBLE IT IN 14 SECONDS?",
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

        # 7. Bottom Viral Call To Action (Never reveals answer!)
        cta_msg = "TYPE YOUR UNSCRAMBLED WORD IN COMMENTS!"
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
        scrambled_str = " - ".join(state["scrambled_letters"])
        hint = state.get("hint", "")

        title = f"Word Scramble: {scrambled_str} = ? 🧠"
        
        description = (
            f"⚡ Word Scramble IQ Test!\n\n"
            f"Unscramble these letters: {scrambled_str}\n"
            f"Clue: {hint}\n\n"
            f"Only 5% can figure it out before the 14s timer expires!\n"
            f"Comment your unscrambled word below! 👇\n\n"
            f"#WordScramble #Anagram #VocabularyGame #BrainTeaser #MindPuzzle #ViralReels"
        )
        
        pinned_comment = (
            f"💬 WHAT WORD DID YOU GET?\n"
            f"Drop your answer in the comments below! 👇\n"
            f"Did you solve it before the clock ran out? ⏱️"
        )
        
        return title, description, pinned_comment
