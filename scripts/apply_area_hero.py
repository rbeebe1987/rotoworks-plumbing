#!/usr/bin/env python3
"""
Replace the old .page-hero block in each service-area page with a new
.hero-split section using the matching area map image as background.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AREAS_DIR = ROOT / "service-areas"

AREAS = {
    "index": {
        "slug": "overview",
        "h1": "Areas We Serve",
        "sub": "RotoWorks Plumbing serves communities across Riverside and North San Diego Counties. Wherever you are, we're a phone call away.",
        "alt": "Map of RotoWorks Plumbing service areas",
    },
    "temecula": {
        "slug": "temecula",
        "h1": "Plumber in Temecula, CA",
        "sub": "Your local 24/7 plumber. Licensed, insured, and we'll beat any written estimate.",
        "alt": "Map of Temecula, CA service area",
    },
    "murrieta": {
        "slug": "murrieta",
        "h1": "Plumber in Murrieta, CA",
        "sub": "Reliable plumbing for Murrieta families &mdash; 24 hours a day, 7 days a week.",
        "alt": "Map of Murrieta, CA service area",
    },
    "menifee": {
        "slug": "menifee",
        "h1": "Plumber in Menifee, CA",
        "sub": "Professional plumbing for Menifee homes and businesses with upfront pricing.",
        "alt": "Map of Menifee, CA service area",
    },
    "riverside-county": {
        "slug": "riverside-county",
        "h1": "Plumber Serving Riverside County",
        "sub": "From Lake Elsinore to Hemet, we bring honest, fast plumbing to the greater Riverside County area.",
        "alt": "Map of Riverside County service area",
    },
    "san-diego-county": {
        "slug": "san-diego-county",
        "h1": "Plumber Serving North San Diego County",
        "sub": "Just over the county line from Temecula &mdash; fast, affordable plumbing for North County San Diego.",
        "alt": "Map of North San Diego County service area",
    },
}


def build_hero(page_key, data):
    return f'''    <section class="hero-split hero-split--map">
      <div class="carousel-track">
        <img src="../images/area-{data['slug']}.png" alt="{data['alt']}" class="carousel-img active">
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


PAGE_HERO_RE = re.compile(
    r'    <section class="page-hero">.*?</section>',
    re.DOTALL,
)


def replace_hero(page_key, data):
    path = AREAS_DIR / f"{page_key}.html"
    if not path.exists():
        print(f"[skip] {path} not found")
        return False
    html = path.read_text(encoding="utf-8")
    if "class=\"hero-split hero-split--map\"" in html:
        print(f"[skip] {page_key}: already updated")
        return False
    new_block = build_hero(page_key, data)
    new_html, n = PAGE_HERO_RE.subn(new_block, html, count=1)
    if n == 0:
        print(f"[FAIL] {page_key}: no page-hero block found")
        return False
    path.write_text(new_html, encoding="utf-8")
    print(f"[ok  ] {page_key}.html")
    return True


def main():
    print(f"Areas dir: {AREAS_DIR}\n")
    ok = 0
    for key, data in AREAS.items():
        if replace_hero(key, data):
            ok += 1
    print(f"\n{ok}/{len(AREAS)} pages updated")


if __name__ == "__main__":
    main()
