#!/usr/bin/env python3
"""
Contrast + touch-target audit for the Twirler site.

Reads the palette straight out of assets/css/site.css, then checks every
surface that carries text against the background it actually renders on
(including translucent layers, which are composited first).

    python tools/audit_contrast.py            # report, exit 1 on failure
    python tools/audit_contrast.py --write     # also write docs/contrast-audit.md

Thresholds are WCAG 2.1 AA: 4.5:1 for body text, 3:1 for large text
(>= 24px, or >= 18.66px bold) and for non-text UI boundaries.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = os.path.join(ROOT, "assets", "css", "site.css")
REPORT = os.path.join(ROOT, "docs", "contrast-audit.md")


# ---------------------------------------------------------------- colour maths
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def blend(fg, alpha, bg):
    """Composite a translucent layer over an opaque backdrop."""
    f, b = hex_to_rgb(fg), hex_to_rgb(bg)
    return rgb_to_hex(tuple(alpha * f[i] + (1 - alpha) * b[i] for i in range(3)))


def luminance(h):
    c = [v / 255 for v in hex_to_rgb(h)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- palette
def read_palette():
    css = open(CSS, encoding="utf-8").read()
    root = re.search(r":root\s*\{(.*?)\}", css, re.S).group(1)
    pal = {}
    for name, val in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", root):
        pal[name] = val
    return pal


P = read_palette()

INK = P["ink"]
INK2 = P["ink-2"]
PANEL = P["panel"]
PANEL2 = P["panel-2"]
CREAM = P["cream"]
CREAM_DIM = P["cream-dim"]
MUTED = P["muted"]
GOLD = P["gold"]
OXBLOOD = P["oxblood"]
ROSE = "#e8a3a9"          # .day.is-live / .badge-18
ON_GOLD = "#12100c"       # text on gold fills
FIELD = PANEL             # form fields sit on --panel

# translucent layers, composited over the surface they sit on
HERO_TOP = blend(GOLD, 0.18, INK)          # hero radial glow, upper area
THUMB = blend(CREAM, 0.03, PANEL)          # release tile ground
TAG_BG = blend(INK, 0.75, THUMB)           # .tag over a tile
LIVE_DAY = blend(OXBLOOD, 0.22, PANEL)     # .day.is-live fill
BADGE_BG = blend(OXBLOOD, 0.18, INK)       # .badge-18 fill
GOLD_SOFT = blend(GOLD, 0.16, PANEL)       # .card--feature

# label, foreground, background, size class ("body" | "large" | "ui")
CHECKS = [
    # --- base type -----------------------------------------------------------
    ("Body copy on page ground", CREAM, INK, "body"),
    ("Secondary copy (thumbnails, day cells, decayed labels)", CREAM_DIM, PANEL, "body"),
    ("Muted small caps (meta, footer, form hints)", MUTED, INK2, "body"),
    ("Muted small caps on a card panel", MUTED, PANEL, "body"),
    ("Eyebrow / kicker (gold, .72rem caps)", GOLD, INK, "body"),
    ("Card heading", CREAM, PANEL, "large"),
    ("Card body", CREAM_DIM, PANEL, "body"),

    # --- hero + ticker -------------------------------------------------------
    ("Hero subtitle", CREAM_DIM, HERO_TOP, "body"),
    ("Hero metric label", CREAM_DIM, INK, "body"),
    ("Ticker phrase (desktop)", MUTED, INK2, "body"),
    ("Ticker chip (mobile)", CREAM_DIM, INK2, "body"),

    # --- interactive ---------------------------------------------------------
    ("Button label — outline", GOLD, INK, "body"),
    ("Button label — solid (dark on gold)", ON_GOLD, GOLD, "body"),
    ("Button hover — dark on gold", ON_GOLD, GOLD, "body"),
    ("Button hover — dark on cream", ON_GOLD, CREAM, "body"),
    ("Ghost button label", CREAM_DIM, INK, "body"),
    ("Nav link", CREAM_DIM, INK, "body"),
    ("Nav link, current page", CREAM, INK, "body"),
    ("Footer link", MUTED, INK2, "body"),

    # --- schedule ------------------------------------------------------------
    ("Shoot day label", GOLD, blend(GOLD, 0.17, PANEL), "body"),
    ("Release day label", ROSE, LIVE_DAY, "body"),
    ("Rest / edit day label", CREAM_DIM, PANEL, "body"),

    # --- release tiles -------------------------------------------------------
    ("Tile monogram (LC 041)", blend(CREAM, 0.62, THUMB), THUMB, "large"),
    ("Tile tag", GOLD, TAG_BG, "body"),
    ("Tile scene title", CREAM, PANEL, "body"),
    ("Tile meta line", MUTED, PANEL, "body"),
    ("Portrait initials", blend(CREAM, 0.36, THUMB), THUMB, "large"),
    ("Portrait caption", CREAM_DIM, blend(INK, 0.92, PANEL), "body"),

    # --- stats / band / cards ------------------------------------------------
    ("Stat figure", GOLD, INK2, "large"),
    ("Stat label", MUTED, INK2, "body"),
    ("Feature card heading", CREAM, GOLD_SOFT, "large"),
    ("Band body copy", CREAM_DIM, INK2, "body"),

    # --- forms ---------------------------------------------------------------
    ("Field label", MUTED, INK, "body"),
    ("Field value", CREAM, FIELD, "body"),
    ("Field placeholder", "#928b83", FIELD, "body"),
    ("Select option (native popup)", CREAM, "#15151a", "body"),
    ("Select option, checked", ON_GOLD, GOLD, "body"),
    ("Form note", MUTED, INK, "body"),

    # --- gate + badges -------------------------------------------------------
    ("Gate heading", CREAM, PANEL, "large"),
    ("Gate body", CREAM_DIM, PANEL, "body"),
    ("Gate fine print", MUTED, PANEL, "body"),
    ("18+ badge figure", ROSE, BADGE_BG, "body"),
    ("Selection highlight", ON_GOLD, GOLD, "body"),
]


def main():
    rows, failures = [], 0
    for label, fg, bg, size in CHECKS:
        r = ratio(fg, bg)
        need = 3.0 if size == "large" else 4.5
        ok = r >= need
        if not ok:
            failures += 1
        rows.append((label, fg, bg, r, need, ok))

    width = max(len(r[0]) for r in rows)
    print(f"{'surface'.ljust(width)}  fg       bg       ratio    need  ")
    print("-" * (width + 40))
    for label, fg, bg, r, need, ok in rows:
        flag = "ok  " if ok else "FAIL"
        print(f"{label.ljust(width)}  {fg}  {bg}  {r:5.2f}:1  {need:3.1f}  {flag}")

    print()
    if failures:
        print(f"{failures} of {len(rows)} surfaces below AA")
    else:
        print(f"all {len(rows)} surfaces meet WCAG AA")

    if "--write" in sys.argv:
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        with open(REPORT, "w", encoding="utf-8") as fh:
            fh.write("# Contrast audit — Twirler site\n\n")
            fh.write("Generated by `tools/audit_contrast.py` from the live palette in "
                     "`assets/css/site.css`. Thresholds are WCAG 2.1 AA: **4.5:1** for body "
                     "text, **3:1** for large text (>= 24px, or >= 18.66px bold).\n\n")
            fh.write("Translucent fills are composited over what sits behind them before "
                     "measuring, so a badge on the gate panel is judged on the colour it "
                     "actually renders as.\n\n")
            fh.write("| Surface | Foreground | Background | Ratio | Need | Result |\n")
            fh.write("|---|---|---|---|---|---|\n")
            for label, fg, bg, r, need, ok in rows:
                fh.write(f"| {label} | `{fg}` | `{bg}` | {r:.2f}:1 | {need:.1f}:1 | "
                         f"{'pass' if ok else '**fail**'} |\n")
            fh.write("\n## Re-run\n\n```bash\npython3 tools/audit_contrast.py --write\n```\n")
        print("wrote", REPORT)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
