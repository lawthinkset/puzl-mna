from .base_generator import BaseGenerator
from .grid_hunter import GridHunterGenerator
from .optical_swirl import OpticalSwirlGenerator
from .pemdas_math import PemdasMathGenerator
from .rebus_puzzle import RebusPuzzleGenerator
from .word_guess import WordGuessGenerator
from .tangled_wires import TangledWiresGenerator
from .pause_silhouette import PauseSilhouetteGenerator
from .matchstick_puzzle import MatchstickPuzzleGenerator
from .shape_counter import ShapeCounterGenerator
from .shadow_glitch import ShadowGlitchGenerator

ALL_GENERATORS = {
    "grid_hunter": GridHunterGenerator,
    "optical_swirl": OpticalSwirlGenerator,
    "pemdas_math": PemdasMathGenerator,
    "rebus_puzzle": RebusPuzzleGenerator,
    "word_guess": WordGuessGenerator,
    "tangled_wires": TangledWiresGenerator,
    "pause_silhouette": PauseSilhouetteGenerator,
    "matchstick_puzzle": MatchstickPuzzleGenerator,
    "shape_counter": ShapeCounterGenerator,
    "shadow_glitch": ShadowGlitchGenerator
}
