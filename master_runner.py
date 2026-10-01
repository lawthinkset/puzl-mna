"""
Master Infinite Puzzle Reel Factory & Network Publisher.
Coordinates procedural puzzle generation, audio synthesis, FFmpeg rendering,
and automated multi-page Facebook Reel publishing across all 10 puzzle modes.
"""
import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

# UTF-8 encoding safeguard on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from generators import ALL_GENERATORS
from channels.page_registry import CHANNELS_REGISTRY, get_channel_config, list_all_pages
from channels.scheduler import get_slot_puzzle_mapping, print_daily_schedule
from upload.facebook_uploader import upload_reel_to_facebook, load_page_tokens

def generate_reel_for_page(
    page_id: str,
    mode_override: str = None,
    output_filename: str = None,
    duration: float = 14.0,
    fps: int = 30
) -> dict:
    """
    Generates a full 1080x1920 viral reel tailored to the specific page's branding.
    14s duration. Never discloses the answer.
    """
    config = get_channel_config(page_id)
    page_name = config["name"]
    page_slug = config["slug"]
    theme = config.get("theme", "dark_slate")

    # Select puzzle mode
    if mode_override and mode_override in ALL_GENERATORS:
        chosen_mode = mode_override
    else:
        chosen_mode = random.choice(list(ALL_GENERATORS.keys()))

    generator_cls = ALL_GENERATORS[chosen_mode]
    generator = generator_cls(page_name=page_name, theme=theme)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not output_filename:
        output_filename = f"reel_{page_slug}_{chosen_mode}_{ts}.mp4"

    final_video_path = OUTPUT_DIR / output_filename
    
    print("\n" + "=" * 65)
    print(f"🎬 GENERATING 14S REEL FOR: {page_name.upper()} ({page_id})")
    print(f"Puzzle Mode: [{chosen_mode.upper()}] | Theme: [{theme}]")
    print(f"Target File: {final_video_path.name}")
    print("=" * 65)

    # Render video + audio
    generator.render_video(
        output_mp4=str(final_video_path),
        duration=duration,
        fps=fps
    )

    # Generate viral metadata
    title, description, pinned_comment = generator.get_metadata()

    return {
        "page_id": page_id,
        "page_name": page_name,
        "mode": chosen_mode,
        "video_path": str(final_video_path),
        "title": title,
        "description": description,
        "pinned_comment": pinned_comment,
        "generated_at": ts
    }

def main():
    parser = argparse.ArgumentParser(description="Master Infinite Viral Puzzle Reel Factory")
    parser.add_argument("--page", type=str, default="all", help="Target Page ID or 'all' to run across all pages")
    parser.add_argument("--slot", type=int, default=None, help="Run specific posting slot (1-5) using cross-page rotation")
    valid_modes = list(ALL_GENERATORS.keys()) + ["publish", "render"]
    parser.add_argument("--mode", type=str, default=None, choices=valid_modes, help="Force specific puzzle mode or specify 'publish'/'render'")
    parser.add_argument("--count", type=int, default=1, help="Number of reels per target page")
    parser.add_argument("--publish", action="store_true", help="Automatically upload generated reels to Facebook")
    parser.add_argument("--duration", type=float, default=14.0, help="Duration in seconds (default: 14.0)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--show-schedule", action="store_true", help="Display the 5-slot daily schedule matrix")
    args = parser.parse_args()

    if args.show_schedule:
        print_daily_schedule(5)
        return

    should_publish = args.publish or (args.mode == "publish")
    forced_puzzle_mode = args.mode if (args.mode and args.mode not in ("publish", "render")) else None

    # Auto-determine slot from current UTC hour if slot is not explicitly passed
    current_slot = args.slot
    if not current_slot:
        utc_hour = datetime.utcnow().hour
        if 6 <= utc_hour < 10:
            current_slot = 1
        elif 10 <= utc_hour < 14:
            current_slot = 2
        elif 14 <= utc_hour < 18:
            current_slot = 3
        elif 18 <= utc_hour < 22:
            current_slot = 4
        else:
            current_slot = 5
        print(f"[master] Auto-detected daily slot #{current_slot} (UTC hour {utc_hour:02d}:00)")
    else:
        print(f"[master] Using specified daily slot #{current_slot}")

    slot_mapping = get_slot_puzzle_mapping(current_slot)

    if args.page == "all":
        target_pages = [p["page_id"] for p in list_all_pages()]
    else:
        target_pages = [args.page]

    print(f"[master] Starting generation run across {len(target_pages)} page(s) (14s video, strict no-answer policy, publish={should_publish})...")

    results = []
    failed_pages = []
    published_count = 0

    for page_id in target_pages:
        for idx in range(args.count):
            try:
                # Mode priority: forced_puzzle_mode > slot mapping > random mode
                mode_to_use = forced_puzzle_mode or slot_mapping.get(page_id, None)

                reel_info = generate_reel_for_page(
                    page_id=page_id,
                    mode_override=mode_to_use,
                    duration=args.duration,
                    fps=args.fps
                )
                results.append(reel_info)

                if should_publish:
                    print(f"\n[master] Publishing to Facebook Page: {reel_info['page_name']}...")
                    upload_res = upload_reel_to_facebook(
                        video_path=reel_info["video_path"],
                        title=reel_info["title"],
                        description=reel_info["description"],
                        page_id=page_id,
                        pinned_comment=reel_info["pinned_comment"]
                    )
                    reel_info["upload_result"] = upload_res
                    if upload_res and upload_res.get("status") == "success":
                        published_count += 1
                    else:
                        failed_pages.append(reel_info['page_name'])

            except Exception as e:
                print(f"[master] ❌ Error generating for page {page_id}: {e}")
                failed_pages.append(str(page_id))

    print("\n" + "=" * 65)
    print(f"✨ BATCH RUN COMPLETED! Generated {len(results)} reel(s). Published {published_count}/{len(results)}.")
    for r in results:
        status_str = f"Published (ID: {r.get('upload_result', {}).get('video_id', 'N/A')})" if should_publish else "Rendered"
        print(f"  • {r['page_name']} -> {Path(r['video_path']).name} [{status_str}]")
    print("=" * 65)

    if should_publish and published_count == 0 and len(target_pages) > 0:
        print("[master] ❌ CRITICAL: 0 reels published successfully!")
        sys.exit(1)

if __name__ == "__main__":
    main()
