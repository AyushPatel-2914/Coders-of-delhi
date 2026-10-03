"""Runs every Docker lab step as user 'ayushpatel', records real output,
and renders each step as a terminal-style screenshot (PNG)."""
import time, json, os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(REPO, "screenshots")
WORK = "/home/ayushpatel/docker-lab"
USER, HOST = "ayushpatel", "docker-lab"
MAX_LINES = 44          # long outputs are trimmed (clearly marked)
WRAP = 140

F = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
font, bold = ImageFont.truetype(F, 15), ImageFont.truetype(FB, 15)

STEPS = json.load(open(os.path.join(REPO, "tools", "steps.json")))

def run(cmd):
    r = subprocess.run(["su", "-", USER, "-c", f"cd {WORK} && {cmd}"],
                       capture_output=True, text=True, timeout=600)
    return (r.stdout + r.stderr).rstrip("\n")

def trim(out):
    lines = []
    for l in out.splitlines():
        lines += textwrap.wrap(l, WRAP, drop_whitespace=False) or [""]
    if len(lines) > MAX_LINES:
        keep = MAX_LINES // 2
        lines = lines[:keep] + [f"   ... ({len(lines) - 2*keep} lines trimmed) ..."] + lines[-keep:]
    return lines

def render(step, results, path):
    rows = []  # (kind, text)
    for cmd, out in results:
        parts = textwrap.wrap(cmd, WRAP - 26, break_on_hyphens=False) or [""]
        rows.append(("cmd", parts[0] + (" \\" if len(parts) > 1 else "")))
        rows += [("cont", "> " + p + (" \\" if i < len(parts) - 2 else ""))
                 for i, p in enumerate(parts[1:])]
        rows += [("out", l) for l in trim(out)] if out else []
    rows.append(("cmd", ""))
    lh, pad, bar = 20, 16, 34
    W = 1310
    H = bar + pad * 2 + lh * len(rows)
    img = Image.new("RGB", (W, H), "#000000")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, bar], fill="#ffffff", outline="#000000")
    title = f"{USER}@{HOST}: ~/docker-lab   —   Step {step['id']}: {step['title']}"
    d.text((14, 9), title, font=font, fill="#000000")
    y = bar + pad
    for kind, text in rows:
        x = pad
        if kind == "cmd":
            for seg, col in [(f"{USER}@{HOST}:~/docker-lab$ ", "#ffffff")]:
                d.text((x, y), seg, font=bold, fill=col); x += d.textlength(seg, font=bold)
            d.text((x, y), text, font=font, fill="#ffffff")
        elif kind == "cont":
            d.text((x, y), text, font=font, fill="#ffffff")
        else:
            d.text((x, y), text, font=font, fill="#ffffff")
        y += lh
    img.save(path)

import sys
if "--render-only" in sys.argv:
    for st in json.load(open(os.path.join(REPO, "tools", "results.json"))):
        render(st, [(r["cmd"], r["out"]) for r in st["results"]], os.path.join(SHOTS, st["screenshot"]))
    sys.exit()

record = []
for step in STEPS:
    results = []
    for c in step["cmds"]:
        results.append((c[0], run(c[0]))); time.sleep(2)
    name = f"step{step['id']:02d}.png"
    render(step, results, os.path.join(SHOTS, name))
    record.append({**step, "screenshot": name,
                   "results": [{"cmd": c[0], "explain": c[1], "out": o} for c, (_, o) in zip(step["cmds"], results)]})
    print("done step", step["id"], step["title"])
json.dump(record, open(os.path.join(REPO, "tools", "results.json"), "w"), indent=1)
