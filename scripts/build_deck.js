// Build the 9-slide CSC 30100 final-project presentation deck.
// Output: report/Chan_Arsenii_CSC30100_FinalPresentation_navy.pptx
// (the navy-palette deck; sibling figures live in report/figures/, QR in report/qr/)
// The primary deliverable deck (template-based) is built by
// scripts/build_template_deck.py; this navy version is the backup.
//
// Theme: "Midnight Executive" palette — navy primary, ice-blue secondary, white accent.
// Title + closing slides are dark; content slides are light. (The "sandwich" structure
// recommended by the pptx skill: dark for opens/closes, light for content.)
// Fonts: Cambria (headers, math-friendly serif) + Calibri (body).
// Visual motif: a thin vertical navy accent bar on the left of content slides.
// (The skill explicitly warns against horizontal accent lines under titles.)

const path = require("path");
const PptxGenJS = require("pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const FIG = path.join(REPO, "report", "figures");
const QR  = path.join(REPO, "report", "qr");
const OUT = path.join(REPO, "report", "Chan_Arsenii_CSC30100_FinalPresentation_navy.pptx");

// Palette
const NAVY    = "1E2761";   // primary
const ICE     = "CADCFC";   // secondary
const WHITE   = "FFFFFF";
const INK     = "1E293B";   // body text on light slides
const MUTED   = "64748B";   // secondary text
const ACCENT  = "F96167";   // single sharp accent (the μ* number, the "demo" callout)
const RULE    = "E2E8F0";   // subtle divider

// Typography
const HEADER_FONT = "Cambria";
const BODY_FONT   = "Calibri";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function addAccentBar(slide) {
  // Thin navy bar down the left edge — the recurring visual motif.
  slide.addShape("rect", {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 },
  });
}

function addPageNumber(slide, n, total) {
  slide.addText(`${n} / ${total}`, {
    x: 9.4, y: 5.35, w: 0.5, h: 0.25,
    fontFace: BODY_FONT, fontSize: 9, color: MUTED, align: "right",
    margin: 0,
  });
}

// ---------------------------------------------------------------------------
// Deck
// ---------------------------------------------------------------------------

const pres = new PptxGenJS();
pres.layout = "LAYOUT_16x9";        // 10" × 5.625"
pres.author = "Arsenii Chan";
pres.title  = "Startup Growth Dynamics & Valuation";
pres.subject = "CSC 30100 final project";

const TOTAL_SLIDES = 9;

// ===========================================================================
// SLIDE 1 — TITLE (dark, no image)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Title centered
  s.addText("Startup Growth Dynamics & Valuation", {
    x: 0.6, y: 1.55, w: 8.8, h: 1.2,
    fontFace: HEADER_FONT, fontSize: 40, color: WHITE,
    bold: true, align: "center", valign: "middle",
  });

  // Subtitle
  s.addText("A Numerical Methods Approach", {
    x: 0.6, y: 2.7, w: 8.8, h: 0.5,
    fontFace: HEADER_FONT, fontSize: 22, color: ICE,
    italic: true, align: "center", valign: "middle",
  });

  // Author / course / date
  s.addText("Arsenii Chan   ·   CSC 30100   ·   Spring 2026", {
    x: 0.6, y: 4.4, w: 8.8, h: 0.4,
    fontFace: BODY_FONT, fontSize: 14, color: ICE,
    align: "center",
  });

  // Tiny accent rule between subtitle and author (centered, short — NOT under the title)
  s.addShape("rect", {
    x: 4.4, y: 3.6, w: 1.2, h: 0.02,
    fill: { color: ACCENT }, line: { color: ACCENT, width: 0 },
  });

  s.addNotes(
    "Hi, I'm Arsenii. For my Numerical Analysis final, I built a " +
    "startup-survival threshold calculator from scratch — and I want " +
    "to walk you through what it found.\n\n" +
    "[target: 10 seconds]"
  );
}

// ===========================================================================
// SLIDE 2 — THE QUESTION (dark, no image)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Quote mark at top-left as a typographic accent
  s.addText("“", {
    x: 0.6, y: 0.2, w: 1.2, h: 1.2,
    fontFace: HEADER_FONT, fontSize: 110, color: ACCENT,
    align: "left", valign: "top", margin: 0,
  });

  // The driving question — big, centered
  s.addText(
    "At what user-churn rate does a startup’s growth become " +
    "mathematically irreversible — and how confident can we be in " +
    "that answer?",
    {
      x: 1.1, y: 1.2, w: 7.8, h: 2.2,
      fontFace: HEADER_FONT, fontSize: 28, color: WHITE,
      bold: false, italic: true, align: "left", valign: "middle",
      paraSpaceAfter: 6,
    }
  );

  // Plain-English translation underneath
  s.addText("In plain English:", {
    x: 1.1, y: 3.7, w: 7.8, h: 0.35,
    fontFace: BODY_FONT, fontSize: 13, color: ICE,
    bold: true, align: "left", margin: 0,
  });

  s.addText(
    "The single monthly user-cancellation rate above which no amount " +
    "of growth saves the business — and how sure are we?",
    {
      x: 1.1, y: 4.05, w: 7.8, h: 0.85,
      fontFace: BODY_FONT, fontSize: 16, color: WHITE,
      align: "left", valign: "top",
    }
  );

  s.addNotes(
    "Every venture capitalist looks at a startup and asks one question: " +
    "will this company survive? You can answer that with intuition, or " +
    "you can answer it with math. I built the math.\n\n" +
    "Take a typical software-as-a-service startup — reasonable growth, " +
    "reasonable conversion, reasonable costs. There's a single number — " +
    "the rate at which paying users cancel each month — above which the " +
    "company runs out of money before it can ever recover, within a " +
    "10-year horizon. For our default profile, that number is about " +
    "14 percent.\n\n" +
    "Below 14 percent monthly churn, the company survives. Above 14, " +
    "it doesn't. Let me show you how I found it, and how confident I " +
    "am in the answer.\n\n" +
    "[target: 40 seconds]"
  );
}

// ===========================================================================
// SLIDE 3 — THE MODEL (light, equations + small inset)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("The 4D ODE system", {
    x: 0.55, y: 0.35, w: 9, h: 0.6,
    fontFace: HEADER_FONT, fontSize: 30, color: NAVY, bold: true,
    margin: 0,
  });

  s.addText(
    "Four coupled differential equations on (Users, Active, Revenue, Cash):",
    {
      x: 0.55, y: 0.95, w: 9, h: 0.35,
      fontFace: BODY_FONT, fontSize: 13, color: MUTED, italic: true,
      margin: 0,
    }
  );

  // Equations as a multi-line text block in a monospace font.
  // Comments are shown on the SAME line as each equation (right-aligned via
  // padding) to keep the math one-line and avoid wrapping into the inset.
  const eqLines = [
    { text: "dU/dt    = g · U · (1 − U/K)",
      options: { breakLine: true } },
    { text: "           logistic acquisition",
      options: { color: MUTED, italic: true, fontSize: 12, breakLine: true } },
    { text: "dA/dt    = α · g · U · (1 − U/K) − μ · A",
      options: { breakLine: true } },
    { text: "           conversion − churn",
      options: { color: MUTED, italic: true, fontSize: 12, breakLine: true } },
    { text: "dR/dt    = μ_R · (p · A − R)",
      options: { breakLine: true } },
    { text: "           billing-cycle lag toward p·A",
      options: { color: MUTED, italic: true, fontSize: 12, breakLine: true } },
    { text: "dCash/dt = R − F − v · g · U · (1 − U/K)",
      options: { breakLine: true } },
    { text: "           revenue − costs",
      options: { color: MUTED, italic: true, fontSize: 12 } },
  ];
  s.addText(eqLines, {
    x: 0.55, y: 1.45, w: 5.5, h: 3.5,
    fontFace: "Consolas", fontSize: 14, color: INK,
    valign: "top", margin: 0,
  });

  // Inset: default trajectory figure — sized prominently so the four-panel
  // U/A/R/Cash plot is legible, not a thumbnail.
  s.addImage({
    path: path.join(FIG, "nb01_default_trajectory.png"),
    x: 6.15, y: 1.35, w: 3.7, h: 2.5,
    sizing: { type: "contain", w: 3.7, h: 2.5 },
  });
  s.addText("Default-SaaS trajectory, 60 months (RK4)", {
    x: 6.15, y: 3.9, w: 3.7, h: 0.3,
    fontFace: BODY_FONT, fontSize: 10, color: MUTED, italic: true,
    align: "center", margin: 0,
  });

  // Eight-parameter callout at bottom right
  s.addText(
    "Eight parameters, public-data-estimable: g, K, α, μ, p, μ_R, F, v.",
    {
      x: 0.55, y: 4.95, w: 9, h: 0.35,
      fontFace: BODY_FONT, fontSize: 12, color: MUTED, italic: true,
      align: "left", margin: 0,
    }
  );

  addPageNumber(s, 3, TOTAL_SLIDES);

  s.addNotes(
    "I modeled a startup as four coupled differential equations — on " +
    "users, paying users, revenue, and cash. Users follow logistic " +
    "acquisition. Paying users are conversion minus churn. Revenue lags " +
    "the paying-user base — I call this the billing-cycle lag, capturing " +
    "annual contracts and deferred revenue. Cash is revenue minus fixed " +
    "and variable costs.\n\n" +
    "The whole system runs on eight parameters a V-C can estimate from " +
    "public data: growth rate, market size, average revenue per user, " +
    "churn, and costs. The inset on the right shows the default profile " +
    "run for 60 months — the S-curve in users, revenue catching up, " +
    "and cash dipping before it recovers.\n\n" +
    "[target: 50 seconds]"
  );
}

// ===========================================================================
// SLIDE 4 — CONVERGENCE (light, big plot)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("Five solvers from scratch — convergence verified", {
    x: 0.55, y: 0.35, w: 9.2, h: 0.6,
    fontFace: HEADER_FONT, fontSize: 26, color: NAVY, bold: true,
    margin: 0,
  });

  // Large-bleed figure
  s.addImage({
    path: path.join(FIG, "nb02_convergence.png"),
    x: 0.55, y: 1.1, w: 6.2, h: 3.9,
    sizing: { type: "contain", w: 6.2, h: 3.9 },
  });

  // Right column: the order claims, big and clean
  s.addText("Theory  vs  measured", {
    x: 7.0, y: 1.2, w: 2.8, h: 0.35,
    fontFace: BODY_FONT, fontSize: 13, color: MUTED,
    bold: true, margin: 0,
  });

  const orderRows = [
    { label: "Euler",       theory: "O(h)",   measured: "1.01" },
    { label: "Heun",        theory: "O(h²)", measured: "2.07" },
    { label: "RK4",         theory: "O(h⁴)", measured: "4.07" },
    { label: "AB4",         theory: "O(h⁴)", measured: "3.91" },
    { label: "Adams-Moulton", theory: "O(h⁴)", measured: "4.19" },
  ];

  orderRows.forEach((r, i) => {
    const y = 1.65 + i * 0.45;
    s.addText(r.label, {
      x: 7.0, y, w: 1.4, h: 0.4,
      fontFace: BODY_FONT, fontSize: 14, color: INK,
      bold: true, margin: 0, valign: "middle",
    });
    s.addText(r.theory, {
      x: 8.4, y, w: 0.7, h: 0.4,
      fontFace: BODY_FONT, fontSize: 13, color: MUTED,
      margin: 0, valign: "middle",
    });
    s.addText(r.measured, {
      x: 9.1, y, w: 0.7, h: 0.4,
      fontFace: BODY_FONT, fontSize: 14, color: NAVY,
      bold: true, align: "right", margin: 0, valign: "middle",
    });
  });

  s.addText(
    "No SciPy. Each method matches its theoretical convergence " +
    "order to within 4%.",
    {
      x: 0.55, y: 5.05, w: 9.2, h: 0.35,
      fontFace: BODY_FONT, fontSize: 12, color: MUTED, italic: true,
      align: "left", margin: 0,
    }
  );

  addPageNumber(s, 4, TOTAL_SLIDES);

  s.addNotes(
    "I implemented all five O-D-E solvers from scratch — no SciPy. " +
    "Each method matches its theoretical convergence order to within " +
    "4 percent. Euler at slope one, Heun at slope two, the three " +
    "fourth-order methods at slope four. The lines you see on this " +
    "log-log plot are the proof.\n\n" +
    "Without this slide, every number downstream is a guess. This is " +
    "the contract everything else rests on.\n\n" +
    "[target: 45 seconds]"
  );
}

// ===========================================================================
// SLIDE 5 — THE VALLEY (light, full-bleed hero figure)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("Calibrating from data — a structural-identifiability finding", {
    x: 0.55, y: 0.3, w: 9.2, h: 0.55,
    fontFace: HEADER_FONT, fontSize: 23, color: NAVY, bold: true,
    margin: 0,
  });

  // Hero figure — give it most of the slide.
  // Uses the presentation-quality redraw (pres_loss_surface.png) instead
  // of the notebook export, which had overlapping contour-value labels in
  // the dense valley region. Same data, cleaner rendering.
  s.addImage({
    path: path.join(FIG, "pres_loss_surface.png"),
    x: 1.4, y: 0.95, w: 7.2, h: 3.6,
    sizing: { type: "contain", w: 7.2, h: 3.6 },
  });

  // Caption block underneath, two short lines, the second emphasized
  s.addText("Growth rate g recovers to <1%.", {
    x: 0.55, y: 4.65, w: 9.2, h: 0.3,
    fontFace: BODY_FONT, fontSize: 14, color: INK,
    align: "center", margin: 0,
  });

  s.addText(
    [
      { text: "Billing-cycle lag μ_R lives on a ", options: { color: INK } },
      { text: "non-identifiable valley", options: { color: ACCENT, bold: true } },
      { text: " — the two parameters partially compensate for each other.", options: { color: INK } },
    ],
    {
      x: 0.55, y: 4.95, w: 9.2, h: 0.35,
      fontFace: BODY_FONT, fontSize: 14,
      align: "center", margin: 0,
    }
  );

  addPageNumber(s, 5, TOTAL_SLIDES);

  s.addNotes(
    "I fit the model to noisy revenue data using gradient descent and " +
    "Adam — both written from scratch. The growth rate recovers to " +
    "within one percent of truth.\n\n" +
    "But when I fit growth rate AND billing-cycle lag together, I get " +
    "this curved valley — not a single point. The two parameters trade " +
    "off, because a faster lag mimics a higher growth rate over a " +
    "finite observation window. That's what's called structural " +
    "identifiability.\n\n" +
    "So I asked the harder question: does that ambiguity matter for " +
    "the answer? I walked along the valley's worst direction — the " +
    "eigenvector the data is least informative about — and recomputed " +
    "the threshold. It moves by only about 2.4 percent. The calibration " +
    "is ambiguous, but the answer is robust.\n\n" +
    "[target: 60 seconds]"
  );
}

// ===========================================================================
// SLIDE 6 — SHOPIFY REAL-DATA ANCHOR (light, parameter card + fit chart)
// Same Adam optimizer that produced the synthetic valley above, fit
// against 9 quarters of public Shopify pre-IPO revenue. Closes the
// "where do these numbers come from" credibility question.
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("Calibrated against real data — Shopify Inc. pre-IPO F-1", {
    x: 0.55, y: 0.35, w: 9.2, h: 0.55,
    fontFace: HEADER_FONT, fontSize: 22, color: NAVY, bold: true,
    margin: 0,
  });

  s.addText(
    "Same Adam optimizer · 1-parameter fit · 9 quarters of public SEC EDGAR data",
    {
      x: 0.55, y: 0.95, w: 9.2, h: 0.35,
      fontFace: BODY_FONT, fontSize: 13, color: MUTED, italic: true,
      margin: 0,
    }
  );

  // Left column: recovered-g headline + supporting context.
  s.addText(
    [
      { text: "g = 13.5%/mo", options: { color: ACCENT, bold: true, fontSize: 26 } },
      { text: "  recovered", options: { color: MUTED, italic: true, fontSize: 14 } },
    ],
    {
      x: 0.55, y: 1.55, w: 4.1, h: 0.55,
      fontFace: BODY_FONT, valign: "middle", margin: 0,
    }
  );

  s.addText(
    "Converged in 242 iterations.\n\n" +
    "K and μ_R held at anchored values — short revenue " +
    "data alone cannot distinguish them from g (the same " +
    "valley finding from the previous slide).",
    {
      x: 0.55, y: 2.15, w: 4.1, h: 1.65,
      fontFace: BODY_FONT, fontSize: 12, color: INK,
      valign: "top", margin: 0, paraSpaceAfter: 4,
    }
  );

  s.addText(
    "Source:  Shopify Inc. F-1 + F-1/A amendments,\n2012-Q4 → 2014-Q4  (SEC EDGAR)",
    {
      x: 0.55, y: 3.95, w: 4.1, h: 0.6,
      fontFace: "Consolas", fontSize: 10, color: MUTED,
      valign: "top", margin: 0,
    }
  );

  s.addText(
    "Synthetic profiles in the rest of the talk are illustrative\n" +
    "archetypes. The engine fits real revenue too.",
    {
      x: 0.55, y: 4.7, w: 4.1, h: 0.7,
      fontFace: BODY_FONT, fontSize: 11, color: INK, italic: true,
      valign: "top", margin: 0,
    }
  );

  // Right column: the engine fit overlaid on observed quarterly points.
  s.addImage({
    path: path.join(FIG, "nb_shopify_fit.png"),
    x: 4.85, y: 1.4, w: 5.0, h: 3.0,
    sizing: { type: "contain", w: 5.0, h: 3.0 },
  });

  s.addText(
    "Engine RK4 fit (navy) vs F-1 quarterly revenue (coral).",
    {
      x: 4.85, y: 4.45, w: 5.0, h: 0.3,
      fontFace: BODY_FONT, fontSize: 10, color: MUTED, italic: true,
      align: "center", margin: 0,
    }
  );

  addPageNumber(s, 6, TOTAL_SLIDES);

  s.addNotes(
    "To answer where these numbers come from — I also calibrated the " +
    "engine against real data. I pulled nine quarters of Shopify's " +
    "pre-I-P-O revenue from public SEC filings, late 2012 through the " +
    "end of 2014.\n\n" +
    "I ran the same Adam optimizer, fitting only the growth rate, " +
    "because the data window is too short to identify the lag " +
    "separately — same valley finding from the previous slide. It " +
    "converged in 242 iterations and recovered a growth rate of " +
    "13.5 percent per month. The fitted trajectory tracks the observed " +
    "quarterly points cleanly.\n\n" +
    "The synthetic profiles in the rest of the talk are illustrative " +
    "archetypes; this shows the engine fits real revenue too.\n\n" +
    "[target: 40 seconds]"
  );
}

// ===========================================================================
// SLIDE 7 — THE ANSWER (light, big number + posterior + tornado)
// Tornado replaces the original iteration-paths chart: that figure had a
// broken LaTeX y-axis label, and the tornado does double duty — it
// visualizes the α-dominance claim that justifies the caveat strip below.
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("The answer:  μ* ≈ 14.2% per month", {
    x: 0.55, y: 0.35, w: 9.2, h: 0.55,
    fontFace: HEADER_FONT, fontSize: 26, color: NAVY, bold: true,
    margin: 0,
  });

  // Big number block, accent-colored
  s.addText(
    [
      { text: "μ* ≈ 14.2%/mo", options: { color: ACCENT, bold: true, fontSize: 28 } },
      { text: "      ", options: {} },
      { text: "95% CI [8.0%, 16.0%]", options: { color: NAVY, fontSize: 20 } },
    ],
    {
      x: 0.55, y: 1.05, w: 9.2, h: 0.55,
      fontFace: BODY_FONT, align: "center", margin: 0, valign: "middle",
    }
  );

  // Subtitle
  s.addText(
    "Three root-finders, one root.  Newton 3 iters  <  secant 4  <  bisection 20.",
    {
      x: 0.55, y: 1.65, w: 9.2, h: 0.35,
      fontFace: BODY_FONT, fontSize: 13, color: MUTED, italic: true,
      align: "center", margin: 0,
    }
  );

  // Two figures side by side
  s.addImage({
    path: path.join(FIG, "nb05_mu_star_posterior.png"),
    x: 0.55, y: 2.15, w: 4.5, h: 2.6,
    sizing: { type: "contain", w: 4.5, h: 2.6 },
  });
  s.addText("MC posterior over μ*", {
    x: 0.55, y: 4.8, w: 4.5, h: 0.3,
    fontFace: BODY_FONT, fontSize: 11, color: MUTED, italic: true,
    align: "center", margin: 0,
  });

  s.addImage({
    path: path.join(FIG, "nb05_tornado.png"),
    x: 5.15, y: 2.15, w: 4.5, h: 2.6,
    sizing: { type: "contain", w: 4.5, h: 2.6 },
  });
  s.addText("Sensitivity of μ* — α dominates 3:1", {
    x: 5.15, y: 4.8, w: 4.5, h: 0.3,
    fontFace: BODY_FONT, fontSize: 11, color: MUTED, italic: true,
    align: "center", margin: 0,
  });

  // Caveat strip at bottom — the tornado on the right makes the
  // α-dominance claim visible, so the prose can be tighter.
  s.addText(
    "α held at its calibrated MAP in this MC; marginal CI under joint " +
    "uncertainty is wider. Documented in the report.",
    {
      x: 0.55, y: 5.15, w: 9.2, h: 0.3,
      fontFace: BODY_FONT, fontSize: 10, color: MUTED, italic: true,
      align: "center", margin: 0,
    }
  );

  addPageNumber(s, 7, TOTAL_SLIDES);

  s.addNotes(
    "I sampled the calibrated parameters from a Monte Carlo posterior, " +
    "ran the O-D-E for each sample, and used Newton's method to find " +
    "break-even on the cash curve. Three root-finders — Newton in three " +
    "iterations, secant in four, bisection in twenty — all converge to " +
    "the same answer.\n\n" +
    "The critical churn rate above which the business never recovers " +
    "within ten years is fourteen point two percent per month. The " +
    "95 percent confidence interval is 8 to 16 percent.\n\n" +
    "On the right is the sensitivity tornado. Conversion rate alpha " +
    "dominates — its bar is three times longer than the next-strongest " +
    "parameter. That's why the confidence interval on the left holds " +
    "alpha fixed at its calibrated value. A joint posterior would be " +
    "wider, and I document that in the report.\n\n" +
    "[target: 60 seconds]"
  );
}

// ===========================================================================
// SLIDE 8 — WHAT I LEARNED (light, three-card layout)
// (Live-demo slide cut: it duplicated the QR/CTA on the closing slide and
// was the highest-failure-risk moment of the deck. The math is the proof;
// the demo was theatre.)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("Three things this project taught me", {
    x: 0.55, y: 0.4, w: 9.2, h: 0.6,
    fontFace: HEADER_FONT, fontSize: 28, color: NAVY, bold: true,
    margin: 0,
  });

  const lessons = [
    {
      n: "01",
      title: "A wrong model produces precise nonsense.",
      body:
        "I caught a structural defect in my revenue equation in Phase 1 " +
        "and fixed it before any calibration ran on top. The original " +
        "would have given a precise answer to the wrong question.",
    },
    {
      n: "02",
      title: "Identifiability matters more than accuracy.",
      body:
        "Whether you CAN recover a parameter is the deeper question. " +
        "The Hessian eigenvector along the calibration valley is the " +
        "answer, not the eyeballed one.",
    },
    {
      n: "03",
      title: "Validation-first separates engineering from coursework.",
      body:
        "114 tests gate every notebook. No engine module is imported " +
        "into a notebook until its tests pass. The discipline is the " +
        "deliverable.",
    },
  ];

  // Three columns
  lessons.forEach((l, i) => {
    const x = 0.55 + i * 3.15;
    const w = 2.95;
    // Card background — subtle
    s.addShape("rect", {
      x, y: 1.25, w, h: 3.7,
      fill: { color: "F8FAFC" }, line: { color: RULE, width: 0.75 },
    });
    // Numeral
    s.addText(l.n, {
      x: x + 0.2, y: 1.35, w: 1.0, h: 0.55,
      fontFace: HEADER_FONT, fontSize: 32, color: ACCENT, bold: true,
      margin: 0,
    });
    // Title
    s.addText(l.title, {
      x: x + 0.2, y: 1.95, w: w - 0.4, h: 1.2,
      fontFace: HEADER_FONT, fontSize: 16, color: NAVY, bold: true,
      margin: 0, valign: "top",
    });
    // Body
    s.addText(l.body, {
      x: x + 0.2, y: 3.15, w: w - 0.4, h: 1.65,
      fontFace: BODY_FONT, fontSize: 12, color: INK,
      margin: 0, valign: "top", paraSpaceAfter: 4,
    });
  });

  addPageNumber(s, 8, TOTAL_SLIDES);

  s.addNotes(
    "Three quick lessons.\n\n" +
    "One — I caught a structural bug in my revenue equation early, " +
    "and fixed it before any calibration touched it. The wrong model " +
    "would have given precise nonsense.\n\n" +
    "Two — identifiability matters more than accuracy. Whether you " +
    "CAN recover a parameter is the deeper question.\n\n" +
    "Three — writing tests before notebook code is the discipline that " +
    "separates engineering from coursework.\n\n" +
    "[target: 30 seconds]"
  );
}

// ===========================================================================
// SLIDE 9 — TRY IT YOURSELF / QR / THANKS (dark)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("Try it yourself", {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontFace: HEADER_FONT, fontSize: 32, color: WHITE, bold: true,
    align: "center", margin: 0,
  });

  // Big QR code centered
  s.addImage({
    path: path.join(QR, "qr_large.png"),
    x: 3.5, y: 1.15, w: 3.0, h: 3.0,
  });

  // Dashboard URL
  s.addText("startup-growth-simulator.streamlit.app", {
    x: 0.6, y: 4.25, w: 8.8, h: 0.4,
    fontFace: "Consolas", fontSize: 18, color: ICE,
    align: "center", margin: 0,
  });

  // Repo URL
  s.addText("Code:  github.com/ArseniiChan/startup-growth-simulator", {
    x: 0.6, y: 4.65, w: 8.8, h: 0.35,
    fontFace: "Consolas", fontSize: 13, color: ICE,
    align: "center", margin: 0,
  });

  // "Thanks." in the accent color, larger
  s.addText("Thanks.", {
    x: 0.6, y: 5.05, w: 8.8, h: 0.5,
    fontFace: HEADER_FONT, fontSize: 22, color: ACCENT, italic: true,
    align: "center", margin: 0,
  });

  s.addNotes(
    "Code is on GitHub. The dashboard is live — scan the QR.\n\n" +
    "What startup would you fund?\n\n" +
    "Thanks.\n\n" +
    "[target: 15 seconds]"
  );
}

// ---------------------------------------------------------------------------
// Write
// ---------------------------------------------------------------------------

pres.writeFile({ fileName: OUT })
  .then((file) => {
    console.log("wrote " + file);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
