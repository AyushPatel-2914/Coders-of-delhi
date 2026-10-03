// Builds Docker_Lab_Report.docx (plain black & white) from tools/results.json
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
        BorderStyle, HeadingLevel, AlignmentType, PageBreak } = require("docx");
const REPO = path.join(__dirname, "..");
const steps = JSON.parse(fs.readFileSync(path.join(REPO, "tools", "results.json")));
const NAME = "Ayush Patel", ROLL = "202301084";
const FONT = "Times New Roman", MONO = "Courier New";
const PAGE_W = 9026;              // A4 width minus 1" margins (DXA)
const COLS = [4300, 4726];
const IMG_W = 600;                // px, fits the text width

const pngSize = f => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
const image = f => {
  const p = path.join(REPO, "screenshots", f), [w, h] = pngSize(p);
  return new Paragraph({ spacing: { before: 120, after: 120 }, children: [new ImageRun({
    type: "png", data: fs.readFileSync(p), transformation: { width: IMG_W, height: Math.round(h * IMG_W / w) },
    altText: { title: f, description: f, name: f } })] });
};
const text = (t, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o.p, children: [new TextRun({ text: t, ...o.r })] });
const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };
const cell = (children, w) => new TableCell({ borders, width: { size: w, type: WidthType.DXA },
  margins: { top: 60, bottom: 60, left: 100, right: 100 }, children });
const cmdTable = rs => new Table({ width: { size: PAGE_W, type: WidthType.DXA }, columnWidths: COLS, rows: [
  new TableRow({ tableHeader: true, children: [cell([text("Command", { r: { bold: true } })], COLS[0]),
                                               cell([text("Purpose", { r: { bold: true } })], COLS[1])] }),
  ...rs.map(r => new TableRow({ children: [
    cell([new Paragraph({ children: [new TextRun({ text: r.cmd, font: MONO, size: 18 })] })], COLS[0]),
    cell([new Paragraph({ children: [new TextRun({ text: r.explain })] })], COLS[1])] }))] });
const codeBlock = f => fs.readFileSync(path.join(REPO, f), "utf8").replace(/\n$/, "").split("\n").map(l =>
  new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: l || " ", font: MONO, size: 18 })] }));

const BROWSER = { 10: ["browser_docker_run.png", "Browser view of the custom image running with docker run (port 8082)."],
                  15: ["browser_compose.png", "Browser view of the same app deployed with Docker Compose (port 8081)."] };

const body = [
  new Paragraph({ spacing: { before: 3600 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Docker Lab Submission", bold: true, size: 48 })] }),
  text(`Name: ${NAME}`, { p: { alignment: AlignmentType.CENTER }, r: { size: 28 } }),
  text(`Roll No: ${ROLL}`, { p: { alignment: AlignmentType.CENTER }, r: { size: 28 } }),
  text("All steps were performed on a Linux machine (user ayushpatel) with Docker Engine 29.6.2 and Docker Compose v5.3.1. Every screenshot is the real output of the commands listed above it.",
       { p: { alignment: AlignmentType.CENTER, spacing: { before: 600 } } }),
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Project Files")] }),
];
for (const f of ["Dockerfile", "docker-compose.yml", "app/index.html"]) {
  body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(f)] }), ...codeBlock(f));
}
for (const s of steps) {
  body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun(`Step ${s.id}: ${s.title}`)] }),
            cmdTable(s.results), image(s.screenshot));
  if (BROWSER[s.id]) body.push(text(BROWSER[s.id][1], { r: { italics: true } }), image(BROWSER[s.id][0]));
}
body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun("Conclusion")] }),
  text("In this lab I installed and verified Docker, ran containers from public images, managed the container lifecycle, wrote a Dockerfile and built my own image, used named volumes and bind mounts for data, connected containers with a custom network, tagged/saved the image, and deployed the application with Docker Compose. The browser screenshots confirm the application ran successfully."));

const hs = size => ({ run: { font: FONT, size, bold: true, color: "000000" }, paragraph: { spacing: { before: 240, after: 160 } } });
const doc = new Document({
  creator: NAME, title: `Docker Lab - ${NAME} (${ROLL})`,
  styles: { default: { document: { run: { font: FONT, size: 24, color: "000000" } },
                       heading1: hs(32), heading2: hs(26) } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 },
                 margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: body }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(REPO, "Docker_Lab_Report.docx"), b); console.log("docx written"); });
