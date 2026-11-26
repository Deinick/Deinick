#!/usr/bin/env python3
"""Draws the static pixel-art SVGs for the profile README.

    python3 scripts/make_assets.py

writes:
    assets/pixel-duel.svg      - header banner: two hooded duelists, a helper bot, a ringed planet
    assets/energy-blades.svg   - tech stack shown as glowing energy blades

All characters, sprites and scenery are original designs drawn for this
profile (MIT License). Standard library only.

To change your tech stack, edit STACK below and re-run the script.
"""
import math
import os
import random

import pixel as px

# ---------------------------------------------------------------- your stack
# (name, proficiency 0-100, blade colour). Edit freely, then re-run.
STACK = [
    ("JavaScript", 85, "#FFE81F"),
    ("TypeScript", 75, "#2E9BFF"),
    ("Python",     70, "#3DFF6E"),
    ("React",      80, "#4BD5EE"),
    ("Node.js",    70, "#7CFF4F"),
    ("Git",        75, "#FF2A2A"),
    ("Docker",     55, "#B266FF"),
]

TITLE = "DEINICK"
SUBTITLE = "CHAPTER II : THE PIXEL DUEL"

# ---------------------------------------------------------------- sprites
# Duelist, facing right. H hood, h cloak, t tunic, s skin/glove, e eyes, b belt, k boots
DUELIST = [
    "....HHHH......",
    "...HHHHHH.....",
    "..HHHHsssH....",
    "..HHHssess....",
    "..HHHsssss....",
    "..HHHHsss.....",
    "..hhHttthh....",
    ".hhhhtttthh...",
    ".hhhhtttthhss.",
    ".hhhhtttthhss.",
    ".hhhbbbbbb....",
    ".hhhtttttt....",
    ".hhhtttttt....",
    ".hhhhttttt....",
    "..hhhttttt....",
    "..hhhhtttth...",
    ".hhhhhhhhhh...",
    ".hhhh..hhhh...",
    ".hhh....hhh...",
    ".kkk....kkkk..",
]
HERO_PAL = {"H": "#5A3A22", "h": "#8B5A2B", "t": "#D9B98A", "s": "#F1C27D",
            "e": "#1A1A1A", "b": "#3B2414", "k": "#2A1A10"}
RIVAL_PAL = {"H": "#14141C", "h": "#24242F", "t": "#3A3A4A", "s": "#0A0A0F",
             "e": "#FF2A2A", "b": "#55556A", "k": "#0A0A0F"}

# Helper bot. a antenna, w hull, v visor, E eyes, o stripe, g base
BOT = [
    "....a.....",
    "....a.....",
    "..wwwwww..",
    ".wwwwwwww.",
    ".wvvvvvvw.",
    ".wvEvvEvw.",
    ".wwwwwwww.",
    ".woowwoow.",
    "..wwwwww..",
    "...gggg...",
]
BOT_PAL = {"a": "#9AA4B2", "w": "#E6E6E6", "v": "#1B2A4A", "E": "#4BD5EE",
           "o": "#FF8C1A", "g": "#6E7681"}

# Small starfighter, flying right. r fins, w hull, c cockpit, f engine
FIGHTER = [
    "..rr........",
    "..www.......",
    ".wwwwww.....",
    "fwwwwwwwwcc.",
    ".wwwwww.....",
    "..www.......",
    "..rr........",
]
FIGHTER_PAL = {"r": "#FF2A2A", "w": "#C9D1D9", "c": "#4BD5EE", "f": "#FFB000"}

# Energy-blade hilt (horizontal). g metal, L highlight, d shade, k grip ridges, s neck, E emitter, r button
HILT = [
    "...rr...........",
    "gggkgkgkgkgggssE",
    "gLLLLLLLLLLLLssE",
    "gdddddddddddddsE",
    "gggkgkgkgkgggssE",
]
HILT_PAL = {"g": "#9AA4B2", "L": "#D0D7DE", "d": "#57606A", "k": "#1B1F24",
            "s": "#30363D", "E": "#E6EDF3", "r": "#FF2A2A"}


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def cells_path(cells, P, fill, extra=""):
    d = "".join(f"M{x * P:g} {y * P:g}h{P}v{P}h-{P}z" for x, y in cells)
    return f'<path d="{d}" fill="{fill}" {extra}/>'


# ---------------------------------------------------------------- duel banner
def pixel_duel():
    W, H, P = 900, 300, 4          # P = size of one art pixel
    GW, GH = W // P, H // P        # 225 x 75 grid
    ground = 62
    rnd = random.Random(1977 % 97)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']
    o.append("""<style>
.tw{animation:tw 2.6s steps(3) infinite}@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
.hum{animation:hum .18s steps(2) infinite}@keyframes hum{0%{opacity:1}100%{opacity:.82}}
.lunge-l{animation:ll 2.4s steps(1) infinite}@keyframes ll{0%,60%{transform:translateX(0)}62%,80%{transform:translateX(4px)}82%,100%{transform:translateX(0)}}
.lunge-r{animation:lr 2.4s steps(1) infinite}@keyframes lr{0%,60%{transform:translateX(0)}62%,80%{transform:translateX(-4px)}82%,100%{transform:translateX(0)}}
.spark{transform-box:fill-box;transform-origin:center;animation:sp 2.4s steps(4) infinite}
@keyframes sp{0%,60%{opacity:0;transform:scale(.3)}62%{opacity:1;transform:scale(1)}72%{opacity:.8;transform:scale(1.5)}80%,100%{opacity:0;transform:scale(1.8)}}
.hover{animation:hv 1.6s steps(2) infinite}@keyframes hv{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.flame{animation:fl .2s steps(2) infinite}@keyframes fl{0%{opacity:1}100%{opacity:.35}}
.blink{animation:bl 1.1s steps(1) infinite}@keyframes bl{0%,50%{fill:#FF2A2A}51%,100%{fill:#3A0A0A}}
.fly{animation:fy 11s linear infinite}@keyframes fy{0%{transform:translateX(-80px)}45%{transform:translateX(980px)}100%{transform:translateX(980px)}}
.eye{animation:ey 3s steps(1) infinite}@keyframes ey{0%,92%{opacity:1}93%,97%{opacity:.2}98%,100%{opacity:1}}
</style>""")
    o.append('<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
             '<feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/>'
             '<feMergeNode in="SourceGraphic"/></feMerge></filter>'
             f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>')
    o.append('<g clip-path="url(#frame)">')

    # banded dusk sky (pixel-art gradient)
    bands = ["#07021A", "#0B0424", "#10062E", "#170938", "#1F0C40", "#2A0F47",
             "#36124C", "#43164F", "#521B52", "#621F52", "#73244F"]
    band_h = math.ceil(ground / len(bands))
    for i, c in enumerate(bands):
        o.append(rect(0, i * band_h * P, W, band_h * P + P, c))
    # dither the band edges for that 16-bit look
    for i in range(1, len(bands)):
        y = i * band_h
        cells = [(x, y - 1) for x in range(i % 2, GW, 2)]
        o.append(cells_path(cells, P, bands[i]))

    # stars
    stars = [(rnd.randrange(GW), rnd.randrange(ground - 14)) for _ in range(70)]
    for i, (sx, sy) in enumerate(stars):
        if 175 <= sx <= 200 and 5 <= sy <= 32:
            continue  # keep the planet clean
        cls = 'class="tw" ' if i % 3 == 0 else ""
        delay = f'style="animation-delay:-{rnd.uniform(0, 2.6):.2f}s" ' if cls else ""
        o.append(rect(sx * P, sy * P, P, P, "#FFFFFF" if i % 5 else "#FFE81F",
                      f'{cls}{delay}opacity="{0.9 if cls else rnd.choice([0.35, 0.55, 0.75])}"'))

    # ringed gas giant (top right) with a tilted ring, drawn cell by cell
    cx, cy, r = 188, 18, 11
    planet = {"#E08A3C": [], "#C4682A": [], "#F2B266": [], "#8E4420": []}
    ring_back, ring_front = [], []
    for y in range(cy - r - 4, cy + r + 5):
        for x in range(cx - r - 9, cx + r + 10):
            dx, dy = x - cx + .5, y - cy + .5
            # ring: thin tilted ellipse
            rx_, ry_ = dx * math.cos(-.35) - dy * math.sin(-.35), dx * math.sin(-.35) + dy * math.cos(-.35)
            e = (rx_ / 19) ** 2 + (ry_ / 4.2) ** 2
            inside = dx * dx + dy * dy <= r * r
            if inside:
                band = int((dy + r) / 3.2) % 4
                shade = dx + dy > 7
                col = ["#E08A3C", "#C4682A", "#F2B266", "#C4682A"][band]
                if shade:
                    col = "#8E4420"
                planet[col].append((x, y))
            if 0.72 <= e <= 1.0:
                (ring_front if ry_ > 0 or not inside else ring_back).append((x, y))
    for col, cells in planet.items():
        o.append(cells_path(cells, P, col))
    o.append(cells_path(ring_front, P, "#F5D9A8", 'opacity=".9"'))
    # small moon
    moon = [(x, y) for y in range(5, 13) for x in range(146, 154)
            if (x - 149.5) ** 2 + (y - 8.5) ** 2 <= 11]
    o.append(cells_path(moon, P, "#B9B3C9"))
    o.append(cells_path([(150, 7), (148, 10), (151, 10)], P, "#8A84A0"))

    # passing starfighter
    o.append(f'<g class="fly">{px.sprite(FIGHTER, FIGHTER_PAL, 0, 10 * P, 3)}</g>')

    # far mesas, then near rocks
    def skyline(base, seed, lo, hi, color):
        r_ = random.Random(seed)
        cells, x = [], 0
        while x < GW:
            w = r_.randint(6, 18)
            h = r_.randint(lo, hi)
            for xx in range(x, min(GW, x + w)):
                for yy in range(base - h, base):
                    cells.append((xx, yy))
            x += w
        return cells_path(cells, P, color)
    o.append(skyline(ground, 3, 3, 11, "#2B0E36"))
    o.append(skyline(ground, 8, 1, 5, "#1D0A28"))
    o.append(rect(0, ground * P, W, H - ground * P, "#140820"))
    o.append(rect(0, ground * P, W, P, "#3B1A4A"))
    pebbles = [(rnd.randrange(GW), rnd.randrange(ground + 2, GH)) for _ in range(60)]
    o.append(cells_path(pebbles, P, "#241030"))

    # title
    o.append(px.text(TITLE, 28 + 4, 28 + 4, 6, "#3A2A00"))
    o.append(px.text(TITLE, 28, 28, 6, "#FFE81F"))
    o.append(px.text(SUBTITLE, 30, 84, 2, "#4BD5EE"))

    # duelists
    hx, rx, fy = 82, 117, ground - 20
    L = 16

    def blade(x0, y0, step, color):
        core, edge = [], []
        for i in range(L):
            x, y = x0 + i * step, y0 - i
            core += [(x, y), (x + step, y)]
            edge += [(x - step, y), (x + 2 * step, y)]
        tip = [(x0 + L * step, y0 - L), (x0 + (L + 1) * step, y0 - L)]
        return (f'<g class="hum" filter="url(#glow)">{cells_path(edge + tip, P, color)}'
                f'{cells_path(core, P, "#FFFFFF")}</g>')

    def hilt(cells):
        return cells_path(cells, P, "#9AA4B2") + cells_path(cells[1:2], P, "#1B1F24")

    shadow = [(x, ground) for x in range(hx, hx + 12)] + [(x, ground) for x in range(rx + 2, rx + 14)]
    o.append(cells_path(shadow, P, "#0B0414"))

    o.append('<g class="lunge-l">')
    o.append(px.sprite(DUELIST, HERO_PAL, hx * P, fy * P, P))
    o.append(hilt([(hx + 11, fy + 9), (hx + 12, fy + 8), (hx + 13, fy + 7)]))
    o.append(blade(hx + 14, fy + 6, 1, "#2E9BFF"))
    o.append("</g>")

    o.append('<g class="lunge-r">')
    o.append(px.sprite(px.mirror(DUELIST), RIVAL_PAL, rx * P, fy * P, P))
    o.append(cells_path([(rx + 6, fy + 3), (rx + 4, fy + 3)], P, "#FF2A2A", 'class="eye" filter="url(#glow)"'))
    o.append(hilt([(rx + 2, fy + 9), (rx + 1, fy + 8), (rx, fy + 7)]))
    o.append(blade(rx - 1, fy + 6, -1, "#FF2A2A"))
    o.append("</g>")

    # clash spark where the blades cross
    sx, sy = 106 * P + P, (fy + 6 - 10) * P
    spark = [(0, -3), (0, -2), (0, 2), (0, 3), (-3, 0), (-2, 0), (2, 0), (3, 0),
             (-2, -2), (2, -2), (-2, 2), (2, 2), (0, 0), (1, 0), (0, 1), (1, 1)]
    d = "".join(f"M{sx + x * P}  {sy + y * P}h{P}v{P}h-{P}z" for x, y in spark)
    o.append(f'<path class="spark" d="{d}" fill="#FFF7B0" filter="url(#glow)"/>')

    # helper bot, hovering to the left of the fight
    bx, by = 58, ground - 18
    o.append('<g class="hover">')
    o.append(px.sprite(BOT, BOT_PAL, bx * P, by * P, P))
    o.append(rect((bx + 4) * P, (by - 1) * P, P, P, "#FF2A2A", 'class="blink"'))
    o.append(cells_path([(bx + 3, by + 10), (bx + 4, by + 10), (bx + 5, by + 10), (bx + 6, by + 10),
                         (bx + 4, by + 11), (bx + 5, by + 11)], P, "#FFB000", 'class="flame"'))
    o.append("</g>")

    o.append("</g>")
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="#2E9BFF" stroke-opacity=".35" stroke-width="2"/>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- energy-blade stack
def energy_blades():
    W, ROW, TOP = 900, 44, 72
    H = TOP + ROW * len(STACK) + 26
    blade_x, blade_max = 310, 460
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    o.append("""<style>
.bl{transform-box:fill-box;transform-origin:left center;animation:ig .7s cubic-bezier(.2,.9,.3,1.2) both,hum .14s steps(2) infinite}
@keyframes ig{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
@keyframes hum{0%{opacity:1}100%{opacity:.86}}
.pc{animation:pc .4s steps(1) both}@keyframes pc{0%{opacity:0}100%{opacity:1}}
.tw{animation:tw 3s steps(3) infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:.9}}
</style>""")
    o.append('<defs><filter id="g" x="-10%" y="-200%" width="120%" height="500%">'
             '<feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/>'
             '<feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    o.append(f'<rect width="{W}" height="{H}" rx="14" fill="#000814"/>')
    rnd = random.Random(5)
    for i in range(45):
        o.append(rect(rnd.randrange(0, W, 3), rnd.randrange(0, H, 3), 2, 2, "#FFFFFF",
                      f'class="tw" style="animation-delay:-{rnd.uniform(0, 3):.2f}s"'))
    o.append(px.text("ARSENAL", 30, 26, 3, "#FFE81F"))
    o.append(px.text(":: ENERGY BLADE CALIBRATION", 30 + px.text_width("ARSENAL ", 3), 33, 2, "#4BD5EE"))
    o.append(rect(30, 58, W - 60, 2, "#2E9BFF", 'opacity=".4"'))

    for i, (name, lvl, color) in enumerate(STACK):
        y = TOP + i * ROW + 6
        delay = 0.3 + i * 0.22
        o.append(px.text(name, 30, y + 3, 2, "#C9D1D9"))
        o.append(px.sprite(HILT, HILT_PAL, blade_x - 64, y - 3, 4))
        length = blade_max * lvl / 100
        o.append(f'<g class="bl" style="animation-delay:{delay:.2f}s,0s" filter="url(#g)">'
                 f'<rect x="{blade_x}" y="{y + 1}" width="{length:.0f}" height="12" rx="6" fill="{color}"/>'
                 f'<rect x="{blade_x}" y="{y + 4}" width="{length - 4:.0f}" height="6" rx="3" fill="#FFFFFF"/></g>')
        pct = f"{lvl}%"
        o.append(px.text(pct, W - 30 - px.text_width(pct, 2), y + 3, 2, color,
                         f'class="pc" style="animation-delay:{delay + .5:.2f}s"'))
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="#2E9BFF" stroke-opacity=".35" stroke-width="2"/>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    for name, svg in [("pixel-duel.svg", pixel_duel()), ("energy-blades.svg", energy_blades())]:
        path = os.path.normpath(os.path.join(root, name))
        with open(path, "w") as f:
            f.write(svg)
        print("wrote", path, f"({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
