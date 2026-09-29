import os
import cv2
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

from core.audio_engine import generate_puzzle_audio
from core.video_muxer import mux_video_audio

class BaseGenerator(ABC):
    """
    Abstract Base Class for Infinite Procedural Viral Puzzle Generators.
    Ensures standard 1080x1920 9:16 vertical video output, 14-second tension curve,
    synchronized procedural audio, strict 'NO-ANSWER-DISCLOSURE' policy for max comments,
    and automatic Meta metadata generation (title, caption, pinned comment).
    """
    def __init__(self, page_name: str = "Viral Puzzles", theme: str = "dark_slate"):
        self.page_name = page_name
        self.theme = theme
        self.width = 1080
        self.height = 1920
        self.puzzle_data: Dict[str, Any] = {}

    @abstractmethod
    def generate_puzzle_state(self) -> Dict[str, Any]:
        """Procedurally generate new unique puzzle parameters."""
        pass

    @abstractmethod
    def render_frame(self, t: float, duration: float) -> np.ndarray:
        """
        Render a single frame at timestamp t in BGR format.
        CRITICAL: Never disclose the answer at any timestamp.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Tuple[str, str, str]:
        """
        Returns (title, description, pinned_comment) optimized for viral Facebook Reel engagement.
        """
        pass

    def render_video(
        self,
        output_mp4: str,
        duration: float = 14.0,
        fps: int = 30
    ) -> str:
        """
        Renders complete video frames via OpenCV, synthesizes 14s synchronized audio,
        and muxes to H.264/AAC MP4.
        """
        # Ensure fresh procedural puzzle state
        self.puzzle_data = self.generate_puzzle_state()
        
        out_file = Path(output_mp4)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        temp_raw_avi = out_file.parent / f"temp_{out_file.stem}_raw.mp4"
        temp_wav = out_file.parent / f"temp_{out_file.stem}_audio.wav"

        total_frames = int(duration * fps)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(temp_raw_avi), fourcc, fps, (self.width, self.height))

        print(f"[generator] Rendering {total_frames} frames ({duration}s @ {fps}fps)...")
        for frame_idx in range(total_frames):
            t = frame_idx / fps
            frame_bgr = self.render_frame(t, duration)
            writer.write(frame_bgr)
            
        writer.release()

        # Generate Procedural 14-second Audio (Accelerating tension, no answer chime)
        print(f"[generator] Synthesizing synchronized suspense audio...")
        generate_puzzle_audio(
            duration=duration,
            countdown_duration=duration,
            output_wav=str(temp_wav)
        )

        # Mux to high-spec 1080p MP4
        print(f"[generator] Muxing to {out_file.name} via FFmpeg...")
        mux_video_audio(
            video_path=str(temp_raw_avi),
            audio_path=str(temp_wav),
            output_path=str(out_file),
            fps=fps
        )

        # Cleanup temporary intermediary files
        if temp_raw_avi.exists():
            temp_raw_avi.unlink()
        if temp_wav.exists():
            temp_wav.unlink()

        file_mb = round(out_file.stat().st_size / (1024 * 1024), 2)
        print(f"[SUCCESS] Created Reel: {out_file} ({file_mb} MB)")
        return str(out_file)
