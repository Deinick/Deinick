#!/usr/bin/env python3
"""Holo-terminal stats card: your GitHub stats as an animated hologram SVG.

Shows contributions, streaks, PRs, stars, a segmented month-by-month
"hyperspace jumps" bar chart and a power-cell bar of your top languages.

Original code (MIT License), standard library only.

    GITHUB_TOKEN=... GH_USER=Deinick python3 scripts/holo_stats.py
    python3 scripts/holo_stats.py --demo        # offline preview
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

import pixel as px

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}"""

CYAN, YELLOW, BLUE, RED, DIM = "#4BD5EE", "#FFE81F", "#2E9BFF", "#FF2A2A", "#5C8DA8"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def fetch(user, token):
    body = json.dumps({"query": QUERY, "variables": {"login": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "holo-stats-svg"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    u = data["data"]["user"]
    cc = u["contributionsCollection"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            size, _ = langs.get(name, (0, None))
            langs[name] = (size + e["size"], e["node"]["color"] or "#8B949E")
    return {
        "login": u["login"],
        "days": days,
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "repos": u["repositories"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "langs": langs,
    }


def demo():
    rnd = random.Random(3)
    today = dt.date.today()
    days = [(today - dt.timedelta(days=i), rnd.choices([0, 1, 2, 4, 7, 12], [30, 20, 18, 15, 10, 7])[0])
            for i in range(364, -1, -1)]
    return {"login": "Deinick", "days": days, "total": sum(c for _, c in days), "commits": 812,
            "prs": 46, "issues": 19, "stars": 37, "repos": 24, "followers": 15,
            "langs": {"JavaScript": (420, "#f1e05a"), "TypeScript": (300, "#3178c6"),
                      "Python": (210, "#3572A5"), "CSS": (90, "#663399"), "HTML": (60, "#e34c26"),
                      "Shell": (20, "#89e051")}}


def streaks(days):
    days = sorted(days)
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    seq = [c for _, c in days]
    if seq and seq[-1] == 0:   # today not counted yet; streak may still be alive
        seq = seq[:-1]
    for c in reversed(seq):
        if not c:
            break
        current += 1
    return current, longest


def monthly(days):
    last = max(d for d, _ in days)
    keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    keys.reverse()
    totals = {k: 0 for k in keys}
    for d, c in days:
        if (d.year, d.month) in totals:
            totals[(d.year, d.month)] += c
    return [(MONTHS[m - 1], totals[(y, m)]) for y, m in keys]


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def render(s):
    W, H = 900, 360
    cur, longest = streaks(s["days"])
    months = monthly(s["days"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']
    o.append("""<style>
.holo{animation:fl 6s steps(1) infinite}
@keyframes fl{0%,40%,44%,100%{opacity:1}41%{opacity:.55}42%{opacity:.9}43%{opacity:.4}}
.scan{animation:sc 4s linear infinite}@keyframes sc{0%{transform:translateY(-40px)}100%{transform:translateY(400px)}}
.bar{transform-box:fill-box;transform-origin:bottom;animation:gr .9s steps(8) both}
@keyframes gr{0%{transform:scaleY(0)}100%{transform:scaleY(1)}}
.cell{animation:on .3s steps(1) both}@keyframes on{0%{opacity:0}100%{opacity:1}}
.cur{animation:cu 1s steps(1) infinite}@keyframes cu{0%,50%{opacity:1}51%,100%{opacity:0}}
.ping{transform-box:fill-box;transform-origin:center;animation:pg 2.4s ease-out infinite}
@keyframes pg{0%{transform:scale(.2);opacity:.9}100%{transform:scale(2.4);opacity:0}}
</style>""")
    o.append('<defs>'
             '<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
             f'<rect width="4" height="1" fill="{CYAN}" opacity=".07"/></pattern>'
             '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#03142A"/><stop offset="1" stop-color="#000814"/></linearGradient>'
             '<linearGradient id="sb" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{CYAN}" stop-opacity=".18"/></linearGradient>'
             '<filter id="gl" x="-5%" y="-5%" width="110%" height="110%">'
             '<feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/>'
             '<feMergeNode in="SourceGraphic"/></feMerge></filter>'
             f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>')
    o.append(f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="url(#bg)"/>')
    o.append('<g class="holo" filter="url(#gl)">')

    # header with a radar "ping" and blinking cursor
    o.append(f'<circle cx="44" cy="38" r="9" fill="none" stroke="{CYAN}" stroke-width="2" shape-rendering="auto"/>')
    o.append(f'<circle class="ping" cx="44" cy="38" r="9" fill="none" stroke="{CYAN}" stroke-width="2" shape-rendering="auto"/>')
    o.append(rect(42, 36, 4, 4, YELLOW))
    o.append(px.text("HOLO-TERMINAL", 66, 28, 3, CYAN))
    head2 = f"// PILOT RECORD: {s['login'].upper()}"
    x2 = 66 + px.text_width("HOLO-TERMINAL ", 3)
    o.append(px.text(head2, x2, 35, 2, DIM))
    o.append(rect(x2 + px.text_width(head2 + " ", 2), 35, 10, 14, CYAN, 'class="cur"'))
    o.append(rect(30, 66, W - 60, 2, CYAN, 'opacity=".35"'))

    # left: stat readout
    rows = [
        ("CONTRIBUTIONS 1Y", s["total"], YELLOW),
        ("CURRENT STREAK", f"{cur}D", RED if cur == 0 else YELLOW),
        ("LONGEST STREAK", f"{longest}D", YELLOW),
        ("COMMITS", s["commits"], CYAN),
        ("PULL REQUESTS", s["prs"], CYAN),
        ("STARS EARNED", s["stars"], CYAN),
        ("REPOSITORIES", s["repos"], CYAN),
    ]
    lx, rx_, y0 = 34, 330, 86
    for i, (label, val, col) in enumerate(rows):
        y = y0 + i * 26
        o.append(f'<g class="cell" style="animation-delay:{.15 + i * .12:.2f}s">')
        o.append(px.text(label, lx, y, 2, DIM))
        v = str(val)
        o.append(px.text(v, rx_ - px.text_width(v, 2), y, 2, col))
        dots_x = lx + px.text_width(label + " ", 2)
        dots_end = rx_ - px.text_width(v + " ", 2)
        for dx in range(int(dots_x), int(dots_end), 8):
            o.append(rect(dx, y + 12, 2, 2, DIM, 'opacity=".5"'))
        o.append("</g>")

    # divider
    o.append(rect(362, 82, 2, 182, CYAN, 'opacity=".25"'))

    # right: monthly bar chart, segmented like an old targeting display
    cx0, cy_base, ch = 384, 246, 126
    o.append(px.text("HYPERSPACE JUMPS / MONTH", cx0, 82, 2, CYAN))
    peak = max((v for _, v in months), default=0) or 1
    bw, gap, seg = 28, 12, 7
    for gy in range(0, ch + 1, 35):  # grid lines
        o.append(rect(cx0, cy_base - gy, 12 * (bw + gap) - gap, 1, CYAN, 'opacity=".12"'))
    for i, (mname, val) in enumerate(months):
        x = cx0 + i * (bw + gap)
        nseg = round(val / peak * (ch // seg)) if val else 0
        o.append(f'<g class="bar" style="animation-delay:{.4 + i * .07:.2f}s">')
        for k in range(nseg):
            top = k == nseg - 1
            col = YELLOW if top and val == peak else (CYAN if k < nseg * .7 else BLUE)
            if top and val != peak:
                col = "#9FEAF7"
            o.append(rect(x, cy_base - (k + 1) * seg + 1, bw, seg - 2, col))
        o.append("</g>")
        o.append(px.text(mname, x + bw / 2 - px.text_width(mname, 1) / 2 * 1, cy_base + 8, 1, DIM))
        if val == peak:
            v = str(val)
            o.append(px.text(v, x + bw / 2 - px.text_width(v, 1) / 2, cy_base - nseg * seg - 12, 1, YELLOW))

    # bottom: language power cells
    by = 290
    o.append(px.text("POWER CELLS", 34, by - 2, 2, CYAN))
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1][0])[:6]
    tot = sum(v[0] for _, v in langs) or 1
    cells, cw = 56, 9
    bx = 34 + px.text_width("POWER CELLS  ", 2)
    idx = 0
    alloc = []
    for name, (size, color) in langs:
        n = max(1, round(size / tot * cells))
        alloc.append((name, color, n, size / tot))
    over = sum(a[2] for a in alloc) - cells
    if over and alloc:
        name, color, n, share = alloc[0]
        alloc[0] = (name, color, max(1, n - over), share)
    for name, color, n, _ in alloc:
        for _ in range(n):
            o.append(rect(bx + idx * (cw + 2), by - 4, cw, 18, color,
                          f'class="cell" style="animation-delay:{1.2 + idx * .02:.2f}s"'))
            idx += 1
    lx = 34
    for name, color, _, share in alloc:
        label = f"{name.upper()} {share * 100:.0f}%"
        o.append(rect(lx, by + 30, 8, 8, color))
        o.append(px.text(label, lx + 14, by + 31, 1, "#C9D1D9"))
        lx += 14 + px.text_width(label, 1) + 22

    o.append("</g>")  # .holo
    o.append(f'<rect width="{W}" height="{H}" fill="url(#sl)"/>')
    o.append(f'<rect class="scan" width="{W}" height="40" fill="url(#sb)"/>')
    o.append("</g>")
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="{CYAN}" stroke-opacity=".45" stroke-width="2"/>')
    # corner brackets
    for (x, y, dx, dy) in [(14, 14, 1, 1), (W - 14, 14, -1, 1), (14, H - 14, 1, -1), (W - 14, H - 14, -1, -1)]:
        o.append(f'<path d="M{x} {y + 18 * dy}V{y}H{x + 18 * dx}" fill="none" stroke="{YELLOW}" stroke-width="3"/>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    if "--demo" in sys.argv:
        stats = demo()
    else:
        user, token = os.environ.get("GH_USER"), os.environ.get("GITHUB_TOKEN")
        if not user or not token:
            sys.exit("Set GH_USER and GITHUB_TOKEN (or run with --demo).")
        stats = fetch(user, token)
    os.makedirs("dist", exist_ok=True)
    with open("dist/holo-stats.svg", "w") as f:
        f.write(render(stats))
    print("wrote dist/holo-stats.svg")


if __name__ == "__main__":
    main()
