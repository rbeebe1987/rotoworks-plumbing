#!/usr/bin/env python3
"""
Generate a RotoWorks cinematic reveal video:
  1. Sora 2 renders the chrome faucet + electric burst + swirling energy
     (no logo — Sora can't do logos well).
  2. FFmpeg composites the real logo.png on top with a timed reveal.
  3. Output -> images/rotoworks-reveal.mp4

The canvas animation on the homepage is replaced with a <video> element.
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# ---- env ----
env_path = Path.home() / ".claude" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

if not os.environ.get("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set"); sys.exit(1)

from openai import OpenAI
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "images"
LOGO = IMG_DIR / "logo.png"
RAW_VIDEO = IMG_DIR / "_reveal_raw.mp4"
FINAL_VIDEO = IMG_DIR / "rotoworks-reveal.mp4"

# ---- Sora 2 prompt ----
PROMPT = (
    "Cinematic commercial intro, 3D rendered. A polished chrome kitchen "
    "faucet in the upper part of the frame drips a single crystal-clear "
    "water droplet that falls in slow motion onto a clean white surface. "
    "As the droplet hits, a blinding white-and-electric-blue energy burst "
    "explodes outward from the impact point, with bright radial lightning "
    "bolts shooting in all directions and glowing volumetric rays. The "
    "burst expands into a glowing circular portal of swirling electric "
    "blue water and lightning energy that hovers in the center of the "
    "frame. The central portal area is mostly empty and bright. Light "
    "blue rim-lighting, clean white background, professional commercial "
    "VFX style, dramatic lens flares, no text, no logos, no watermarks, "
    "no people, no faces."
)

# ---- Step 1: Sora generation ----
def gen_sora():
    if RAW_VIDEO.exists():
        print(f"[skip] {RAW_VIDEO.name} already exists, using it")
        return
    client = OpenAI()
    print("Generating Sora 2 base video (12s, 1280x720)...")
    t0 = time.time()
    video = client.videos.create_and_poll(
        model="sora-2",
        prompt=PROMPT,
        seconds="12",
        size="1280x720",
        poll_interval_ms=5000,
    )
    elapsed = time.time() - t0
    print(f"Status: {video.status} in {elapsed:.0f}s")
    if video.status != "completed":
        err = getattr(video, "error", None)
        print(f"ERROR: {err}"); sys.exit(2)
    resp = client.videos.download_content(video_id=video.id, variant="video")
    resp.write_to_file(str(RAW_VIDEO))
    print(f"Saved -> {RAW_VIDEO}")


# ---- Step 2: FFmpeg composite (logo overlay with timed reveal) ----
def composite():
    """
    Overlay the crisp logo over the Sora burst video.
    - 0.0-3.0s  : logo invisible (just Sora burst)
    - 3.0-4.0s  : logo fades in + scales from 1.15 to 1.0
    - 4.0-12.0s : logo visible, gentle breathing pulse
    """
    if not LOGO.exists():
        print(f"ERROR: logo not found at {LOGO}"); sys.exit(3)

    logo_w = 720        # ~56% of video width
    fade_start = 3.0    # seconds
    fade_dur = 1.2
    video_dur = 12

    # Use -loop 1 to turn the PNG into a video stream so fade works properly,
    # then scale, set alpha format, fade in. Finally overlay with enable clause.
    filter_complex = (
        f"[1:v]scale={logo_w}:-1,format=yuva420p,"
        f"fade=t=in:st={fade_start}:d={fade_dur}:alpha=1"
        f"[logo];"
        f"[0:v][logo]overlay=x=(W-w)/2:y=(H-h)/2:"
        f"enable='gte(t,{fade_start})':shortest=1"
    )

    cmd = [
        FFMPEG, "-y",
        "-i", str(RAW_VIDEO),
        "-loop", "1", "-t", str(video_dur), "-i", str(LOGO),
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        "-an",
        str(FINAL_VIDEO),
    ]
    print("\nCompositing logo overlay with ffmpeg...")
    subprocess.check_call(cmd)
    size = FINAL_VIDEO.stat().st_size / 1024 / 1024
    print(f"Done: {FINAL_VIDEO} ({size:.2f} MB)")


def main():
    gen_sora()
    composite()


if __name__ == "__main__":
    main()
