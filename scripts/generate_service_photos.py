#!/usr/bin/env python3
"""
Generate 7 RotoWorks Plumbing service hero photos via DALL-E 3.

Each prompt features a DIFFERENT person (varied age, gender, ethnicity) performing
the specific service in a real home setting. Landscape 1792x1024 output.
"""
import os
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request

# Load OPENAI_API_KEY from ~/.claude/.env
env_path = Path.home() / ".claude" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY not set in environment or ~/.claude/.env")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "openai"])
    from openai import OpenAI

client = OpenAI(api_key=API_KEY)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = (
    "Photorealistic professional photograph, bright natural daylight, shallow depth of "
    "field, clean modern suburban California home interior, high detail, 35mm lens, "
    "magazine-quality commercial photography. The plumber is wearing a navy blue work "
    "shirt and looks friendly, confident, and competent. No text, no logos, no watermarks."
)

# 7 services, each with a UNIQUE person description
JOBS = [
    {
        "slug": "leak-detection",
        "person": "a middle-aged Hispanic man with short black hair and a neatly trimmed beard, mid-40s",
        "scene": (
            "using a handheld electronic leak detection device with a stethoscope-like "
            "probe against a bathroom wall, concentrating intently, a small orange "
            "moisture meter visible beside him, pristine tiled bathroom background"
        ),
    },
    {
        "slug": "toilet-repair",
        "person": "a young woman plumber in her late 20s with a blonde ponytail tucked under a navy cap, fair skin",
        "scene": (
            "kneeling next to a white porcelain toilet in a bright modern bathroom, "
            "tightening a supply line valve with a wrench, toolbox open beside her, "
            "confident smile"
        ),
    },
    {
        "slug": "faucet-fixture",
        "person": "an older Black man in his mid-50s with short salt-and-pepper hair and glasses",
        "scene": (
            "installing a brushed-nickel kitchen faucet at a white quartz countertop, "
            "tightening a connection from below the sink, focused expression, modern "
            "farmhouse kitchen in background"
        ),
    },
    {
        "slug": "garbage-disposal",
        "person": "an East Asian man in his early 30s with short black hair, clean-shaven",
        "scene": (
            "crouched underneath a kitchen sink repairing a stainless-steel garbage "
            "disposal unit, headlamp on, holding a screwdriver, plumbing parts organized "
            "neatly on the floor"
        ),
    },
    {
        "slug": "sewer-line",
        "person": "a muscular white man in his late 30s with short brown hair and a light stubble",
        "scene": (
            "standing outside near an exposed sewer cleanout in a suburban front yard, "
            "feeding a professional sewer inspection camera cable into the pipe, a small "
            "monitor showing pipe interior visible on a cart next to him"
        ),
    },
    {
        "slug": "water-line",
        "person": "a South Asian woman plumber in her 30s with dark hair in a braid",
        "scene": (
            "soldering a copper water supply line with a torch in a garage utility area, "
            "wearing safety glasses, focused and precise, organized tool belt"
        ),
    },
    {
        "slug": "emergency-service",
        "person": "a Latino man in his late 30s with short dark hair, athletic build",
        "scene": (
            "arriving at a front door at dusk carrying a toolbox and flashlight, a "
            "clearly visible white service van with blue stripes parked in the driveway "
            "with headlights on, urgent but reassuring expression, warm porch light"
        ),
    },
]


def build_prompt(job):
    return (
        f"{STYLE_BASE} Wide landscape photograph of {job['person']}, "
        f"a professional plumber, {job['scene']}. "
        "Every photo in this series features a different plumber — this one is unique."
    )


def generate_one(job):
    slug = job["slug"]
    out_path = OUTPUT_DIR / f"service-{slug}.png"
    if out_path.exists():
        print(f"[skip] {out_path.name} already exists")
        return out_path

    prompt = build_prompt(job)
    print(f"[gen ] {slug}... ", end="", flush=True)
    t0 = time.time()

    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="hd",
        n=1,
    )

    url = resp.data[0].url
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as r:
        out_path.write_bytes(r.read())

    dt = time.time() - t0
    print(f"done ({dt:.1f}s) -> {out_path.name}")
    return out_path


def main():
    print(f"Output dir: {OUTPUT_DIR}\n")
    results = []
    for job in JOBS:
        try:
            results.append(generate_one(job))
        except Exception as e:
            print(f"FAILED: {e}")
            results.append(None)

    print("\n=== Summary ===")
    for job, result in zip(JOBS, results):
        status = "OK  " if result else "FAIL"
        print(f"  [{status}] service-{job['slug']}.png")


if __name__ == "__main__":
    main()
