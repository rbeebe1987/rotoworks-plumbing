#!/usr/bin/env python3
"""
Generate map hero images for each RotoWorks service area page.

Uses the `staticmap` Python library to render real OpenStreetMap tiles with
red markers for each area. No API key required.
"""
import sys
import subprocess
from pathlib import Path

# Install staticmap + pillow if missing
try:
    from staticmap import StaticMap, CircleMarker, IconMarker  # noqa: F401
except ImportError:
    print("Installing staticmap...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "staticmap", "pillow"])
    from staticmap import StaticMap, CircleMarker

from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = Path(__file__).resolve().parent.parent / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Output dimensions — matches the hero aspect ratio
WIDTH = 1792
HEIGHT = 1024

# Anchor coordinates (lat, lon) for each service area
TEMECULA = (33.4936, -117.1484)
MURRIETA = (33.5539, -117.2139)
MENIFEE = (33.6978, -117.1852)
LAKE_ELSINORE = (33.6681, -117.3273)
HEMET = (33.7475, -116.9719)
FALLBROOK = (33.3764, -117.2511)
ESCONDIDO = (33.1192, -117.0864)

RED = "#C8102E"
NAVY = "#0A1F44"

JOBS = [
    {
        "slug": "overview",
        "center": (33.55, -117.15),
        "zoom": 10,
        "markers": [TEMECULA, MURRIETA, MENIFEE, LAKE_ELSINORE, FALLBROOK],
    },
    {
        "slug": "temecula",
        "center": TEMECULA,
        "zoom": 12,
        "markers": [TEMECULA],
    },
    {
        "slug": "murrieta",
        "center": MURRIETA,
        "zoom": 12,
        "markers": [MURRIETA],
    },
    {
        "slug": "menifee",
        "center": MENIFEE,
        "zoom": 12,
        "markers": [MENIFEE],
    },
    {
        "slug": "riverside-county",
        "center": (33.72, -117.05),
        "zoom": 10,
        "markers": [TEMECULA, MURRIETA, MENIFEE, LAKE_ELSINORE, HEMET],
    },
    {
        "slug": "san-diego-county",
        "center": (33.2, -117.15),
        "zoom": 10,
        "markers": [FALLBROOK, ESCONDIDO, TEMECULA],
    },
]

# Use the standard OSM tile server (staticmap default). For production use,
# Carto / Stamen tiles would be cleaner — this is fine for one-off generation.
TILE_URL = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"


def render_marker_layered(base_img, markers, center_lat, center_lon, zoom, width, height):
    """Draw custom red pin markers with shadow over the map."""
    draw = ImageDraw.Draw(base_img, "RGBA")

    def latlon_to_px(lat, lon):
        # Web Mercator projection
        import math
        n = 2 ** zoom
        x_tile = (lon + 180.0) / 360.0 * n
        lat_rad = math.radians(lat)
        y_tile = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
        center_x_tile = (center_lon + 180.0) / 360.0 * n
        c_lat_rad = math.radians(center_lat)
        center_y_tile = (1.0 - math.log(math.tan(c_lat_rad) + 1 / math.cos(c_lat_rad)) / math.pi) / 2.0 * n
        px = (x_tile - center_x_tile) * 256 + width / 2
        py = (y_tile - center_y_tile) * 256 + height / 2
        return int(px), int(py)

    for lat, lon in markers:
        px, py = latlon_to_px(lat, lon)
        # Shadow
        r = 26
        draw.ellipse((px - r - 2, py - r + 4, px + r - 2, py + r + 4),
                     fill=(0, 0, 0, 90))
        # Outer white ring
        draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 255, 255))
        # Red center
        draw.ellipse((px - r + 5, py - r + 5, px + r - 5, py + r - 5),
                     fill=(200, 16, 46, 255))
        # Inner white dot
        dot = 8
        draw.ellipse((px - dot, py - dot, px + dot, py + dot),
                     fill=(255, 255, 255, 255))


def generate_one(job):
    slug = job["slug"]
    out_path = OUT_DIR / f"area-{slug}.png"
    if out_path.exists():
        print(f"[skip] {out_path.name} already exists")
        return out_path

    print(f"[gen ] {slug}... ", end="", flush=True)
    m = StaticMap(WIDTH, HEIGHT, url_template=TILE_URL)
    # Tell staticmap what to render by giving it a marker at the center
    # (we'll draw our own markers on top for quality)
    m.add_marker(CircleMarker(
        (job["center"][1], job["center"][0]),  # staticmap is (lon, lat)
        "#00000000",
        0,
    ))
    img = m.render(zoom=job["zoom"])

    # Overlay custom markers
    render_marker_layered(
        img, job["markers"],
        job["center"][0], job["center"][1], job["zoom"],
        WIDTH, HEIGHT,
    )

    img.save(out_path, "PNG", optimize=True)
    print(f"done -> {out_path.name}")
    return out_path


def main():
    print(f"Output dir: {OUT_DIR}\n")
    ok = 0
    for job in JOBS:
        try:
            generate_one(job)
            ok += 1
        except Exception as e:
            print(f"FAIL: {e}")
    print(f"\n{ok}/{len(JOBS)} maps generated")


if __name__ == "__main__":
    main()
