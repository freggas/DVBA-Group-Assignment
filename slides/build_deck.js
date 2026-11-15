// Build the board deck from the analysis output, so every number on a slide comes from src/analysis.py.
//
// Run:  .venv/bin/python src/analysis.py && node slides/build_deck.js
// In:   dashboard/data.js (window.DATA, written by src/analysis.py)
// Out:  slides/DVBA2026_Team14_Presentation.pptx  (upload to Google Drive → open with Google Slides)
//
// Edits made in PowerPoint / Google Slides are overwritten on the next build: change the text here.
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const pptxgen = require("pptxgenjs");

// data.js assigns window.DATA; run it in a sandbox (a global `window` makes pptxgenjs think it runs in a browser)
const ctx = { window: {} };
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname, "../dashboard/data.js"), "utf8"), ctx);
const D = ctx.window.DATA, K = D.kpi, DR = D.drivers;
const OUT = path.resolve(__dirname, "DVBA2026_Team14_Presentation.pptx");

// ---------- theme ----------
const HEX = { navy: "0A1C3F", ink2: "4A5468", ink3: "7A8396", blue: "1748C9", orange: "E2621B", grey: "8B94A5",
              track: "EEF1F6", line: "E3E6EC", ice: "8FB0FF", mist: "C9D3E8", navy2: "13295A", white: "FFFFFF" };
const THEME = {
  name: "World Cup Value Report", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: HEX.navy, lt1: HEX.white, dk2: HEX.ink2, lt2: HEX.track, accent1: HEX.blue, accent2: HEX.orange,
            accent3: HEX.grey, accent4: HEX.navy2, accent5: HEX.ice, accent6: HEX.mist, hlink: HEX.blue, folHlink: HEX.navy2 },
};

// ---------- numbers (same definitions as story/index.html) ----------
const STAGE = ["Group stage", "Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final", "Champion"];
const STAGE_SHORT = ["Group", "R32", "R16", "QF", "SF", "Final", "Champion"];
const pct = (a, b) => Math.round(100 * a / b);
const p100 = v => `${Math.round(v * 100)}%`;
const signed = (v, dp = 0) => (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(dp);
const list = a => a.length > 1 ? `${a.slice(0, -1).join(", ")} and ${a.at(-1)}` : a.join("");
const fmtM = v => v >= 1000 ? `€${+(v / 1000).toFixed(2)}bn` : `€${Math.round(v)}m`;

const T = D.teams;
const under500 = T.filter(t => t.market_value_m < 500), over500 = T.filter(t => t.market_value_m >= 500);
const pastR32 = a => a.filter(t => t.stage_reached >= 3).length;
const top8Out = T.filter(t => t.value_rank <= 8 && t.stage_reached < 4).map(t => t.team);
const TOPK = [[32, 2], [16, 3], [8, 4], [4, 5], [2, 6], [1, 7]].map(([k, s]) => {
  const top = T.filter(t => t.value_rank <= k);
  return { k, s, n: top.filter(t => t.stage_reached >= s).length, missed: top.filter(t => t.stage_reached < s) };
});
const R = Object.fromEntries(D.rounds.map(r => [r.stage, r]));
const KO = ["Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final"];
const hosts = T.filter(t => t.host_nation === "Yes");
const confRows = [...DR.conf].sort((a, b) => b.mean - a.mean);
const caf = DR.conf.find(c => c.confederation === "CAF"), uefa = DR.conf.find(c => c.confederation === "UEFA");
const cafTeams = T.filter(t => t.confederation === "CAF"), uefaMinus2 = T.filter(t => t.confederation === "UEFA" && t.stage_vs_expected === -2);
const at = (key, v) => D.odds[key].at[String(v)];
const G = D.curve_grid;
const nearest = v => G.reduce((bi, g, i) => Math.abs(Math.log(g / v)) < Math.abs(Math.log(G[bi] / v)) ? i : bi, 0);
const i500 = nearest(500), ci = D.curves_ci.r16;
const peers = under500.filter(t => t.stage_reached >= 3).sort((a, b) => b.stage_reached - a.stage_reached);
const UV = DR.undervalued;

// ---------- deck & layouts ----------
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "World Cup 2026: squad value and progression";
pres.author = "DVBA 2026 Team 14";
const C = pres.SchemeColor;
const W = 13.333, M = 0.6;
const FOOT = "World Cup 2026 Value Report · DVBA 2026 Team 14 · independent student analysis, not affiliated with FIFA";

pres.defineSlideMaster({
  title: "Title", background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: M + 0.2, y: 1.6, w: 8.2, h: 0.4, fontSize: 13, bold: true, color: C.accent1, charSpacing: 2, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M + 0.2, y: 2.1, w: 8.2, h: 2.6, fontSize: 46, bold: true, color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M + 0.2, y: 4.85, w: 7.8, h: 1.0, fontSize: 20, color: C.text2, valign: "top", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: M + 0.2, y: 6.75, w: 11.5, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
  ],
});
pres.defineSlideMaster({
  title: "Section dark", background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: M + 0.2, y: 2.3, w: 6, h: 0.5, fontSize: 18, bold: true, color: C.accent5, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M + 0.2, y: 2.85, w: 11.5, h: 1.8, fontSize: 40, bold: true, color: C.background1, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M + 0.2, y: 4.75, w: 10.5, h: 1.0, fontSize: 20, color: C.accent6, valign: "top" }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.6, y: 6.85, w: 0.6, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
});
pres.defineSlideMaster({
  title: "Content", background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: M, y: 0.4, w: 12.1, h: 0.35, fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.5, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.8, w: 12.1, h: 1.05, fontSize: 28, bold: true, color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M, y: 1.9, w: 12.1, h: 0.45, fontSize: 14, color: C.text2, valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "note", type: "body", x: M, y: 6.35, w: 12.1, h: 0.5, fontSize: 10, color: C.accent3, valign: "top", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: 7.0, w: 10, h: 0.3, fontSize: 9, color: C.accent3, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 9, color: C.accent3, align: "right" },
});

// ---------- building blocks ----------
const CHART_TEXT = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt" };
const quiet = () => ({
  ...CHART_TEXT, catAxisLabelColor: HEX.ink2, valAxisLabelColor: HEX.ink3, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
  dataLabelFontSize: 12, dataLabelColor: HEX.navy, valGridLine: { color: HEX.line, size: 0.75 }, catGridLine: { style: "none" },
  catAxisLineShow: false, valAxisLineShow: false,
});

function content(section, kicker, title, sub, note) {
  const s = pres.addSlide({ masterName: "Content", sectionTitle: section });
  s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (sub) s.addText(sub, { placeholder: "sub" });
  if (note) s.addText(note, { placeholder: "note" });
  return s;
}

// Big-number callouts stacked in the right column
const CHART_W = 7.2;
function callouts(s, items, x = 8.2, y = 2.45, w = 4.5, gap = 0.15) {
  const h = (6.25 - y - gap * (items.length - 1)) / items.length;
  items.forEach((c, i) => {
    const top = y + i * (h + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: top, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `callout ${i + 1}` });
    s.addText(c.n, { x: x + 0.25, y: top + 0.1, w: w - 0.5, h: 0.5, fontSize: 28, bold: true, color: c.color || C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText([
      { text: c.t, options: { fontSize: 13, bold: true, color: C.text1, breakLine: !!c.d } },
      ...(c.d ? [{ text: c.d, options: { fontSize: 11, color: C.text2 } }] : []),
    ], { x: x + 0.25, y: top + 0.63, w: w - 0.5, h: h - 0.7, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 2 });
  });
}

// Scatter helpers. The plot area is placed by hand (layout, inner edges), so labels and lines laid over the
// chart line up with the data. pptxgenjs has no log scale on a scatter x-axis, hence log10 values + own tick labels.
const plotBox = (c, L) => ({ x: c.x + L.x * c.w, y: c.y + L.y * c.h, w: L.w * c.w, h: L.h * c.h });
const dotLegend = (s, items, x, y, w) => s.addText(
  items.flatMap(([t, col], j) => [{ text: "● ", options: { color: col } }, { text: t + (j < items.length - 1 ? "     " : ""), options: { color: C.text2 } }]),
  { x, y, w, h: 0.28, fontSize: 11, margin: 0, isTextBox: true, objectName: "legend" });
const label = (s, text, o) => s.addText(text, { fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "middle", ...o });
// Nudge a point along `offsets` until it is clear of the points already placed (distance in inches)
function nudge(placed, xIn, yIn, offsets, axis, minDist = 0.13) {
  for (const o of offsets) {
    const p = axis === "y" ? { xIn, yIn: yIn + o } : { xIn: xIn + o, yIn };
    if (!placed.some(q => Math.hypot(q.xIn - p.xIn, q.yIn - p.yIn) < minDist)) { placed.push(p); return o; }
  }
  placed.push({ xIn, yIn }); return 0;
}
const SCATTER = (L, colors) => ({ ...CHART_TEXT, layout: L, lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 9,
  lineDataSymbolLineColor: HEX.white, lineDataSymbolLineSize: 1, chartColors: colors, catAxisHidden: true, catGridLine: { style: "none" },
  valGridLine: { color: HEX.line, size: 0.75 }, showLegend: false });

// ---------- slides ----------
// 1. Title
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "Title", sectionTitle: "Opening" });
s.addText("BOARD BRIEFING · WORLD CUP 2026 · 48 SQUADS · 104 MATCHES", { placeholder: "kicker" });
s.addText([{ text: "Squad value buys a place in the knockouts, " }, { text: "not the trophy", options: { color: C.accent1 } }], { placeholder: "title" });
s.addText("What a mid-market federation (€200–500m squad value) should do before 2030", { placeholder: "body" });
{ const file = path.resolve(__dirname, "assets/world-cup-trophy.png"), png = fs.readFileSync(file); // PNG header: width, height at bytes 16, 20
  const h = 5.0, w = h * png.readUInt32BE(16) / png.readUInt32BE(20);
  s.addImage({ path: file, x: 12.4 - w, y: 1.2, w, h, altText: "FIFA World Cup trophy and FIFA wordmark", objectName: "trophy" }); }
s.addNotes("Open with the answer. We advise the Board of a mid-market federation: squad value about €200–500m. The decision: where to put long-term investment to improve World Cup results by 2030. Our one sentence: squad value buys a place in the knockouts, not the trophy.");

// 2. KPIs: one slide per block. The block being discussed is highlighted, the others are greyed out,
// so clicking through reads like an animation (pptxgenjs cannot write animations, and Google Slides drops most of them).
pres.addSection({ title: "1 Key insights" });
const kpis = [
  { n: `${pct(K.richer_won_decisive, K.decisive)}%`, t: "of decided matches won by the more valuable squad", d: `${K.richer_won_decisive} of ${K.decisive}`,
    note: `${pct(K.richer_won_decisive, K.decisive)}% of decided matches went to the more valuable squad: ${K.richer_won_decisive} of ${K.decisive}. Value is a reliable floor.` },
  { n: `${K.top32_reached_r32} of 32`, t: "most valuable squads reached the knockouts", d: "The Round of 32 takes 32 of 48 teams.",
    note: `${K.top32_reached_r32} of the 32 most valuable squads reached the knockouts. If you have the value, you get out of the group.` },
  { n: `${K.top8_reached_qf} of 8`, t: "most valuable squads reached the quarter-finals", d: `${list(top8Out)} went out earlier.`,
    note: `But only ${K.top8_reached_qf} of the 8 richest reached the quarter-finals: ${list(top8Out)} went out earlier. Here the floor stops working.` },
  { n: `${K.ko_close_richer} of ${K.ko_close_n}`, t: "close knockout ties won by the more valuable squad", d: "Close to a coin flip.",
    note: `And when two squads were close in value, the richer one went through only ${K.ko_close_richer} of ${K.ko_close_n} times: a coin flip. That is the tension the rest of the deck explains.` },
];
const kw = (12.1 - 3 * 0.3) / 4;
kpis.forEach((_, focus) => {
  s = content("1 Key insights", "01 · What are the key insights?",
    `The more valuable squad won ${K.richer_won_decisive} of ${K.decisive} decided matches, but only ${K.top8_reached_qf} of the 8 richest squads reached the quarter-finals`,
    "Every match and every squad of the 2026 World Cup, compared on pre-tournament squad market value (April 2026).",
    `Decided = a winner after 90 or 120 minutes; shoot-outs count as draws (${K.draws} of ${K.matches} matches). Close ties = knockout ties between squads within 1.5× of each other in value.`);
  kpis.forEach((k, i) => {
    const on = i === focus, x = M + i * (kw + 0.3), y = 2.65;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: kw, h: 3.4, rectRadius: 0.08, objectName: `kpi ${i + 1}${on ? " (focus)" : ""}`,
      fill: { color: on ? C.background2 : C.background1 }, line: on ? { type: "none" } : { color: C.background2, width: 1 } });
    s.addText(k.n, { x: x + 0.25, y: y + 0.3, w: kw - 0.5, h: 1.0, fontSize: 44, bold: true, color: on ? C.accent1 : C.accent6, margin: 0, isTextBox: true });
    s.addText([{ text: k.t, options: { fontSize: 16, bold: true, color: on ? C.text1 : C.accent3, breakLine: true } }, { text: k.d, options: { fontSize: 12, color: on ? C.text2 : C.accent6 } }],
      { x: x + 0.25, y: y + 1.45, w: kw - 0.5, h: 1.8, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 6 });
  });
  s.addNotes(kpis[focus].note);
});

// 3. Value bands
s = content("1 Key insights", "01 · What are the key insights?",
  `Below €500m, ${pastR32(under500)} of ${under500.length} squads won a knockout match; above it, ${pastR32(over500)} of ${over500.length} did`,
  "Share of squads in each value band that reached the Round of 32 and the Round of 16 (= won a knockout match). Number of squads in brackets.",
  "Squad value: Transfermarkt-based market value, April 2026 snapshot (Kaggle). One tournament, 48 squads: association, not cause.");
s.addChart(pres.charts.BAR, [
  { name: "Reached Round of 32", labels: D.bands.map(b => `${b.value_band} (${b.n})`), values: D.bands.map(b => b.r32 / b.n) },
  { name: "Won a knockout match (Round of 16)", labels: D.bands.map(b => `${b.value_band} (${b.n})`), values: D.bands.map(b => b.r16 / b.n) },
], { ...quiet(), x: M, y: 2.45, w: CHART_W, h: 3.8, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60, chartColors: [HEX.grey, HEX.blue],
     showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0%", valAxisMinVal: 0, valAxisMaxVal: 1.1, valAxisLabelFormatCode: "0%",
     valAxisHidden: true, valGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: HEX.ink2, objectName: "chart value bands" });
callouts(s, [
  { n: `${pastR32(under500)} of ${under500.length}`, t: "squads under €500m won a knockout match", d: list(peers.map(t => t.team)) + "." },
  { n: `${pastR32(over500)} of ${over500.length}`, t: "squads at €500m or more did", color: C.accent1, d: "The share jumps from about 1 in 8 to 2 in 3." },
]);
s.addNotes(`Here is where value starts to matter. Below €500m only ${pastR32(under500)} of ${under500.length} squads won a knockout match. Above it, ${pastR32(over500)} of ${over500.length}. Remember the €500m line: it comes back in the recommendation.`);

// 3b. Option B for slide 3 (the team keeps one of the two): every squad as a dot, value vs stage reached
s = content("1 Key insights", "01 · Option B for the previous slide (keep one)",
  `Below €500m, ${pastR32(under500)} of ${under500.length} squads won a knockout match; above it, ${pastR32(over500)} of ${over500.length} did`,
  "Each dot is a squad: pre-tournament market value (log scale) against the stage it reached. Colour compares that stage with the one its value rank predicted.",
  "Squad value: Transfermarkt-based market value, April 2026 snapshot (Kaggle). One tournament, 48 squads: association, not cause.");
{
  const CH = { x: M, y: 2.8, w: 12.1, h: 3.15 }, L = { x: 0.1, y: 0.03, w: 0.88, h: 0.86 }, P = plotBox(CH, L);
  const lo = Math.log10(30), hi = Math.log10(2000);
  const px = v => P.x + (Math.log10(v) - lo) / (hi - lo) * P.w, py = st => P.y + (7.5 - st) / 7 * P.h;
  const placed = [];
  const pts = [...T].sort((a, b) => a.market_value_m - b.market_value_m).map(t => {
    const off = nudge(placed, px(t.market_value_m), py(t.stage_reached), [0, -0.13, 0.13], "y"); // inches; up = negative
    return { t, x: Math.log10(t.market_value_m), y: t.stage_reached - off / (P.h / 7), xIn: px(t.market_value_m), yIn: py(t.stage_reached) + off };
  });
  const sign = t => Math.sign(t.stage_vs_expected);
  s.addChart(pres.charts.SCATTER, [
    { name: "Value (log10)", values: pts.map(p => p.x) },
    { name: "Went further than value predicted", values: pts.map(p => sign(p.t) > 0 ? p.y : null) },
    { name: "As predicted", values: pts.map(p => sign(p.t) === 0 ? p.y : null) },
    { name: "Fell short", values: pts.map(p => sign(p.t) < 0 ? p.y : null) },
  ], { ...SCATTER(L, [HEX.blue, HEX.grey, HEX.orange]), ...CH, catAxisMinVal: lo, catAxisMaxVal: hi,
       valAxisMinVal: 0.5, valAxisMaxVal: 7.5, valAxisMajorUnit: 1, valAxisHidden: true, objectName: "chart squads value vs stage" });
  STAGE.forEach((name, i) => label(s, name, { x: M, y: py(i + 1) - 0.14, w: P.x - M - 0.12, h: 0.28, align: "right", objectName: `row ${name}` }));
  [50, 100, 250, 500, 1000].forEach(v => label(s, fmtM(v), { x: px(v) - 0.4, y: P.y + P.h + 0.04, w: 0.8, h: 0.24, align: "center", fontSize: 10,
    color: v === 500 ? C.text1 : C.accent3, bold: v === 500 }));
  // €500m line through the plot and the header strip, with the two counts either side of it
  s.addShape(pres.shapes.LINE, { x: px(500), y: 2.45, w: 0, h: P.y + P.h - 2.45, line: { color: C.text1, width: 1.25, dashType: "dash" }, objectName: "500m line" });
  label(s, [{ text: `${pastR32(under500)} of ${under500.length}  `, options: { bold: true, fontSize: 16, color: C.text1 } }, { text: "squads under €500m won a knockout match" }],
    { x: M, y: 2.42, w: px(500) - M - 0.15, h: 0.34, align: "right", fontSize: 12 });
  label(s, [{ text: `${pastR32(over500)} of ${over500.length}  `, options: { bold: true, fontSize: 16, color: C.accent1 } }, { text: "at €500m or more did" }],
    { x: px(500) + 0.15, y: 2.42, w: 4.5, h: 0.34, fontSize: 12 });
  for (const p of pts.filter(p => ["Spain", "Argentina", "France", "Switzerland", "Paraguay"].includes(p.t.team))) {
    const left = p.t.team === "Switzerland"; // sits on the €500m line: label it to the left instead of above
    label(s, p.t.team, left ? { x: p.xIn - 1.32, y: p.yIn - 0.1, w: 1.2, h: 0.2, align: "right", fontSize: 10, bold: true, color: C.text1 }
                            : { x: p.xIn - 0.6, y: p.yIn - 0.33, w: 1.2, h: 0.2, align: "center", fontSize: 10, bold: true, color: C.text1 });
  }
  dotLegend(s, [["Went further than value predicted", HEX.blue], ["As predicted", HEX.grey], ["Fell short", HEX.orange]], P.x, P.y + P.h + 0.32, 7);
  label(s, "Squad market value, log scale →", { x: P.x + P.w - 3, y: P.y + P.h + 0.32, w: 3, h: 0.28, align: "right", fontSize: 10, color: C.accent3 });
}
s.addNotes(`Option B: the same message, squad by squad. Left of the line, almost everyone stops at the Round of 32; right of it, most squads win a knockout match. The colours introduce the idea we use next: did a squad go further or less far than its value predicted?`);

// 4. Top-k
s = content("1 Key insights", "01 · What are the key insights?",
  `Value secures the knockouts, not the late rounds: ${TOPK[0].n} of the top 32 reached the Round of 32, ${TOPK[2].n} of the top 8 the quarter-finals`,
  "Of the k most valuable squads, the share that reached the stage k teams reach.",
  "The top 4, 2 and 1 are tiny samples: read them as illustration, not proof.");
s.addChart(pres.charts.BAR, [{ name: "Reached the stage", labels: TOPK.map(d => `${d.k === 1 ? "Most valuable" : `Top ${d.k}`} → ${STAGE[d.s - 1]}  (${d.n} of ${d.k})`), values: TOPK.map(d => d.n / d.k) }],
  { ...quiet(), x: M, y: 2.45, w: CHART_W, h: 3.8, barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 45, chartColors: [HEX.blue],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0%", valAxisMinVal: 0, valAxisMaxVal: 1.1, valAxisHidden: true,
    valGridLine: { style: "none" }, showLegend: false, objectName: "chart top-k" });
const fr = T.find(t => t.value_rank === 1);
callouts(s, [
  { n: `${TOPK[0].n} of 32`, t: "of the top 32 reached the Round of 32" },
  { n: `${TOPK[2].n} of 8`, t: "of the top 8 reached the quarter-finals", color: C.accent1, d: `${list(TOPK[2].missed.map(t => t.team))} missed.` },
  { n: "0 of 1", t: `${fr.team} (${fmtM(fr.market_value_m)}), the most valuable squad`, color: C.accent2, d: `went out in the ${STAGE[fr.stage_reached - 1].toLowerCase()}s.` },
]);
s.addNotes("The higher the bar, the less value guarantees. Value is a reliable floor, not a ceiling. The question is what happens above the floor.");

// 5. Drivers
pres.addSection({ title: "2 Drivers" });

// 6. Rounds
const sf = R["Semifinal"];
s = content("2 Drivers", "02 · What is driving the results?",
  `By the semi-finals, opponents were within ${sf.median_gap.toFixed(1)}× of each other in value, and the more valuable squad lost both`,
  "Every knockout tie as a dot: the value gap between the two squads (more valuable ÷ less valuable, log scale), round by round. Shaded: within 1.5×.",
  "Shoot-outs count by who went through; third-place match excluded. The gap does not fall every round (QF 2.0× vs R16 1.5×), and there were only 2 semi-finals and 1 final.");
// Dot strip instead of bars, so it reads differently from the top-k bars in part 1. Round labels sit under the plot
// as text (PowerPoint would format numbers in chart labels with the viewer's locale: 2,7× in German).
{
  const CH = { x: M, y: 2.8, w: CHART_W, h: 2.75 }, L = { x: 0.08, y: 0.02, w: 0.9, h: 0.96 }, P = plotBox(CH, L), yMax = 16;
  const px = r => P.x + (r - 0.5) / 5 * P.w, py = g => P.y + (1 - Math.log2(g) / Math.log2(yMax)) * P.h;
  s.addShape(pres.shapes.RECTANGLE, { x: P.x, y: py(1.5), w: P.w, h: py(1) - py(1.5), fill: { color: C.background2 }, line: { type: "none" }, objectName: "within 1.5x zone" });
  label(s, "within\n1.5×", { x: P.x + P.w + 0.05, y: py(1.5), w: 0.5, h: py(1) - py(1.5), fontSize: 9, color: C.accent3 });
  const placed = [];
  const ties = D.matches.filter(m => KO.includes(m.stage)).sort((a, b) => a.value_gap - b.value_gap).map(m => {
    const r = KO.indexOf(m.stage) + 1, off = nudge(placed, px(r), py(m.value_gap), [0, -0.15, 0.15, -0.3, 0.3], "x");
    return { m, x: r + off / (P.w / 5) };
  });
  s.addChart(pres.charts.SCATTER, [
    { name: "Round", values: ties.map(t => t.x) },
    { name: "More valuable squad went through", values: ties.map(t => t.m.richer_progressed === 1 ? t.m.value_gap : null) },
    { name: "Less valuable squad went through", values: ties.map(t => t.m.richer_progressed === 1 ? null : t.m.value_gap) },
  ], { ...SCATTER(L, [HEX.blue, HEX.orange]), ...CH, catAxisMinVal: 0.5, catAxisMaxVal: 5.5, valAxisLogScaleBase: 2, valAxisMinVal: 1,
       valAxisMaxVal: yMax, valAxisLabelFormatCode: '0"×"', valAxisLabelColor: HEX.ink3, valAxisLabelFontSize: 10, valAxisLineShow: false,
       objectName: "chart ties by round" });
  KO.forEach((k, i) => label(s, [
    { text: STAGE[i + 1], options: { bold: true, color: C.text1, breakLine: true } },
    { text: `median ${R[k].median_gap.toFixed(1)}×`, options: { breakLine: true } },
    { text: `richer won ${R[k].richer_through} of ${R[k].n}` },
  ], { x: px(i + 1) - P.w / 10, y: P.y + P.h + 0.06, w: P.w / 5, h: 0.6, align: "center", valign: "top", fontSize: 10, objectName: `round ${k}` }));
  dotLegend(s, [["More valuable squad went through", HEX.blue], ["Less valuable squad went through", HEX.orange]], M, 2.45, CHART_W);
}
callouts(s, [
  { n: `${K.ko_close_richer} of ${K.ko_close_n}`, t: "close knockout ties went to the richer side", d: "Within 1.5× in value: close to a coin flip." },
  { n: `${Math.round(DR.ko_close_margin * 100)}%`, t: "of knockout matches were within one goal", d: `Group stage: ${Math.round(DR.group_close_margin * 100)}%.` },
  { n: `${sf.richer_through} of ${sf.n}`, t: "semi-finals won by the richer side", color: C.accent2 },
]);
s.addNotes("Value gets you into the room. Once everyone in the room is rich, small margins decide: in close ties the richer side went through only 6 of 10 times, and two thirds of knockout matches were level or decided by one goal. Be honest: only two semi-finals, so this is an illustration, not proof.");

// 7. Confederations
const groups = [...confRows.map(c => ({ name: c.confederation, n: c.n, mean: c.mean })), { name: "Hosts", n: hosts.length, mean: DR.hosts.mean }]
  .map(g => ({ ...g, label: `${g.name} (${g.n}):  ${g.mean > 0 ? "+" : g.mean < 0 ? "−" : ""}${Math.abs(g.mean).toFixed(2)}` }));
s = content("2 Drivers", "02 · What is driving the results?",
  "African squads and the three hosts went further than their value predicted; Europe’s squads fell short on average",
  "Average stages reached above (+) or below (−) the stage each squad’s value rank predicted, by confederation. Number of squads in brackets.",
  "Small groups: a signal, not a finding. The hosts belong to CONCACAF and account for its whole surplus. Home advantage is confounded with hosting; 8 of 32 Round-of-32 places went to best third-placed teams.");
s.addChart(pres.charts.BAR, [{ name: "Stages vs value expectation", labels: groups.map(g => g.label), values: groups.map(g => +g.mean.toFixed(2)) }],
  { ...quiet(), x: M, y: 2.45, w: CHART_W, h: 3.8, barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 45,
    chartColors: [HEX.blue], invertedColors: [HEX.orange], showValue: false,
    valAxisMinVal: -0.4, valAxisMaxVal: 0.8, valAxisHidden: true, valGridLine: { style: "none" }, catAxisLabelPos: "low", showLegend: false,
    objectName: "chart confederations" });
callouts(s, [
  { n: signed(caf.net), t: `net stages for the ${caf.n} African (CAF) squads`, color: C.accent1, d: `${cafTeams.filter(t => t.stage_vs_expected > 0).length} beat their value rank, none fell short.` },
  { n: `${hosts.filter(t => t.stage_reached >= 3).length} of ${hosts.length}`, t: "hosts reached the Round of 16", color: C.accent1, d: `${list(hosts.filter(t => t.stage_vs_expected > 0).map(t => t.team))} beat value by one stage.` },
  { n: signed(uefa.net), t: `net stages for the ${uefa.n} European (UEFA) squads`, color: C.accent2, d: `${uefaMinus2.map(t => t.team).join(", ")}: −2 each.` },
]);
s.addNotes("Who beat the value expectation? African squads: plus five stages net, none fell short. All three hosts reached the Round of 16. Europe's squads fell short, led by France, Germany and the Netherlands. Small groups, so treat this as a signal.");

// 9. Recommendation
pres.addSection({ title: "3 Recommendation" });

// 10. Curve + actions
s = content("3 Recommendation", "03 · What should the Board do next?",
  `Target a €500m squad by 2030: it turns the Round of 16 from a long shot (${p100(at("r16", 250))}) into a realistic goal (${p100(at("r16", 500))})`,
  "Modelled chance of reaching each stage by squad value (logistic regression, 48 squads; value axis log-spaced). Light blue: 95% interval for the Round of 16.",
  "One tournament: association, not cause, and the interval is wide. Value is a proxy for player quality, not a lever; that a player pathway into top leagues raises it is our assumption, not something this data tests.");
const tickAt = new Map([50, 100, 250, 500, 1000].map(v => [nearest(v), fmtM(v)]));
const gridLabels = G.map((g, i) => tickAt.get(i) || "");
s.addChart(pres.charts.LINE, [
  { name: "Round of 32", labels: gridLabels, values: D.curves.r32 },
  { name: "Round of 16", labels: gridLabels, values: D.curves.r16 },
  { name: "Quarter-final", labels: gridLabels, values: D.curves.qf },
  { name: "R16 95% interval (low)", labels: gridLabels, values: ci.lo },
  { name: "R16 95% interval (high)", labels: gridLabels, values: ci.hi },
], { ...quiet(), x: M, y: 2.8, w: 7.0, h: 3.45, chartColors: [HEX.grey, HEX.blue, "B5BCC8", HEX.ice, HEX.ice], lineSize: 2.5, lineDataSymbol: "none",
     valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25, valAxisLabelFormatCode: "0%", catAxisLabelFrequency: 1, catAxisLabelRotate: 0,
     showLegend: false, objectName: "chart probability curve" });
// Hand-made legend: the two interval lines would otherwise take two legend entries
s.addText([["Round of 16", HEX.blue], ["95% interval (Round of 16)", HEX.ice], ["Round of 32", HEX.grey], ["Quarter-final", "B5BCC8"]]
  .flatMap(([t, col], j) => [{ text: "━ ", options: { color: col, bold: true } }, { text: t + (j < 3 ? "     " : ""), options: { color: C.text2 } }]),
  { x: M, y: 2.45, w: 7.0, h: 0.3, fontSize: 11, margin: 0, isTextBox: true, objectName: "curve legend" });
const actions = [
  { h: "Set a squad-value target of about €500m by 2030", i: `Round of 16: ${p100(at("r16", 250))} at €250m → ${p100(at("r16", 500))} at €500m (95% interval ${p100(ci.lo[i500])}–${p100(ci.hi[i500])}). Route: a player pathway into top leagues.`, o: "Sporting director" },
  { h: "Judge team and coach against a value-adjusted expectation", i: `At €250m the Round of 32 is par (${p100(at("r32", 250))}), the Round of 16 a bonus (${p100(at("r16", 250))}).`, o: "Board, at each tournament review" },
  { h: "Study the squads that won a knockout match on less than €500m", i: `Only ${peers.length} of ${under500.length} did: ${list(peers.map(t => `${t.team} (${STAGE_SHORT[t.stage_reached - 1]}${t.host_nation === "Yes" ? ", host" : ""})`))}.`, o: "Technical director" },
];
actions.forEach((a, i) => {
  const x = 8.0, y = 2.45 + i * 1.3;
  s.addShape(pres.shapes.OVAL, { x, y: y + 0.03, w: 0.38, h: 0.38, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `action ${i + 1} badge` });
  s.addText(String(i + 1), { x, y: y + 0.03, w: 0.38, h: 0.38, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText([
    { text: a.h, options: { fontSize: 14, bold: true, color: C.text1, breakLine: true } },
    { text: `${a.i} `, options: { fontSize: 11, color: C.text2 } },
    { text: `Owner: ${a.o}.`, options: { fontSize: 11, bold: true, color: C.accent3 } },
  ], { x: x + 0.55, y, w: 12.7 - x - 0.55, h: 1.2, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 3 });
});
s.addNotes(`At €250m the Round of 16 is a lottery (${p100(at("r16", 250))}); at €500m it is a plan (${p100(at("r16", 500))}). Be ready for: 41% is still below 50%. Yes: €500m makes the Round of 16 realistic, not likely. Three actions, each with an owner.`);

// 10b. Option B for slide 10 (keep one): "what is vs what could be" at €250m today and €500m by 2030
s = content("3 Recommendation", "03 · Option B for the previous slide (keep one)",
  `At €500m every stage gets realistic: Round of 16 from ${p100(at("r16", 250))} to ${p100(at("r16", 500))}, quarter-final from ${p100(at("qf", 250))} to ${p100(at("qf", 500))}`,
  "What is vs what could be: modelled chance of reaching each stage for a squad valued at €250m today and at €500m by 2030 (logistic regression, 48 squads).",
  `One tournament: association, not cause. 95% interval for the Round of 16 at €500m: ${p100(ci.lo[i500])}–${p100(ci.hi[i500])}. Value is a proxy, not a lever; the player-pathway route is our assumption.`);
{
  const w3 = (12.1 - 2 * 0.3) / 3;
  [["r32", "Round of 32"], ["r16", "Round of 16"], ["qf", "Quarter-final"]].forEach(([k, name], i) => {
    const x = M + i * (w3 + 0.3), y = 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: w3, h: 1.8, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `then-now ${name}` });
    label(s, name, { x: x + 0.3, y: y + 0.18, w: w3 - 0.6, h: 0.3, fontSize: 14, bold: true, color: C.text1 });
    label(s, [{ text: p100(at(k, 250)), options: { color: C.accent3 } }, { text: "  →  ", options: { fontSize: 26, bold: false, color: C.accent3 } },
              { text: p100(at(k, 500)), options: { color: C.accent1 } }], { x: x + 0.3, y: y + 0.55, w: w3 - 0.6, h: 0.75, fontSize: 40, bold: true });
    label(s, "€250m today  →  €500m by 2030", { x: x + 0.3, y: y + 1.35, w: w3 - 0.6, h: 0.28, fontSize: 11 });
  });
  const acts = [
    { h: "Target about €500m squad value by 2030", d: "Route: a player pathway into top leagues.", o: "Sporting director" },
    { h: "Judge team and coach against a value-adjusted expectation", d: `At €250m the Round of 32 is par, the Round of 16 a bonus.`, o: "Board" },
    { h: `Study the ${peers.length} squads that won a knockout match on under €500m`, d: `${list(peers.map(t => t.team))}.`, o: "Technical director" },
  ];
  acts.forEach((a, i) => {
    const x = M + i * (w3 + 0.3), y = 4.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: w3, h: 1.75, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: C.background2, width: 1.5 }, objectName: `action ${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.22, w: 0.38, h: 0.38, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `action ${i + 1} badge` });
    label(s, String(i + 1), { x: x + 0.25, y: y + 0.22, w: 0.38, h: 0.38, fontSize: 14, bold: true, color: C.background1, align: "center" });
    label(s, [{ text: a.h, options: { fontSize: 14, bold: true, color: C.text1, breakLine: true } }, { text: a.d, options: { fontSize: 11, breakLine: true } },
              { text: `Owner: ${a.o}`, options: { fontSize: 11, bold: true, color: C.accent3 } }],
      { x: x + 0.8, y: y + 0.18, w: w3 - 1.05, h: 1.45, valign: "top", paraSpaceAfter: 3 });
  });
}
s.addNotes(`Option B. Contrast what is with what could be. Today, at €250m, the Round of 16 is a ${p100(at("r16", 250))} shot. At €500m it is ${p100(at("r16", 500))}, and the quarter-final becomes possible. Three actions get us there, each with an owner.`);

// 11. The ask
s = pres.addSlide({ masterName: "Section dark", sectionTitle: "3 Recommendation" });
s.addText("THE ASK", { placeholder: "num" });
s.addText("Approve a €500m squad-value target for 2030 and a value-adjusted scorecard", { placeholder: "title" });
s.addText("First step: the sporting director maps where the current squad plays and returns a pathway plan within 90 days.", { placeholder: "body" });
s.addNotes("End on the decision and the first step. Pause before the ask. Then open the floor.");

// 12. Backup section
pres.addSection({ title: "Backup" });
// 12a. Backup: undervalued
s = content("Backup", "Backup · for Q&A",
  "Being “undervalued” by the market did not predict going further than value expected",
  "“Undervalued” = the market ranks a squad lower than FIFA’s results-based ranking does (value rank minus FIFA rank).",
  "Spearman rank correlations, n = 48 unless stated. Correlation is a screen, not a diagnosis: what drives over-performance lies outside this data (coaching, cohesion, the draw, home advantage).");
const stats3 = [
  { n: `ρ = ${UV.rho.toFixed(2)}`, t: "undervaluation vs stages beyond the value expectation", d: `p = ${UV.p.toFixed(2)}. The ${UV.n_top} most undervalued squads averaged ${signed(UV.mean_top, 2)} stages.` },
  { n: `ρ = ${DR.uefa_only.rho.toFixed(2)}`, t: `value vs stage reached within UEFA alone (n = ${DR.uefa_only.n})`, d: "Same as across all 48: the headline is not an artefact of the confederation mix (Simpson check)." },
  { n: `ρ = ${signed(DR.group_strength_vs_expected.rho, 2).replace("+", "")}`, t: "group strength vs over/under-performance", d: "A hard draw does not explain who fell short." },
];
stats3.forEach((c, i) => {
  const w3 = (12.1 - 2 * 0.3) / 3, xx = M + i * (w3 + 0.3), y = 2.65;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: xx, y, w: w3, h: 3.4, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `stat ${i + 1}` });
  s.addText(c.n, { x: xx + 0.3, y: y + 0.3, w: w3 - 0.6, h: 1.0, fontSize: 44, bold: true, color: C.text1, margin: 0, isTextBox: true });
  s.addText([{ text: c.t, options: { fontSize: 16, bold: true, color: C.text1, breakLine: true } }, { text: c.d, options: { fontSize: 13, color: C.text2 } }],
    { x: xx + 0.3, y: y + 1.45, w: w3 - 0.6, h: 1.8, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 6 });
});
s.addNotes("Backup for the evidence challenger. The challenge asks whether undervalued federations outperformed. They did not, measured against FIFA's ranking. And the value effect holds within Europe alone, so it is not a confederation artefact.");

// 12b. Backup: method
s = content("Backup", "Backup · Data, method and limits", "How we got the numbers, and what they cannot tell you", null,
  "Full log of assumptions, transformations and AI use: docs/decisions.md. Every number with its denominator: docs/results.md.");
const cols = [
  { h: "Data", b: ["Kaggle: 48 squads with April 2026 market value, FIFA rank and bookmaker odds", `Kaggle: all ${K.matches} match results`, "One team name harmonised; stage reached derived from the match list (one label was wrong)"] },
  { h: "Method", b: ["Value-only expectation: the k-th most valuable squad should reach the k-th best finish", "Spearman rank correlation with bootstrap 95% CI", "Logistic regression of reaching each stage on log(value)"] },
  { h: "Limits", b: ["One tournament, 48 squads: association, not cause", "Value, FIFA rank and odds predict about equally well (ρ\u00a00.64–0.74)", "Market value is a proxy for quality, not a lever"] },
];
const w3 = (12.1 - 2 * 0.3) / 3;
cols.forEach((c, i) => {
  const x = M + i * (w3 + 0.3), y = 2.2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: w3, h: 3.9, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `method ${c.h}` });
  s.addText(c.h, { x: x + 0.3, y: y + 0.25, w: w3 - 0.6, h: 0.45, fontSize: 18, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  s.addText(c.b.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < c.b.length - 1 } })),
    { x: x + 0.3, y: y + 0.85, w: w3 - 0.6, h: 2.9, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 8, isTextBox: true });
});

(async () => {
  await pres.writeFile({ fileName: OUT });
  const { applyTheme } = require("./apply_theme.js"); // pptxgenjs cannot write theme colors itself
  await applyTheme(OUT, THEME);
  console.log(`wrote ${path.relative(process.cwd(), OUT)}`);
})();
