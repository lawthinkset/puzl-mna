# Infinite Viral Puzzle Reels Engine (Facebook Pages Network)

An automated, high-retention Facebook Reels video generation pipeline built for scaling across 8 to 12+ distinct Facebook Pages. Every puzzle is procedurally generated with mathematical algorithms, ensuring infinite unique variations with zero hardcoded repetition.

---

## 🚀 Key Rules & Viral Architecture

1. **Strict NO-ANSWER Rule**: Never discloses or highlights the answer in the video under any circumstance. Videos end with an urgent countdown and a call-to-action urging viewers to debate and comment their answers. This maximizes comment volume, repeated looping, watch time, and algorithmic virality.
2. **14.0 Second Video Length**: Every reel lasts exactly 14 seconds (420 frames @ 30 FPS). Optimized for high completion rate and automatic looping.
3. **Multi-Page Rotation (Matrix Scheduling)**: 5 daily posting slots ensure every Facebook page receives a *different* puzzle archetype per slot, cycling through all formats across the day with zero duplicate content.
4. **Infinite Procedural Generation**: Equations, spirals, 6-wire Catmull-Rom splines, anagram scrambles, 63-cell matrices, and matchstick geometries are calculated live on each run.
5. **Meta-Compliant 1080x1920 Full HD**: Strict vertical 9:16, 30 FPS, H.264 High Profile, YUV420p color, faststart streaming flag, AAC 192k audio.
6. **Procedural Suspense Soundscape**: Built-in 14s tension soundbed (sub-bass drone, steady metronome, accelerating heartbeat pulses, tension riser, sub-bass hit; zero answer chimes).
7. **Direct Graph API v21.0 Publishing**: Automated 3-step resumable publishing to Facebook Reels with page token resolution and automatic pinned engagement comments.

---

## 🧠 The 10 Viral Puzzle Archetypes

| Generator | Archetype Name | Mechanics & Engagement Driver |
| :--- | :--- | :--- |
| `grid_hunter` | **Grid Hunter (Odd One Out)** | 9×7 matrix (63 cells, A-G, 1-9) of confusing pairs (88/80, 43/34, E/F, O/Q). Prompts viewers to comment the exact grid coordinate. |
| `optical_swirl` | **Optical Swirl Vortex** | Hypnotic rotating logarithmic spiral hiding a low-contrast 3-digit number with 4 interactive options. Triggers 3-4 loop replays. |
| `pemdas_math` | **PEMDAS Order-of-Operations** | Viral math traps (`40 ÷ 10 × 4 - 4`, `8 ÷ 2(2 + 2)`) with Option A vs Option B split. Sparks fierce debate in comment threads. |
| `rebus_puzzle` | **Visual Rebus Equation** | 3D emoji transparent assets + letter math (`K + 👑 = KING`, `W + 👑 = ?`). Quick comprehension and viral comment responses. |
| `word_guess` | **Anagram Word Scramble** | Floating animated letter tiles, mystery slot boxes, and category clues. No solution revealed; viewers race to unscramble in comments. |
| `tangled_wires` | **6-Way Tangled Wire Charger** | 6 braided/intertwined Catmull-Rom spline cables connecting to a charging phone. Viewers trace with their finger to find the real wire. |
| `pause_silhouette` | **Pause Challenge** | 5 procedural physics modes (orbit, ricochet, pendulum, zoom, figure-8) across 100+ 3D assets. Challenges viewers to pause on the silhouette. |
| `matchstick_puzzle` | **Matchstick Equation Fix** | Realistic 7-segment wooden matches with red sulfur tips. "Move 1 stick to fix the equation" (e.g. `6 + 4 = 4`). |
| `shape_counter` | **Concentric Reticle Counter** | Overlapping geometric radar reticles scattering numbered shapes. Challenges viewers to count the target before time runs out. |
| `shadow_glitch` | **Shadow Glitch Spotter** | Center 3D hero with 4 cast silhouettes (A, B, C, D) where 1 has a subtle geometric glitch. Viewers inspect every shadow angle. |

---

## 📂 Project Structure

```
viral_puzzle_engine/
│
├── .github/workflows/
│   └── viral_puzzle_engine.yml   # GitHub Actions workflow for 5 daily scheduled slots
│
├── assets/                       # 3D transparent icons & bundled bold TrueType font
│   ├── fonts/font_bold.ttf
│   └── *.png
│
├── core/
│   ├── audio_engine.py           # 14s tension soundscape generator (ticks, heartbeats, riser)
│   ├── ui_renderer.py            # Studio broadcast UI (header cards, timer bar, urgency CTA)
│   └── video_muxer.py            # FFmpeg 1080x1920 H.264/AAC faststart muxer
│
├── generators/
│   ├── __init__.py               # Exports all 10 generators
│   ├── base_generator.py         # Abstract base generator
│   ├── grid_hunter.py            # 9x7 coordinate odd-one-out matrix
│   ├── optical_swirl.py          # Rotating spiral hidden number
│   ├── pemdas_math.py            # Viral order of operations trap
│   ├── rebus_puzzle.py           # 3D emoji word equation
│   ├── word_guess.py             # Anagram scramble floating tiles
│   ├── tangled_wires.py          # 6 braided Catmull-Rom cables
│   ├── pause_silhouette.py       # 5-mode physics pause reflex
│   ├── matchstick_puzzle.py      # 7-segment matchstick equation fix
│   ├── shape_counter.py          # Concentric radar target counter
│   └── shadow_glitch.py          # Geometric glitch shadow spotter
│
├── channels/
│   ├── page_registry.py          # 8 Facebook Pages registry & theme configuration
│   └── scheduler.py              # Permutation matrix for 5 daily posting slots
│
├── upload/
│   └── facebook_uploader.py      # Meta Graph API v21.0 resumable Reels uploader
│
├── master_runner.py              # Master orchestrator CLI
├── requirements.txt              # Pure Python dependencies
└── README.md
```

---

## 🛠️ Installation & Setup

1. **Install FFmpeg**:
   - Ensure `ffmpeg` is installed and available in your system `PATH`.
2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Facebook Page Tokens**:
   - Place your `facebook_pages_tokens.json` in `C:\Users\kreg9\facebook_pages_tokens.json` (or set environment variable `FACEBOOK_PAGES_JSON`).

---

## 💻 CLI Usage

### View the 5-Slot Rotation Schedule
```bash
python master_runner.py --show-schedule
```

### Test-Render a Specific Puzzle (No Upload)
```bash
# Render a specific puzzle archetype:
python master_runner.py --puzzle grid_hunter --mode render
python master_runner.py --puzzle tangled_wires --mode render
python master_runner.py --puzzle pemdas_math --mode render
```

### Render Slot 1 for All Pages (Dry Run)
```bash
python master_runner.py --slot 1 --mode render
```

### Run and Publish Slot 1 to Facebook Reels
```bash
python master_runner.py --slot 1 --mode publish
```

---

## ⚡ GitHub Actions Automation

The repository includes `.github/workflows/viral_puzzle_engine.yml` which automates execution across 5 daily posting slots:
- **Slot 1**: 08:00 UTC
- **Slot 2**: 12:00 UTC
- **Slot 3**: 16:00 UTC
- **Slot 4**: 20:00 UTC
- **Slot 5**: 00:00 UTC

### GitHub Secret Configuration:
Add a secret named `FACEBOOK_PAGES_JSON` in your GitHub repository settings (**Settings > Secrets and variables > Actions**) containing your JSON object mapping Page IDs to Page Access Tokens.
