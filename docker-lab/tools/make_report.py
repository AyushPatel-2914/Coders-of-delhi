"""Builds README.md and Docker_Lab_Report.pdf from tools/results.json."""
import html, json, os, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
steps = json.load(open(os.path.join(REPO, "tools", "results.json")))
NAME, ROLL = "Ayush Patel", "202301084"
INTRO = ("All steps below were performed on a Linux machine (user `ayushpatel`) with "
         "Docker Engine 29.6.2 and Docker Compose v5.3.1. Every screenshot is the real "
         "output of the commands shown above it.")
BROWSER = {10: ("browser_docker_run.png", "Browser view of the custom image running with docker run (port 8082)."),
           15: ("browser_compose.png", "Browser view of the same app deployed with Docker Compose (port 8081).")}
FILES = ["Dockerfile", "docker-compose.yml", "app/index.html"]

# ---------- README.md ----------
md = [f"# Docker Lab Submission\n\n**Name:** {NAME}  \n**Roll No:** {ROLL}\n\n{INTRO}\n",
      "## Project files\n", "| File | Purpose |", "|---|---|",
      "| `Dockerfile` | Recipe to build my custom Nginx image |",
      "| `docker-compose.yml` | Deploys the app with one command (port 8081 + named volume) |",
      "| `app/index.html` | Web page served by the container (shows name and roll number) |",
      "| `screenshots/` | Terminal and browser screenshots for every step |",
      "| `Docker_Lab_Report.pdf` | This report as a PDF for submission |", "",
      "## Steps\n"]
md += [f"{s['id']}. [{s['title']}](#step-{s['id']}-{s['title'].lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '').replace(',', '')})" for s in steps]
for s in steps:
    md.append(f"\n## Step {s['id']}: {s['title']}\n")
    md += ["| Command | Purpose |", "|---|---|"]
    md += [f"| `{r['cmd'].replace('|', '&#124;')}` | {r['explain']} |" for r in s["results"]]
    md.append(f"\n![Step {s['id']} screenshot](screenshots/{s['screenshot']})")
    if s["id"] in BROWSER:
        f, cap = BROWSER[s["id"]]
        md.append(f"\n*{cap}*\n\n![{cap}](screenshots/{f})")
md.append("\n## Conclusion\n\nIn this lab I installed and verified Docker, ran containers from public images, "
          "managed the container lifecycle, wrote a Dockerfile and built my own image, used named volumes "
          "and bind mounts for data, connected containers with a custom network, tagged/saved the image, "
          "and deployed the application with Docker Compose. The browser screenshots confirm the "
          "application ran successfully.\n")
open(os.path.join(REPO, "README.md"), "w").write("\n".join(md))

# ---------- PDF (HTML -> Chromium print) ----------
e = html.escape
h = [f"""<!doctype html><html><head><meta charset="utf-8"><title>Docker Lab - {NAME}</title><style>
body{{font-family:Arial,sans-serif;font-size:12px;color:#222;margin:0}}
.cover{{height:95vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.cover h1{{font-size:36px;color:#0d47a1;margin:0 0 10px}} .cover p{{font-size:18px;margin:4px}}
h2{{color:#0d47a1;border-bottom:2px solid #0d47a1;padding-bottom:4px;margin-top:0}}
.step{{page-break-before:always}} table{{border-collapse:collapse;width:100%;margin-bottom:10px}}
td,th{{border:1px solid #bbb;padding:5px;vertical-align:top;text-align:left}} th{{background:#e3ecfa}}
td code{{font-family:monospace;font-size:11px;word-break:break-all}} td:first-child{{width:45%}}
img{{max-width:100%;border:1px solid #999;margin:6px 0}} pre{{background:#f4f4f4;padding:8px;font-size:11px;border:1px solid #ddd}}
.cap{{font-style:italic;color:#555}}</style></head><body>
<div class="cover"><h1>Docker Lab Submission</h1><p><b>Name:</b> {NAME}</p><p><b>Roll No:</b> {ROLL}</p>
<p style="font-size:14px;max-width:600px;margin-top:30px">{e(INTRO.replace('`',''))}</p></div>
<div class="step"><h2>Project Files</h2>"""]
for f in FILES:
    h.append(f"<h3>{f}</h3><pre>{e(open(os.path.join(REPO, f)).read())}</pre>")
h.append("</div>")
for s in steps:
    h.append(f'<div class="step"><h2>Step {s["id"]}: {e(s["title"])}</h2><table><tr><th>Command</th><th>Purpose</th></tr>')
    h += [f"<tr><td><code>{e(r['cmd'])}</code></td><td>{e(r['explain'])}</td></tr>" for r in s["results"]]
    h.append(f'</table><img src="screenshots/{s["screenshot"]}">')
    if s["id"] in BROWSER:
        f, cap = BROWSER[s["id"]]
        h.append(f'<p class="cap">{e(cap)}</p><img src="screenshots/{f}">')
    h.append("</div>")
h.append(f'<div class="step"><h2>Conclusion</h2><p style="font-size:14px">{md[-1].split(chr(10))[3]}</p></div></body></html>')
tmp = os.path.join(REPO, "report.html")
open(tmp, "w").write("\n".join(h))
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox",
                "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={os.path.join(REPO, 'Docker_Lab_Report.pdf')}", "file://" + tmp],
               capture_output=True)
os.remove(tmp)
print("README.md and Docker_Lab_Report.pdf written")
