#!/usr/bin/env python3
"""
Replace the old hero block in each service page with a new .hero-split
section (photo background + headline + CALL button + estimate form card),
matching the homepage treatment.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"

# Per-service hero copy (h1 + subtitle). Photo slug matches the .png filename.
SERVICES = {
    "drain-cleaning": {
        "h1": "Drain Cleaning in Temecula &amp; Murrieta",
        "sub": "Fast, effective drain clearing for kitchens, bathrooms, and main lines. Same-day service when you need it.",
        "alt": "RotoWorks plumber cleaning a kitchen drain",
    },
    "water-heater": {
        "h1": "Water Heater Repair &amp; Installation in Temecula",
        "sub": "Tank and tankless water heaters. We repair, replace, and install &mdash; often the same day you call.",
        "alt": "RotoWorks plumber installing a water heater",
    },
    "leak-detection": {
        "h1": "Leak Detection &amp; Repair in Temecula",
        "sub": "Hidden leaks waste water, drive up bills, and damage your home. We find and fix them fast.",
        "alt": "RotoWorks plumber using electronic leak detection equipment",
    },
    "toilet-repair": {
        "h1": "Toilet Repair &amp; Replacement in Temecula",
        "sub": "Running, leaking, or constantly clogging? We fix toilet problems right the first time.",
        "alt": "RotoWorks plumber repairing a toilet",
    },
    "faucet-fixture": {
        "h1": "Faucet &amp; Fixture Repair in Temecula",
        "sub": "Dripping faucets, leaky valves, and outdated fixtures? We repair and install them all.",
        "alt": "RotoWorks plumber installing a kitchen faucet",
    },
    "garbage-disposal": {
        "h1": "Garbage Disposal Repair in Temecula",
        "sub": "Jammed, leaking, or making strange noises? We get your disposal working again fast.",
        "alt": "RotoWorks plumber repairing a garbage disposal",
    },
    "sewer-line": {
        "h1": "Sewer Line Cleaning &amp; Repair in Temecula",
        "sub": "Sewer backups, tree root intrusion, and slow drains. We clear and repair it all.",
        "alt": "RotoWorks plumber inspecting a sewer line with a camera",
    },
    "water-line": {
        "h1": "Water Line Repair &amp; Repiping in Temecula",
        "sub": "Low pressure, discolored water, or a busted main? We repair and replace water lines fast.",
        "alt": "RotoWorks plumber soldering a copper water line",
    },
    "emergency-service": {
        "h1": "24/7 Emergency Plumbing Service in Temecula",
        "sub": "Burst pipe, sewage backup, or flooding at 2 AM? We're on our way &mdash; day or night.",
        "alt": "RotoWorks plumber arriving for an emergency service call",
    },
}


def build_hero(slug, data):
    return f'''    <section class="hero-split">
      <div class="carousel-track">
        <img src="../images/service-{slug}.png" alt="{data['alt']}" class="carousel-img active">
      </div>
      <div class="hero-overlay"></div>

      <div class="hero-split-inner">
        <div class="hero-split-content">
          <h1>{data['h1']}</h1>
          <p>{data['sub']}</p>
          <div class="hero-buttons">
            <a href="tel:9510000000" class="btn btn-red btn-lg">
              <i class="fas fa-phone" style="margin-right:0.5rem;"></i> CALL (951) 000-0000
            </a>
          </div>
          <ul class="hero-trust-list">
            <li><i class="fas fa-check"></i> 24/7 Emergency Response</li>
            <li><i class="fas fa-check"></i> Price Beat Guarantee</li>
            <li><i class="fas fa-check"></i> Licensed &amp; Insured</li>
          </ul>
        </div>

        <aside class="hero-split-form">
          <div class="hero-form-card">
            <h2>Get a Free Estimate</h2>
            <p class="hero-form-subtitle">We respond in 30 minutes or less.</p>
            <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
              <input type="text" name="_gotcha" style="display:none">
              <div class="form-group">
                <input type="text" name="name" required placeholder="Your Name">
              </div>
              <div class="form-group">
                <input type="tel" name="phone" required placeholder="Phone Number" pattern="[0-9]{{10}}">
              </div>
              <div class="form-group">
                <textarea name="issue" required placeholder="Briefly describe your plumbing issue" rows="3"></textarea>
              </div>
              <button type="submit" class="form-submit">GET FREE ESTIMATE</button>
              <p class="form-note">Or call <a href="tel:9510000000">(951) 000-0000</a> for fastest service.</p>
            </form>
          </div>
        </aside>
      </div>
    </section>'''


# Regex patterns for the two legacy hero styles
PAGE_HERO_RE = re.compile(
    r'    <section class="page-hero">.*?</section>',
    re.DOTALL,
)
SERVICE_HERO_IMG_RE = re.compile(
    r'    <div class="service-hero-img">.*?</div>',
    re.DOTALL,
)


def replace_hero(slug, data):
    path = SERVICES_DIR / f"{slug}.html"
    if not path.exists():
        print(f"[skip] {path} not found")
        return False

    html = path.read_text(encoding="utf-8")
    new_block = build_hero(slug, data)

    if "class=\"hero-split\"" in html:
        print(f"[skip] {slug}: already has hero-split")
        return False

    new_html, n1 = PAGE_HERO_RE.subn(new_block, html, count=1)
    if n1 == 0:
        new_html, n2 = SERVICE_HERO_IMG_RE.subn(new_block, html, count=1)
        if n2 == 0:
            print(f"[FAIL] {slug}: no hero block found to replace")
            return False

    path.write_text(new_html, encoding="utf-8")
    print(f"[ok  ] {slug}.html")
    return True


def main():
    print(f"Services dir: {SERVICES_DIR}\n")
    count = 0
    for slug, data in SERVICES.items():
        if replace_hero(slug, data):
            count += 1
    print(f"\n{count}/{len(SERVICES)} pages updated")


if __name__ == "__main__":
    main()
