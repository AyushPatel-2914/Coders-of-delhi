"""Adds a simple browser address bar above a raw page screenshot."""
import sys
from PIL import Image, ImageDraw, ImageFont
raw, url, out = sys.argv[1:4]
page = Image.open(raw); W, H = page.size
img = Image.new("RGB", (W, H + 52), "#ffffff"); d = ImageDraw.Draw(img)
d.rounded_rectangle([10, 10, W - 10, 42], radius=4, fill="#ffffff", outline="#000000", width=1)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
d.text((22, 16), url, font=f, fill="#000000")
img.paste(page, (0, 52))
d.rectangle([0, 0, W - 1, H + 51], outline="#000000"); img.save(out)
