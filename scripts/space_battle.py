#!/usr/bin/env python3
"""Space Battle: turns a GitHub contribution graph into an animated SVG.

A small starfighter flies across the graph and its laser blasts every square
that has contributions; the squares then regenerate in a wave and it loops.

Original code written for this profile, released under the MIT License
(see LICENSE). Uses only the Python standard library — no third-party code.

Usage (in GitHub Actions):
    GITHUB_TOKEN=... GH_USER=Deinick python3 scripts/space_battle.py
Local preview without network:
    python3 scripts/space_battle.py --demo
"""
import json
import os
import random
import sys
import urllib.request

CELL, GAP = 11, 3
PAD_X, PAD_TOP, PAD_BOTTOM = 16, 34, 14
DURATION = 14.0          # seconds per loop
SWEEP = 0.62             # fraction of the loop the ship spends crossing

LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]

THEMES = {
    # dark mode: red laser, squares glow from deep blue to star-yellow
    "dark": {
        "bg": "#000814", "cells": ["#161b22", "#1b2a4a", "#2E5BFF", "#7FB2FF", "#FFE81F"],
        "laser": "#FF2A2A", "ship": "#C9D1D9", "accent": "#FF2A2A", "flash": "#FFFFFF",
        "star": "#FFFFFF",
    },
    # light mode: green laser, squares from pale to navy
    "light": {
        "bg": "#FFFFFF", "cells": ["#ebedf0", "#cfe3ff", "#7FB2FF", "#2E9BFF", "#0B3D91"],
        "laser": "#1FBF4A", "ship": "#30363D", "accent": "#1FBF4A", "flash": "#FFE81F",
        "star": "#9AA4B2",
    },
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { contributionLevel weekday } }
      }
    }
  }
}"""


def fetch_weeks(user, token):
    body = json.dumps({"query": QUERY, "variables": {"login": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "space-battle-svg"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[(d["weekday"], LEVELS.index(d["contributionLevel"])) for d in w["contributionDays"]]
            for w in weeks]


def demo_weeks():
    random.seed(7)
    return [[(d, random.choices(range(5), [40, 25, 15, 12, 8])[0]) for d in range(7)]
            for _ in range(53)]


def render(weeks, theme):
    t = THEMES[theme]
    cols = len(weeks)
    w = PAD_X * 2 + cols * (CELL + GAP) - GAP
    grid_h = 7 * (CELL + GAP) - GAP
    h = PAD_TOP + grid_h + PAD_BOTTOM
    grid_x0 = PAD_X
    travel = w + 60  # ship goes from -30 to w+30

    def pct(x):
        return f"{max(0.0, min(100.0, x)):.3f}%"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    css = [
        f".c{{animation:blast {DURATION}s linear infinite}}",
        "@keyframes blast{0%{opacity:1}0.8%{fill:" + t["flash"] + ";opacity:1}3%{opacity:0}68%{opacity:0}72%{opacity:1}100%{opacity:1}}",
        f".ship{{animation:fly {DURATION}s linear infinite}}",
        "@keyframes fly{0%%{transform:translateX(-30px)}%s{transform:translateX(%dpx)}100%%{transform:translateX(%dpx)}}"
        % (pct(SWEEP * 100), travel - 30, travel - 30),
        f".beam{{animation:beam {DURATION}s linear infinite}}",
        "@keyframes beam{0%%{opacity:0}2%%{opacity:.9}%s{opacity:.9}%s{opacity:0}100%%{opacity:0}}"
        % (pct(SWEEP * 100 - 2), pct(SWEEP * 100)),
        ".tw{animation:tw 3s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:.9}}",
    ]
    out.append(f"<style>{''.join(css)}</style>")
    if theme == "dark":
        out.append(f'<rect width="{w}" height="{h}" rx="10" fill="{t["bg"]}"/>')
    # background stars
    rnd = random.Random(42)
    for i in range(40):
        out.append(f'<circle class="tw" style="animation-delay:-{rnd.uniform(0,3):.2f}s" '
                   f'cx="{rnd.uniform(0,w):.1f}" cy="{rnd.uniform(0,h):.1f}" r="{rnd.uniform(.4,1.1):.2f}" fill="{t["star"]}"/>')

    # grid: base (empty) squares, then lit squares on top that get blasted
    for ci, week in enumerate(weeks):
        x = grid_x0 + ci * (CELL + GAP)
        # time the ship's nose reaches this column
        frac = ((x + CELL / 2 + 30) / travel) * SWEEP
        delay = frac * DURATION
        for day, lvl in week:
            y = PAD_TOP + day * (CELL + GAP)
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{t["cells"][0]}"/>')
            if lvl > 0:
                out.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{x}" y="{y}" '
                           f'width="{CELL}" height="{CELL}" rx="2" fill="{t["cells"][lvl]}"/>')

    # the starfighter (an original, simple arrowhead design) + its laser beam
    sy = PAD_TOP - 18
    out.append('<g class="ship">')
    out.append(f'<rect class="beam" x="-1" y="{sy + 8}" width="2" height="{grid_h + 12}" fill="{t["laser"]}"/>')
    out.append(f'<path d="M -12 {sy - 5} L 12 {sy} L -12 {sy + 5} L -7 {sy} Z" fill="{t["ship"]}"/>')
    out.append(f'<path d="M -12 {sy - 5} L -4 {sy - 9} L 0 {sy - 2} Z M -12 {sy + 5} L -4 {sy + 9} L 0 {sy + 2} Z" fill="{t["accent"]}"/>')
    out.append(f'<circle cx="-13" cy="{sy}" r="2" fill="{t["laser"]}" opacity=".8"/>')
    out.append("</g></svg>")
    return "\n".join(out)


def main():
    if "--demo" in sys.argv:
        weeks = demo_weeks()
    else:
        user, token = os.environ.get("GH_USER"), os.environ.get("GITHUB_TOKEN")
        if not user or not token:
            sys.exit("Set GH_USER and GITHUB_TOKEN (or run with --demo).")
        weeks = fetch_weeks(user, token)
    os.makedirs("dist", exist_ok=True)
    for theme in THEMES:
        path = f"dist/space-battle-{theme}.svg"
        with open(path, "w") as f:
            f.write(render(weeks, theme))
        print("wrote", path)


if __name__ == "__main__":
    main()
