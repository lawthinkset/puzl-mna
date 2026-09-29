import math
import wave
import numpy as np
from pathlib import Path

def generate_puzzle_audio(
    duration: float = 14.0,
    countdown_duration: float = 14.0,
    output_wav: str = "temp_audio.wav",
    sample_rate: int = 44100
):
    """
    Synthesizes a 14-second high-retention suspense audio track:
    - Hypnotic cinematic sub-drone (60Hz + 90Hz + 120Hz harmonics)
    - Steady metronome clock ticks for the first 9 seconds
    - Accelerating heartbeat & tension clicks in final 5 seconds
    - High-urgency white noise riser sweep in the final 2 seconds
    - Dramatic 'Time's Up' impact chord at the end (ZERO answer chime)
    """
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    # 1. Hypnotic low suspense drone
    drone = 0.09 * np.sin(2 * np.pi * 60 * t) + 0.05 * np.sin(2 * np.pi * 90 * t) + 0.03 * np.sin(2 * np.pi * 120 * t)

    # 2. Metronome Clock Ticks
    tick_sound = np.zeros(total_samples, dtype=np.float32)
    tick_len = int(0.04 * sample_rate)
    t_tick = np.linspace(0, 0.04, tick_len, endpoint=False)
    
    # Normal crisp clock tick
    click = (
        np.sin(2 * np.pi * 2200 * t_tick) * np.exp(-t_tick * 150) * 0.45 +
        np.sin(2 * np.pi * 1100 * t_tick) * np.exp(-t_tick * 90) * 0.30
    )
    
    # Urgent high click for final seconds
    urgent_click = (
        np.sin(2 * np.pi * 3200 * t_tick) * np.exp(-t_tick * 160) * 0.55 +
        np.sin(2 * np.pi * 1600 * t_tick) * np.exp(-t_tick * 100) * 0.35
    )

    tick_times = []
    # 0.0s to 9.0s: Steady 0.5s ticks
    for ct in np.arange(0.0, min(9.0, countdown_duration - 5.0), 0.5):
        tick_times.append((ct, False))

    # 9.0s to 12.0s: 0.33s ticks
    for ct in np.arange(9.0, min(12.0, countdown_duration - 2.0), 0.33):
        tick_times.append((ct, True))

    # 12.0s to 14.0s: Rapid 0.2s double ticks
    for ct in np.arange(12.0, countdown_duration, 0.20):
        tick_times.append((ct, True))

    for tick_t, is_urgent in tick_times:
        idx = int(tick_t * sample_rate)
        end_idx = min(idx + tick_len, total_samples)
        sample_chunk = urgent_click if is_urgent else click
        tick_sound[idx:end_idx] += sample_chunk[:end_idx - idx]

    # 3. Suspense Riser Whoosh in final 2 seconds (12.0s to 14.0s)
    riser_sound = np.zeros(total_samples, dtype=np.float32)
    riser_start = max(0.0, duration - 2.2)
    riser_len = int((duration - riser_start) * sample_rate)
    if riser_len > 0:
        t_riser = np.linspace(0, 1.0, riser_len, endpoint=False)
        f_instant = 180 + 800 * (t_riser ** 2.2)
        phase = 2 * np.pi * np.cumsum(f_instant) / sample_rate
        noise = (np.random.rand(riser_len) * 2 - 1) * 0.18
        riser_wave = (np.sin(phase) * 0.35 + noise) * (t_riser ** 2)
        idx = int(riser_start * sample_rate)
        end_idx = min(idx + riser_len, total_samples)
        riser_sound[idx:end_idx] += riser_wave[:end_idx - idx]

    # 4. Dramatic 'Time Is Up' low bass impact hit in the final 0.8s
    hit_sound = np.zeros(total_samples, dtype=np.float32)
    hit_start = max(0.0, duration - 1.0)
    hit_len = int((duration - hit_start) * sample_rate)
    if hit_len > 0:
        t_hit = np.linspace(0, 1.0, hit_len, endpoint=False)
        hit_wave = (np.sin(2 * np.pi * 80 * t_hit) + 0.5 * np.sin(2 * np.pi * 40 * t_hit)) * np.exp(-t_hit * 3.5) * 0.6
        idx = int(hit_start * sample_rate)
        end_idx = min(idx + hit_len, total_samples)
        hit_sound[idx:end_idx] += hit_wave[:end_idx - idx]

    # Mix down
    mix = drone + tick_sound + riser_sound + hit_sound
    max_val = np.max(np.abs(mix))
    if max_val > 1e-5:
        mix = mix / max_val * 0.88
    
    audio_int16 = (mix * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))

    out_path = Path(output_wav)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())
        
    return str(out_path)
