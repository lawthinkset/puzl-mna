"""
Test and Verification Script.
Generates quick verification test reels across all 10 procedural puzzle generator types:
1. grid_hunter
2. optical_swirl
3. pemdas_math
4. rebus_puzzle
5. word_guess
6. tangled_wires
7. pause_silhouette
8. matchstick_puzzle
9. shape_counter
10. shadow_glitch
"""
import sys
import time
from pathlib import Path

# Safeguard Windows stdout encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from generators import ALL_GENERATORS

def test_all():
    out_dir = Path(__file__).parent / "output" / "test_samples"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🧪 TESTING ALL 10 INFINITE PUZZLE GENERATORS (NO-ANSWER POLICY)")
    print("=" * 60)

    for mode_name, gen_cls in ALL_GENERATORS.items():
        out_file = out_dir / f"sample_{mode_name}.mp4"
        print(f"\n--- Testing Generator: [{mode_name}] ---")
        t0 = time.time()
        
        gen = gen_cls(page_name="Puzzle Tester", theme="dark_slate")
        res_path = gen.render_video(
            output_mp4=str(out_file),
            duration=5.0,  # 5s test duration for fast verification
            fps=30
        )
        
        dt = round(time.time() - t0, 2)
        size_mb = round(Path(res_path).stat().st_size / (1024 * 1024), 2)
        print(f"✅ [{mode_name}] Rendered in {dt}s -> {out_file.name} ({size_mb} MB)")
        
        title, desc, pinned = gen.get_metadata()
        print(f"   Title: {title}")
        print(f"   Pinned Comment: {pinned.splitlines()[0]}")

    print("\n" + "=" * 60)
    print(f"🎉 ALL 10 GENERATORS VERIFIED SUCCESSFULLY!")
    print(f"Test files saved in: {out_dir}")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
