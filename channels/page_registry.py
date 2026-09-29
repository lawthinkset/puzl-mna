"""
Page Profiles and Thematic Channel Registry for the Viral Puzzle Network.
Assigns each Facebook Page its designated puzzle archetype and visual branding,
allowing 7-12+ channels to run completely unique, infinite puzzle reels.
"""
from typing import Dict, Any, List

CHANNELS_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Page 1: Precision Reflex & Shadow Silhouette Match
    "1319646877895110": {
        "slug": "brainfocus",
        "name": "BrainFocus Taps",
        "tagline": "Precision Reflex & Microsecond Timing",
        "primary_mode": "pause_silhouette",
        "supported_modes": ["pause_silhouette", "grid_hunter"],
        "theme": "dark_slate",
        "hashtags": ["#BrainFocus", "#ReflexTest", "#PauseChallenge", "#MindGames", "#ViralReels"]
    },

    # Page 2: Viral PEMDAS & Order of Operations Math Trap
    "1309712825557751": {
        "slug": "mindmath",
        "name": "MindMath Taps",
        "tagline": "Mental Math & Calculation Order Debates",
        "primary_mode": "pemdas_math",
        "supported_modes": ["pemdas_math", "grid_hunter"],
        "theme": "dark_slate",
        "hashtags": ["#MindMath", "#MathIQ", "#PEMDAS", "#MathDebate", "#BrainTraining", "#ViralReels"]
    },

    # Page 3: Odd-One-Out Grid Matrix & Coordinate Search
    "1350182274839663": {
        "slug": "mindquiz",
        "name": "MindQuiz Focus",
        "tagline": "Observation IQ & Odd-One-Out Hunter",
        "primary_mode": "grid_hunter",
        "supported_modes": ["grid_hunter", "optical_swirl"],
        "theme": "dark_slate",
        "hashtags": ["#MindQuiz", "#OddOneOut", "#SpotTheDifference", "#ObservationTest", "#ViralReels"]
    },

    # Page 4: Hypnotic Optical Swirl & Hidden Number Decoder
    "1334005973127654": {
        "slug": "mindview",
        "name": "MindView Taps",
        "tagline": "Hypnotic Optical Illusions & Hidden Code Decoders",
        "primary_mode": "optical_swirl",
        "supported_modes": ["optical_swirl", "tangled_wires"],
        "theme": "dark_slate",
        "hashtags": ["#MindView", "#OpticalIllusion", "#MagicEye", "#VisualPuzzle", "#ViralReels"]
    },

    # Page 5: Word Completion & Vocabulary Speed Drills
    "1316150674917146": {
        "slug": "brainfog",
        "name": "BrainFog Taps",
        "tagline": "Morning Brain Wake-Up & Vocabulary Drills",
        "primary_mode": "word_guess",
        "supported_modes": ["word_guess", "rebus_puzzle"],
        "theme": "deep_purple",
        "hashtags": ["#BrainFog", "#WordPuzzle", "#VocabularyChallenge", "#BrainWakeup", "#ViralReels"]
    },

    # Page 6: Tangled Cord & Wire Path Solver
    "1227319627140685": {
        "slug": "braintaps_flow",
        "name": "BrainTaps Flow",
        "tagline": "Satisfying Logic Wire Maze & Flow Paths",
        "primary_mode": "tangled_wires",
        "supported_modes": ["tangled_wires", "pause_silhouette"],
        "theme": "vibrant_navy",
        "hashtags": ["#BrainTapsFlow", "#TangledWires", "#WireMaze", "#SatisfyingLogic", "#ViralReels"]
    },

    # Page 7: Rebus & Emoji Word Equations
    "1384807541372867": {
        "slug": "planview_lens",
        "name": "PlanView Lens",
        "tagline": "Visual Rebus Equations & Symbolic Deductions",
        "primary_mode": "rebus_puzzle",
        "supported_modes": ["rebus_puzzle", "grid_hunter"],
        "theme": "vibrant_navy",
        "hashtags": ["#PlanView", "#RebusPuzzle", "#EmojiPuzzle", "#WordFormula", "#ViralReels"]
    },

    # Page 8: Infinite Shape / Pattern Counter
    "1340879302432137": {
        "slug": "buildings_bountsy",
        "name": "Buildings Bountsy",
        "tagline": "Spatial Geometry & Shape Counting Tests",
        "primary_mode": "grid_hunter",
        "supported_modes": ["grid_hunter", "optical_swirl"],
        "theme": "clean_light",
        "hashtags": ["#BuildingsBountsy", "#GeometryPuzzle", "#CountTheShapes", "#BrainTeaser", "#ViralReels"]
    }
}

def get_channel_config(page_id: str) -> Dict[str, Any]:
    """Returns the profile configuration for a given Facebook page ID."""
    return CHANNELS_REGISTRY.get(page_id, {
        "slug": "generic_page",
        "name": "Viral Puzzle Reels",
        "tagline": "Infinite Viral Puzzles",
        "primary_mode": "grid_hunter",
        "supported_modes": ["grid_hunter", "optical_swirl", "pemdas_math"],
        "theme": "dark_slate",
        "hashtags": ["#ViralPuzzles", "#BrainTeaser", "#ViralReels"]
    })

def list_all_pages() -> List[str]:
    """Returns list of all active Facebook Page IDs."""
    return list(CHANNELS_REGISTRY.keys())
