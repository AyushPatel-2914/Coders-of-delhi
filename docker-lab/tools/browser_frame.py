"""Adds a simple browser address bar above a raw page screenshot."""
import sys
from PIL import Image, ImageDraw, ImageFont
raw, url, out = sys.argv[1:4]
page = Image.open(raw); W, H = page.size
img = Image.new("RGB", (W, H + 52), "#dee1e6"); d = ImageDraw.Draw(img)
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    d.ellipse([14 + i*22, 20, 26 + i*22, 32], fill=c)
d.rounded_rectangle([90, 10, W - 20, 42], radius=16, fill="#ffffff")
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
d.text((110, 16), url, font=f, fill="#202124")
img.paste(page, (0, 52)); img.save(out)
