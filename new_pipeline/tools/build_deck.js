const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_data.json"), "utf8"));

const C = {
  bg: "FFFFFF",
  ink: "202832",
  mute: "5B6675",
  faint: "D9E1EA",
  faintBg: "F4F7FA",
  blue: "176BFF",
  bluePale: "DFEBFF",
  blueDeep: "0D47B3",
  source: "8792A0",
  white: "FFFFFF",
};
const F_HEAD = "Aptos Display";
const F_BODY = "Aptos";

const PW = 13.333, PH = 7.5;

function headlineSize(text) {
  if (text.length > 70) return 22;
  if (text.length > 50) return 25;
  return 28;
}
function bodySize(text) {
  return text.length > 150 ? 11 : 12.5;
}

function newSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: C.bg };
  return s;
}

function footer(s, sourceName, sourceUrl, page, total) {
  s.addText([{ text: `Source: ${sourceName}`, options: { hyperlink: { url: sourceUrl }, color: C.blue } }], {
    x: 0.55, y: 7.12, w: 6, h: 0.28, fontFace: F_BODY, fontSize: 9.5, color: C.source, margin: 0, isTextBox: true,
  });
  s.addText(`${page}/${total}`, {
    x: 12.2, y: 7.12, w: 0.6, h: 0.28, fontFace: F_BODY, fontSize: 9.5, color: C.source,
    align: "right", margin: 0, isTextBox: true,
  });
}

function categoryHeader(s, number, subcategory) {
  s.addShape("rect", { x: 0.55, y: 0.42, w: 0.06, h: 0.32, fill: { color: C.blue }, line: { type: "none" } });
  s.addText(number, {
    x: 0.72, y: 0.36, w: 0.55, h: 0.32, fontFace: F_HEAD, fontSize: 13, bold: true, color: C.blue,
    margin: 0, isTextBox: true, valign: "top",
  });
  s.addText(subcategory, {
    x: 1.25, y: 0.36, w: 10.9, h: 0.32, fontFace: F_BODY, fontSize: 11.5, bold: true, color: C.mute,
    charSpacing: 1, margin: 0, isTextBox: true, valign: "top",
  });
  s.addShape("line", { x: 0.55, y: 0.86, w: 12.23, h: 0, line: { color: C.faint, width: 1 } });
}

function metricBlock(s, x, y, w, value, label) {
  s.addText(value, { x, y, w, h: 0.5, fontFace: F_HEAD, fontSize: 27, bold: true, color: C.blue, margin: 0, isTextBox: true });
  s.addText(label, { x, y: y + 0.48, w, h: 0.4, fontFace: F_BODY, fontSize: 11, color: C.mute, margin: 0, isTextBox: true });
}

function tagsRow(s, x, y, tags) {
  let cx = x;
  for (const t of tags) {
    const w = 0.22 + t.length * 0.085;
    s.addShape("roundRect", { x: cx, y, w, h: 0.32, rectRadius: 0.06, fill: { color: C.bluePale }, line: { color: C.faint, width: 0.75 } });
    s.addText(t, { x: cx, y, w, h: 0.32, fontFace: F_BODY, fontSize: 10, color: C.blueDeep, align: "center", valign: "middle", margin: 0, isTextBox: true });
    cx += w + 0.14;
  }
}

function imageWithFrame(s, imgPath, x, y, w, h) {
  s.addImage({ path: imgPath, x, y, w, h, sizing: { type: "cover", w, h } });
  s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: C.faint, width: 1 } });
}

function buildTopicSlide(pres, story, total) {
  const s = newSlide(pres);
  categoryHeader(s, story.number, story.subcategory);

  const imageOnRight = story.slot !== "left";
  const textX = imageOnRight ? 0.55 : 6.85;
  const textW = 5.95;
  const imgX = imageOnRight ? 7.05 : 0.55;
  const imgW = 5.72;
  const imgY = 1.12, imgH = 4.62;

  imageWithFrame(s, story.image, imgX, imgY, imgW, imgH);

  // headline
  s.addText(story.headline, {
    x: textX, y: 1.05, w: textW, h: 1.3, fontFace: F_HEAD, fontSize: headlineSize(story.headline),
    bold: true, color: C.ink, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.05,
  });

  // What changed
  const wcY = 2.55;
  s.addText("WHAT CHANGED", {
    x: textX, y: wcY, w: textW, h: 0.3, fontFace: F_BODY, fontSize: 12, bold: true, color: C.blue,
    charSpacing: 0.5, margin: 0, isTextBox: true,
  });
  s.addText(story.what_changed, {
    x: textX, y: wcY + 0.34, w: textW, h: 1.05, fontFace: F_BODY, fontSize: bodySize(story.what_changed),
    color: C.ink, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.18,
  });

  // metrics
  const metY = wcY + 1.55;
  metricBlock(s, textX, metY, 2.1, story.metrics[0][0], story.metrics[0][1]);
  if (story.metrics[1]) {
    s.addShape("line", { x: textX + 2.3, y: metY + 0.04, w: 0, h: 0.9, line: { color: C.faint, width: 1 } });
    metricBlock(s, textX + 2.5, metY, 2.6, story.metrics[1][0], story.metrics[1][1]);
  }

  // enterprise relevance
  const erY = metY + 1.08;
  s.addShape("rect", { x: textX, y: erY, w: 0.05, h: 0.68, fill: { color: C.blue }, line: { type: "none" } });
  s.addText("ENTERPRISE RELEVANCE", {
    x: textX + 0.16, y: erY - 0.02, w: textW - 0.16, h: 0.26, fontFace: F_BODY, fontSize: 11.5, bold: true,
    color: C.blue, charSpacing: 0.5, margin: 0, isTextBox: true,
  });
  s.addText(story.enterprise, {
    x: textX + 0.16, y: erY + 0.26, w: textW - 0.16, h: 0.55, fontFace: F_BODY, fontSize: 10.5,
    color: C.ink, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.12,
  });

  // bottom line / recommendation — distinct from enterprise relevance, never empty
  const blY = erY + 0.92;
  s.addText([
    { text: "Bottom line   ", options: { bold: true, color: C.ink } },
    { text: story.bottom_line, options: { color: C.mute } },
  ], {
    x: textX, y: blY, w: textW, h: 0.5, fontFace: F_BODY, fontSize: 10.5, margin: 0, isTextBox: true,
    valign: "top", lineSpacingMultiple: 1.12,
  });

  // tags under the image
  tagsRow(s, imgX, imgY + imgH + 0.14, story.tags);

  footer(s, story.source_name, story.source_url, story.page, total);
  return s;
}

function buildCover(pres, weekLabel, dateLabel) {
  const s = newSlide(pres);
  s.addText("Top Gen AI", { x: 0.7, y: 1.5, w: 5.6, h: 0.5, fontFace: F_BODY, fontSize: 15, bold: true, color: C.blue, charSpacing: 1, margin: 0, isTextBox: true });
  s.addText(`Top Gen AI\nAdvances: ${weekLabel}`, {
    x: 0.7, y: 2.05, w: 5.6, h: 2.0, fontFace: F_HEAD, fontSize: 42, bold: true, color: C.ink, margin: 0,
    isTextBox: true, lineSpacingMultiple: 1.02,
  });
  s.addText("AI Executive Briefing", { x: 0.7, y: 4.15, w: 5.6, h: 0.4, fontFace: F_BODY, fontSize: 15, color: C.mute, margin: 0, isTextBox: true });
  s.addText(`Generated ${dateLabel}`, { x: 0.7, y: 6.6, w: 5.6, h: 0.3, fontFace: F_BODY, fontSize: 10.5, color: C.source, margin: 0, isTextBox: true });
  s.addText("Prepared for Executive Leadership", { x: 0.7, y: 6.88, w: 5.6, h: 0.3, fontFace: F_BODY, fontSize: 10.5, color: C.source, margin: 0, isTextBox: true });
  imageWithFrame(s, DATA.cover_image, 6.9, 0, 6.433, 7.5);
  return s;
}

function buildDivider(pres, div) {
  const s = newSlide(pres);
  s.addText(div.number, { x: 0.7, y: 2.3, w: 4, h: 1.2, fontFace: F_HEAD, fontSize: 60, bold: true, color: C.bluePale, margin: 0, isTextBox: true });
  s.addText(div.title, { x: 0.7, y: 3.3, w: 6.5, h: 1.0, fontFace: F_HEAD, fontSize: 32, bold: true, color: C.ink, margin: 0, isTextBox: true });
  s.addText(div.subtitle, { x: 0.7, y: 4.15, w: 6.0, h: 0.6, fontFace: F_BODY, fontSize: 14, color: C.mute, margin: 0, isTextBox: true });
  imageWithFrame(s, DATA.divider_image, 7.6, 0, 5.733, 7.5);
  return s;
}

function buildWeeklyOverview(pres) {
  const s = newSlide(pres);
  s.addText("Weekly overview", { x: 0.55, y: 0.5, w: 8, h: 0.6, fontFace: F_HEAD, fontSize: 30, bold: true, color: C.ink, margin: 0, isTextBox: true });
  s.addText(
    "Six developments this week span reasoning, coding agents, inference silicon, robotics, "
    + "clinical AI, and security automation. The throughline: autonomous operation is moving from "
    + "pilot to production faster than governance frameworks are keeping pace.",
    { x: 0.55, y: 1.2, w: 11.3, h: 0.9, fontFace: F_BODY, fontSize: 13, color: C.ink, margin: 0, isTextBox: true, lineSpacingMultiple: 1.25 }
  );
  const stats = DATA.weekly_stats;
  const cardW = 2.75, gap = 0.25, startX = 0.55, y = 2.5, h = 1.6;
  stats.forEach((st, i) => {
    const x = startX + i * (cardW + gap);
    s.addShape("roundRect", { x, y, w: cardW, h, rectRadius: 0.06, fill: { color: C.faintBg }, line: { color: C.faint, width: 1 } });
    s.addText(st[0], { x, y: y + 0.25, w: cardW, h: 0.7, fontFace: F_HEAD, fontSize: 34, bold: true, color: C.blue, align: "center", margin: 0, isTextBox: true });
    s.addText(st[1], { x, y: y + 1.0, w: cardW, h: 0.4, fontFace: F_BODY, fontSize: 11, color: C.mute, align: "center", charSpacing: 0.5, margin: 0, isTextBox: true });
  });
  s.addText("This week's domains", { x: 0.55, y: 4.5, w: 6, h: 0.35, fontFace: F_BODY, fontSize: 12, bold: true, color: C.blue, margin: 0, isTextBox: true });
  const domains = ["Frontier AI", "Developer AI", "AI Hardware", "Robotics", "Healthcare AI", "Cybersecurity"];
  tagsRow(s, 0.55, 4.9, domains);

  s.addShape("line", { x: 0.55, y: 5.55, w: 12.23, h: 0, line: { color: C.faint, width: 1 } });
  s.addText("Reading order", { x: 0.55, y: 5.75, w: 6, h: 0.32, fontFace: F_BODY, fontSize: 12, bold: true, color: C.blue, margin: 0, isTextBox: true });
  const order = DATA.stories.map((st) => `${st.number}  ${st.headline.split(" ").slice(0, 6).join(" ")}…`);
  order.forEach((line, i) => {
    s.addText(line, { x: 0.55, y: 6.08 + i * 0.22, w: 11.3, h: 0.22, fontFace: F_BODY, fontSize: 10, color: C.mute, margin: 0, isTextBox: true });
  });
  return s;
}

function buildSignals(pres) {
  const s = newSlide(pres);
  s.addText("Weekly signals", { x: 0.55, y: 0.5, w: 8, h: 0.6, fontFace: F_HEAD, fontSize: 30, bold: true, color: C.ink, margin: 0, isTextBox: true });
  const items = DATA.signals;
  const rowH = 1.05, startY = 1.4;
  const priorityColor = { HIGH: C.blue, MEDIUM: C.mute, LOW: C.faint };
  items.forEach((it, i) => {
    const y = startY + i * rowH;
    s.addText(it.n, { x: 0.55, y, w: 0.6, h: 0.5, fontFace: F_HEAD, fontSize: 20, bold: true, color: C.bluePale, margin: 0, isTextBox: true });
    s.addText(it.headline, { x: 1.25, y, w: 9.3, h: 0.4, fontFace: F_BODY, fontSize: 14, bold: true, color: C.ink, margin: 0, isTextBox: true, valign: "top" });
    s.addText(it.detail, { x: 1.25, y: y + 0.36, w: 9.3, h: 0.4, fontFace: F_BODY, fontSize: 11, color: C.mute, margin: 0, isTextBox: true, valign: "top" });
    s.addShape("roundRect", { x: 10.9, y: y + 0.05, w: 1.0, h: 0.32, rectRadius: 0.05, fill: { color: it.priority === "HIGH" ? C.bluePale : C.faintBg }, line: { color: C.faint, width: 0.75 } });
    s.addText(it.priority, { x: 10.9, y: y + 0.05, w: 1.0, h: 0.32, fontFace: F_BODY, fontSize: 9, bold: true, color: it.priority === "HIGH" ? C.blueDeep : C.mute, align: "center", valign: "middle", margin: 0, isTextBox: true });
    if (i < items.length - 1) s.addShape("line", { x: 0.55, y: y + rowH - 0.12, w: 11.35, h: 0, line: { color: C.faint, width: 0.75 } });
  });
  return s;
}

function buildLeadership(pres) {
  const s = newSlide(pres);
  s.addText("Leadership brief", { x: 0.55, y: 0.5, w: 8, h: 0.6, fontFace: F_HEAD, fontSize: 30, bold: true, color: C.ink, margin: 0, isTextBox: true });
  s.addText("Three signals worth board-level attention this week.", { x: 0.55, y: 1.05, w: 10, h: 0.35, fontFace: F_BODY, fontSize: 12.5, color: C.mute, margin: 0, isTextBox: true });
  const colW = 3.85, gap = 0.2, startX = 0.55, y = 1.7, h = 5.1;
  const headers = ["SIGNAL", "INTERPRETATION", "ACTION"];
  DATA.leadership.forEach((row, ci) => { // columns are per-insight groups stacked as rows instead for readability
  });
  // Render as 3 rows x 3 labeled columns (Signal / Interpretation / Action) per insight
  const rowH = 1.55;
  DATA.leadership.forEach((row, i) => {
    const ry = 1.7 + i * (rowH + 0.15);
    s.addShape("rect", { x: 0.55, y: ry, w: 0.05, h: rowH, fill: { color: C.blue }, line: { type: "none" } });
    const colWidth = 3.95;
    const cols = [
      { label: "SIGNAL", text: row.signal },
      { label: "INTERPRETATION", text: row.interpretation },
      { label: "ACTION", text: row.action, accent: true },
    ];
    cols.forEach((c, ci) => {
      const cx = 0.85 + ci * (colWidth + 0.1);
      s.addText(c.label, { x: cx, y: ry, w: colWidth, h: 0.25, fontFace: F_BODY, fontSize: 9.5, bold: true, color: C.blue, charSpacing: 0.5, margin: 0, isTextBox: true });
      s.addText(c.text, { x: cx, y: ry + 0.28, w: colWidth, h: rowH - 0.3, fontFace: F_BODY, fontSize: 11, color: c.accent ? C.blueDeep : C.ink, bold: !!c.accent, margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.15 });
    });
    if (i < DATA.leadership.length - 1) s.addShape("line", { x: 0.55, y: ry + rowH + 0.07, w: 12.2, h: 0, line: { color: C.faint, width: 0.75 } });
  });
  return s;
}

function main() {
  const pres = new pptxgen();
  pres.defineLayout({ name: "WIDE", width: PW, height: PH });
  pres.layout = "WIDE";

  buildCover(pres, "CW35, 2026", "26 Aug 2026");
  buildDivider(pres, DATA.dividers[0]);
  const total = DATA.stories.length;
  DATA.stories.forEach((story) => buildTopicSlide(pres, story, total));
  buildWeeklyOverview(pres);
  buildSignals(pres);
  buildLeadership(pres);

  const outPath = path.join(__dirname, "..", "output", "TopGenAI-CW35-2026-redesign.pptx");
  pres.writeFile({ fileName: outPath }).then(() => console.log("wrote", outPath));
}

main();
