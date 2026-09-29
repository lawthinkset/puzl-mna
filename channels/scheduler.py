"""
Cross-Page Multi-Slot Posting Matrix & Round-Robin Scheduler.
Coordinates 5 daily posting runs across the 6 Logic Facebook Pages ensuring:
1. Every page posts a DIFFERENT puzzle archetype in any given time slot (zero duplicate posting).
2. Across the day, all pages cycle through all 10 viral puzzle archetypes.
"""
from typing import Dict, List, Tuple
from .page_registry import CHANNELS_REGISTRY, list_all_pages
from generators import ALL_GENERATORS

PUZZLE_MODES = list(ALL_GENERATORS.keys())

def get_slot_puzzle_mapping(slot_number: int = 1) -> Dict[str, str]:
    """
    Computes a non-overlapping permutation mapping for a specific posting slot.
    Slot 1..5: Each Facebook page receives a distinct puzzle mode.
    """
    pages = list_all_pages()
    num_pages = len(pages)
    num_modes = len(PUZZLE_MODES)

    mapping: Dict[str, str] = {}
    
    # Calculate round-robin offset based on slot_number
    base_offset = (slot_number - 1) * 2

    for p_idx, p_info in enumerate(pages):
        page_id = p_info["page_id"]
        mode_idx = (base_offset + p_idx) % num_modes
        mapping[page_id] = PUZZLE_MODES[mode_idx]

    return mapping

def print_daily_schedule(num_slots: int = 5):
    """Prints the daily posting schedule matrix across all pages and slots."""
    pages = list_all_pages()
    print("=" * 80)
    print(f"📅 DAILY MULTI-PAGE POSTING SCHEDULE MATRIX ({num_slots} SLOTS / DAY)")
    print("=" * 80)
    
    for slot in range(1, num_slots + 1):
        mapping = get_slot_puzzle_mapping(slot)
        print(f"\n⏰ POSTING SLOT #{slot}:")
        for pid, mode in mapping.items():
            p_name = CHANNELS_REGISTRY[pid]["name"]
            print(f"  • {p_name:<20} -> Mode: [{mode.upper()}]")
    print("=" * 80)
