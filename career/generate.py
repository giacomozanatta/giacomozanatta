#!/usr/bin/env python3
"""Generate the metro-map career diagram (light and dark SVGs) used in the profile README.

Edit the timeline in build() and run:  python3 career/generate.py
"""
import math
from html import escape
from pathlib import Path

L0, L1, L2 = 40, 72, 104      # x of the three lanes
D = 32                        # height of a 45-degree lane change (equal to lane spacing)
S = 54                        # spacing between consecutive stations on the same lane
GAP = 22                      # distance between a bend and the nearest station
TOP = 64                      # space reserved for the legend
YEAR_X, TITLE_X = 140, 240
WIDTH = 680
STROKE = 7

LINES = {  # key: (legend label, light color, dark color)
    "main": ("Giacomo", "#1e3a8a", "#5b8def"),
    "bs":   ("B.S.", "#d6457e", "#f06fa3"),
    "ms":   ("M.S.", "#00a650", "#2ec46f"),
    "alp":  ("Alpenite", "#e32017", "#f5534b"),
    "phd":  ("PhD", "#7b3f98", "#b07ad6"),
    "aws":  ("AWS", "#ff9900", "#ff9900"),
}

THEMES = {
    "light": {"bg": "#ffffff", "text": "#1f2328", "muted": "#59636e", "idx": 1},
    "dark":  {"bg": "#0d1117", "text": "#e6edf3", "muted": "#9198a1", "idx": 2},
}

FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
TAG_SIZE, TAG_CHAR = 11, 6.8  # monospace glyphs are ~0.6em wide, so tag widths are predictable


def blend(fg, bg, alpha):
    """Mix two #rrggbb colors; used instead of opacity so every SVG renderer shows the same tint."""
    mix = (round(int(fg[i:i + 2], 16) * alpha + int(bg[i:i + 2], 16) * (1 - alpha)) for i in (1, 3, 5))
    return "#" + "".join(f"{v:02x}" for v in mix)


def build():
    """Return (tracks, stations, end_y). Tracks are (line, [points]); y grows downwards."""
    tracks, stations = [], []

    def st(x, y, line, year, title, org="", sub="", tags=(), kind="stop"):
        stations.append(dict(x=x, y=y, line=line, year=year, title=title, org=org,
                             sub=sub, tags=tags, kind=kind))

    y = 0
    st(L0, y, "main", "", "Giacomo Zanatta", kind="origin")

    y += GAP
    bs = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "bs", "2015–2018", "B.S. Information Science and Technology", "Ca' Foscari")
    y += GAP
    bs += [(L1, y), (L0, y + D)]
    tracks.append(("bs", bs))

    y += D + 16
    ms = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "ms", "2018–2023", "M.S. Computer Science", "Ca' Foscari",
       sub="Software Dependability and Cybersecurity")
    y += GAP + 8
    ms += [(L1, y), (L2, y + D)]
    alp = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "alp", "2019–2021", "Software Consultant & Software Engineer", "Alpenite",
       tags=("Node.js", "SFCC", "APEX", "Python", "JavaScript", "CI/CD", "Jira"))
    y += S
    st(L1, y, "alp", "2021–2023", "Technical Leader", "Alpenite",
       tags=("Golang", "Heroku", "microservices"))
    y += GAP + 12
    alp += [(L1, y), (L0, y + D)]
    ms += [(L2, y), (L0, y + 2 * D)]
    tracks += [("alp", alp), ("ms", ms)]

    y += 2 * D + 16
    phd = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "phd", "2023–2027", "PhD in Computer Science", "Ca' Foscari",
       tags=("software correctness", "static analysis", "Java", "Python"))
    y += GAP + 12

    for city, year, tags in (("New York", "2025", ("Java", "Python")),
                             ("Austin", "2026", ("Java", "Python", "Lean"))):
        aws = [(L1, y), (L2, y + D)]
        y += D + GAP
        st(L2, y, "aws", year, "Applied Scientist Intern", f"AWS {city}", tags=tags)
        y += GAP + 12
        aws += [(L2, y), (L1, y + D)]
        tracks.append(("aws", aws))
        y += D + 16

    end = y
    phd.append((L1, end))
    tracks.append(("phd", phd))
    tracks.insert(0, ("main", [(L0, 0), (L0, end)]))
    return tracks, stations, end


def rounded_path(points, r=10):
    """SVG path through points with rounded corners of radius r."""
    d = [f"M{points[0][0]},{points[0][1]}"]
    for (ax, ay), (bx, by), (cx, cy) in zip(points, points[1:], points[2:]):
        l1, l2 = math.dist((ax, ay), (bx, by)), math.dist((bx, by), (cx, cy))
        p = (bx - (bx - ax) * r / l1, by - (by - ay) * r / l1)
        q = (bx + (cx - bx) * r / l2, by + (cy - by) * r / l2)
        d.append(f"L{p[0]:.1f},{p[1]:.1f} Q{bx},{by} {q[0]:.1f},{q[1]:.1f}")
    d.append(f"L{points[-1][0]},{points[-1][1]}")
    return " ".join(d)


def render(theme):
    t = THEMES[theme]
    color = {k: v[t["idx"]] for k, v in LINES.items()}
    tracks, stations, end = build()
    height = TOP + end + 56
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
           f'viewBox="0 0 {WIDTH} {height}" font-family=\'{FONT}\' role="img">',
           "<title>Career map of Giacomo Zanatta</title>"]

    # legend
    x = 16
    for key, (label, *_) in LINES.items():
        out.append(f'<line x1="{x}" y1="20" x2="{x + 22}" y2="20" stroke="{color[key]}" '
                   f'stroke-width="{STROKE}" stroke-linecap="round"/>')
        out.append(f'<text x="{x + 32}" y="25" font-size="13" fill="{t["muted"]}">{label}</text>')
        x += 104

    out.append(f'<g transform="translate(0,{TOP})">')
    # dotted tails: the lines keep going
    for lane, key in ((L0, "main"), (L1, "phd")):
        out.append(f'<line x1="{lane}" y1="{end}" x2="{lane}" y2="{end + 40}" stroke="{color[key]}" '
                   f'stroke-width="{STROKE}" stroke-linecap="round" stroke-dasharray="0 12"/>')
    # branch tracks first so the main line sits on top of junctions
    for key, pts in sorted(tracks, key=lambda tr: tr[0] == "main"):
        out.append(f'<path d="{rounded_path(pts)}" fill="none" stroke="{color[key]}" '
                   f'stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"/>')

    for s in stations:
        x, y, c = s["x"], s["y"], color[s["line"]]
        if s["kind"] == "origin":
            out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{t["bg"]}" stroke="{c}" stroke-width="4"/>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{t["bg"]}" stroke="{c}" stroke-width="3.2"/>')

        # left column: year with the organization below it; right column: title with sub or tags below
        ty = y - 3 if s["year"] else y + 5
        if s["year"]:
            out.append(f'<text x="{YEAR_X}" y="{ty}" font-size="13" font-weight="700" fill="{c}">'
                       f'{escape(s["year"])}</text>')
            out.append(f'<text x="{YEAR_X}" y="{y + 15}" font-size="12" fill="{t["muted"]}">'
                       f'{escape(s["org"])}</text>')
        out.append(f'<text x="{TITLE_X}" y="{ty}" font-size="14" font-weight="600" '
                   f'fill="{t["text"]}">{escape(s["title"])}</text>')
        if s["sub"]:
            out.append(f'<text x="{TITLE_X}" y="{y + 15}" font-size="12" fill="{t["muted"]}">'
                       f'{escape(s["sub"])}</text>')
        tx = TITLE_X
        for tag in s["tags"]:
            w = len(tag) * TAG_CHAR + 14
            out.append(f'<rect x="{tx}" y="{y + 5}" width="{w:.0f}" height="18" rx="4" '
                       f'fill="{blend(c, t["bg"], 0.14)}" stroke="{blend(c, t["bg"], 0.5)}"/>')
            out.append(f'<text x="{tx + 7}" y="{y + 18}" font-family=\'{MONO}\' font-size="{TAG_SIZE}" '
                       f'fill="{t["text"]}">{escape(tag)}</text>')
            tx += w + 6
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = Path(__file__).parent
    for theme in THEMES:
        (here / f"career-{theme}.svg").write_text(render(theme))
        print(f"wrote {here / f'career-{theme}.svg'}")
