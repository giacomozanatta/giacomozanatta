#!/usr/bin/env python3
"""Generate the metro-map career diagram (light and dark SVGs) used in the profile README.

Edit the timeline in build() and run:  python3 career/generate.py
"""
import math
from html import escape
from pathlib import Path

L0, L1, L2 = 40, 72, 104      # x of the three lanes
D = 32                        # height of a 45-degree lane change (equal to lane spacing)
S = 44                        # spacing between consecutive stations on the same lane
GAP = 20                      # distance between a bend and the nearest station
TOP = 64                      # space reserved for the legend
YEAR_X, TITLE_X = 140, 228
WIDTH = 680
STROKE = 7

LINES = {  # key: (legend label, light color, dark color)
    "main": ("Giacomo", "#57606a", "#8b949e"),
    "bs":   ("B.S.", "#0098d4", "#2fb4ea"),
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


def build():
    """Return (tracks, stations, end_y). Tracks are (line, [points]); y grows downwards."""
    tracks, stations = [], []

    def st(x, y, line, year, title, sub="", kind="stop"):
        stations.append(dict(x=x, y=y, line=line, year=year, title=title, sub=sub, kind=kind))

    y = 0
    st(L0, y, "main", "", "Giacomo Zanatta", "Treviso, Italy", kind="interchange")

    y += GAP
    bs = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "bs", "2015–2018", "B.S. Computer Science", "Ca' Foscari University of Venice")
    y += GAP
    bs += [(L1, y), (L0, y + D)]
    tracks.append(("bs", bs))

    y += D + 16
    ms = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "ms", "2018–2023", "M.S. Software Dependability & Cybersecurity",
       "Ca' Foscari University of Venice")
    y += GAP
    ms += [(L1, y), (L2, y + D)]
    alp = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "alp", "2019–2021", "Software Engineer", "Alpenite, Venice")
    y += S
    st(L1, y, "alp", "2021–2023", "Technical Leader", "Alpenite, led a team on luxury e-commerce")
    y += S
    st(L2, y, "ms", "2023", "M.S. thesis: LiSA and ROS", "Static analysis for robotics")
    y += GAP
    alp += [(L1, y), (L0, y + D)]
    ms += [(L2, y), (L0, y + 2 * D)]
    tracks += [("alp", alp), ("ms", ms)]

    y += 2 * D + GAP
    st(L0, y, "main", "2023", "From industry to research", kind="interchange")

    y += GAP
    phd = [(L0, y), (L1, y + D)]
    y += D + GAP
    st(L1, y, "phd", "2023", "PhD in Computer Science", "Ca' Foscari University of Venice")
    y += S
    st(L1, y, "phd", "2024", "Visiting Researcher", "INRIA Antique, ENS Paris")

    for city, year, after in (("New York", "2025", ("2026", "JLiSA ranked 3rd at SV-COMP", "Java track, TACAS 2026")),
                              ("Austin", "2026", None)):
        y += GAP
        aws = [(L1, y), (L2, y + D)]
        y += D + GAP
        st(L2, y, "aws", year, "Applied Scientist Intern", f"Amazon Web Services, {city}")
        y += GAP
        aws += [(L2, y), (L1, y + D)]
        tracks.append(("aws", aws))
        y += D + GAP
        if after:
            st(L1, y, "phd", *after)

    st(L1, y, "phd", "now", "Real-time security firewall for ROS 2", "PhD research", kind="here")
    phd.append((L1, y))
    tracks.append(("phd", phd))
    tracks.insert(0, ("main", [(L0, 0), (L0, y)]))
    return tracks, stations, y


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
    # dashed tails: the lines keep going
    for lane, key in ((L0, "main"), (L1, "phd")):
        out.append(f'<line x1="{lane}" y1="{end}" x2="{lane}" y2="{end + 40}" stroke="{color[key]}" '
                   f'stroke-width="{STROKE}" stroke-linecap="round" stroke-dasharray="0 12"/>')
    # branch tracks first so the main line sits on top of junctions
    for key, pts in sorted(tracks, key=lambda tr: tr[0] == "main"):
        out.append(f'<path d="{rounded_path(pts)}" fill="none" stroke="{color[key]}" '
                   f'stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"/>')

    for s in stations:
        x, y, c = s["x"], s["y"], color[s["line"]]
        if s["kind"] == "interchange":
            out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{t["bg"]}" stroke="{t["text"]}" stroke-width="3"/>')
        elif s["kind"] == "here":
            out.append(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{c}" stroke-width="2">'
                       '<animate attributeName="r" values="7;17" dur="2.2s" repeatCount="indefinite"/>'
                       '<animate attributeName="opacity" values="0.8;0" dur="2.2s" repeatCount="indefinite"/>'
                       '</circle>')
            out.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="{t["bg"]}" stroke-width="2.5"/>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{t["bg"]}" stroke="{c}" stroke-width="3.2"/>')

        ty = y - 1 if s["sub"] else y + 5
        if s["year"]:
            out.append(f'<text x="{YEAR_X}" y="{ty}" font-size="13" font-weight="700" '
                       f'fill="{c if s["kind"] != "interchange" else t["text"]}">{escape(s["year"])}</text>')
        out.append(f'<text x="{TITLE_X}" y="{ty}" font-size="14" font-weight="600" '
                   f'fill="{t["text"]}">{escape(s["title"])}</text>')
        if s["sub"]:
            out.append(f'<text x="{TITLE_X}" y="{y + 15}" font-size="12" fill="{t["muted"]}">{escape(s["sub"])}</text>')
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = Path(__file__).parent
    for theme in THEMES:
        (here / f"career-{theme}.svg").write_text(render(theme))
        print(f"wrote {here / f'career-{theme}.svg'}")
