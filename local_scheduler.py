"""
Local High-Reliability Scheduler for Viral Puzzle Engine.
Can be executed as a background service/daemon or invoked via Windows Task Scheduler.
Guarantees 5 daily posting runs across all 6 Facebook pages.
"""
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# UTF-8 stdout protection
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent
PYTHON_EXE = sys.executable

SLOTS_UTC = {
    1: 8,   # 08:00 UTC / 13:30 IST
    2: 12,  # 12:00 UTC / 17:30 IST
    3: 16,  # 16:00 UTC / 21:30 IST
    4: 20,  # 20:00 UTC / 01:30 IST (+1)
    5: 0    # 00:00 UTC / 05:30 IST (+1)
}

def get_current_slot() -> int:
    """Returns the current slot (1-5) based on the closest UTC hour."""
    utc_now = datetime.now(timezone.utc)
    hour = utc_now.hour
    if 6 <= hour < 10:
        return 1
    elif 10 <= hour < 14:
        return 2
    elif 14 <= hour < 18:
        return 3
    elif 18 <= hour < 22:
        return 4
    else:
        return 5

def run_slot(slot: int, publish: bool = True):
    """Executes a slot generation and publication cycle."""
    utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n[{utc_str}] 🚀 Triggering Slot #{slot} execution (publish={publish})...")
    
    cmd = [
        PYTHON_EXE,
        str(BASE_DIR / "master_runner.py"),
        "--slot", str(slot)
    ]
    if publish:
        cmd.append("--publish")
        
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    print(f"[{utc_str}] Slot #{slot} completed with return code {result.returncode}")
    return result.returncode == 0

def daemon_loop():
    """Continuous local daemon checking every minute for scheduled slots."""
    print("=" * 70)
    print("⏰ VIRAL PUZZLE ENGINE - LOCAL DAEMON SCHEDULER ACTIVE")
    print("5 Daily Slots Configured (UTC): 08:00, 12:00, 16:00, 20:00, 00:00")
    print("Press Ctrl+C to terminate.")
    print("=" * 70)

    last_executed_key = None

    while True:
        utc_now = datetime.now(timezone.utc)
        current_date = utc_now.date()
        hour = utc_now.hour
        minute = utc_now.minute

        for slot_num, target_hour in SLOTS_UTC.items():
            if hour == target_hour and 0 <= minute <= 10:
                slot_key = f"{current_date}_slot_{slot_num}"
                if last_executed_key != slot_key:
                    print(f"\n[DAEMON] Matched Slot #{slot_num} window (Hour: {hour}:00 UTC)")
                    run_slot(slot_num, publish=True)
                    last_executed_key = slot_key
                    break

        time.sleep(30)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Local scheduler runner")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background daemon loop")
    parser.add_argument("--run-now", action="store_true", help="Run the current slot immediately and exit")
    parser.add_argument("--slot", type=int, default=None, help="Force specific slot number")
    args = parser.parse_args()

    if args.daemon:
        daemon_loop()
    else:
        slot_to_run = args.slot or get_current_slot()
        run_slot(slot_to_run, publish=True)
