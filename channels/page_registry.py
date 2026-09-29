"""
Page Profiles and Thematic Channel Registry for the Viral Puzzle Network.
Configured for the 6 Target Logic & Brain Teaser Facebook Pages.
Each page has designated primary modes, studio visual themes, hashtags,
and viral pinned engagement comments.
"""
from typing import Dict, Any, List

CHANNELS_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Page 1: Logical Rhinos
    "1300440873161089": {
        "slug": "logical_rhinos",
        "name": "Logical Rhinos",
        "tagline": "Sharpen Your Instincts • Daily Brain Teasers & Viral Logic Puzzles",
        "primary_mode": "grid_hunter",
        "supported_modes": ["grid_hunter", "pemdas_math", "logic_lock", "pause_silhouette"],
        "theme": "dark_slate",
        "hashtags": ["#LogicalRhinos", "#LogicPuzzle", "#BrainTeaser", "#OddOneOut", "#ViralReels", "#IQTest"],
        "pinned_comment": "🦏 97% fail on their first try! What is your exact coordinate or answer? Drop it below and debate! 👇"
    },

    # Page 2: Bison Logics
    "1321506077717337": {
        "slug": "bison_logics",
        "name": "Bison Logics",
        "tagline": "Unstoppable Mind Power • Daily Deduction & Math Puzzles",
        "primary_mode": "pemdas_math",
        "supported_modes": ["pemdas_math", "matchstick_puzzle", "optical_swirl", "word_guess"],
        "theme": "dark_slate",
        "hashtags": ["#BisonLogics", "#MathIQ", "#PEMDAS", "#MathDebate", "#BrainTraining", "#ViralReels"],
        "pinned_comment": "🦬 Only 1 in 100 solve this correctly without pausing! What is your answer? Comment below! 👇"
    },

    # Page 3: LogicSteps Lens
    "1313658835168646": {
        "slug": "logicsteps_lens",
        "name": "LogicSteps Lens",
        "tagline": "Look Closer • Step-by-Step Logic Riddles & Hidden Clues",
        "primary_mode": "optical_swirl",
        "supported_modes": ["optical_swirl", "shape_counter", "shadow_glitch", "grid_hunter"],
        "theme": "vibrant_navy",
        "hashtags": ["#LogicSteps", "#OpticalIllusion", "#HiddenNumber", "#LookCloser", "#ViralReels"],
        "pinned_comment": "🔍 Did you spot the number in time or did you need to replay? Comment your answer and how many seconds it took! 👇"
    },

    # Page 4: Avenue Logics
    "1276928968848084": {
        "slug": "avenue_logics",
        "name": "Avenue Logics",
        "tagline": "The Premier Boulevard for Razor-Sharp Minds • Daily Brain Games",
        "primary_mode": "rebus_puzzle",
        "supported_modes": ["rebus_puzzle", "word_guess", "pemdas_math", "grid_hunter"],
        "theme": "deep_purple",
        "hashtags": ["#AvenueLogics", "#RebusPuzzle", "#WordRiddle", "#BrainGames", "#ViralReels"],
        "pinned_comment": "⚡ Are you Team A or Team B? Explain your logic in the comments and see who agrees with you! 👇"
    },

    # Page 5: LostLogic Lens
    "1236588396214516": {
        "slug": "lostlogic_lens",
        "name": "LostLogic Lens",
        "tagline": "Finding Logic in the Impossible • High-Difficulty Logic Mysteries",
        "primary_mode": "logic_lock",
        "supported_modes": ["logic_lock", "shadow_glitch", "pause_silhouette", "optical_swirl"],
        "theme": "vibrant_navy",
        "hashtags": ["#LostLogic", "#CrackTheCode", "#VaultPuzzle", "#BrainTeaser", "#LogicIQ", "#ViralReels"],
        "pinned_comment": "🔐 Only 2% can deduce all 3 digits before time runs out! What is your code? Drop it below! 👇"
    },

    # Page 6: LogicFix Lens
    "1345900581939535": {
        "slug": "logicfix_lens",
        "name": "LogicFix Lens",
        "tagline": "Your Daily Brain Fix • Addictive Logic & Reflex Puzzles",
        "primary_mode": "matchstick_puzzle",
        "supported_modes": ["matchstick_puzzle", "pause_silhouette", "shape_counter", "grid_hunter"],
        "theme": "clean_light",
        "hashtags": ["#LogicFix", "#MatchstickPuzzle", "#EquationFix", "#MindWorkout", "#ViralReels"],
        "pinned_comment": "💡 Can you fix this equation or spot the anomaly in under 10 seconds? Drop your move below! 👇"
    }
}

def get_channel_config(page_id: str) -> Dict[str, Any]:
    """Returns the profile configuration for a given Facebook page ID."""
    return CHANNELS_REGISTRY.get(page_id, {
        "slug": f"page_{page_id}",
        "name": f"Logic Channel {page_id[-4:]}",
        "tagline": "Daily Viral Brain & Logic Puzzles",
        "primary_mode": "grid_hunter",
        "supported_modes": ["grid_hunter", "pemdas_math", "logic_lock"],
        "theme": "dark_slate",
        "hashtags": ["#BrainPuzzles", "#LogicIQ", "#ViralReels"],
        "pinned_comment": "🔥 Comment your solution below and challenge a friend! 👇"
    })

def list_all_pages() -> List[Dict[str, Any]]:
    """Returns all registered channels as a list with page_id injected."""
    res = []
    for pid, cfg in CHANNELS_REGISTRY.items():
        item = dict(cfg)
        item["page_id"] = pid
        res.append(item)
    return res
