import os
import subprocess
from pathlib import Path

def mux_video_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    fps: int = 30,
    crf: int = 19
) -> str:
    """
    Muxes video and procedural audio into a broadcast-standard 1080x1920 Reel MP4:
    - Codec: H.264 High Profile (libx264)
    - Pixel format: yuv420p (required by Meta / Facebook Graph API)
    - Audio: AAC 192k stereo
    - Faststart enabled (enables instant mobile buffering)
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.2",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out_file)
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg muxing failed:\n{result.stderr}")
        
    return str(out_file)
