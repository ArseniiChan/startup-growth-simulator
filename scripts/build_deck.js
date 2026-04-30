// Build the 9-slide CSC 30100 final-project presentation deck.
// Output: report/presentation.pptx (sibling figures live in report/figures/, QR in report/qr/)
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
const OUT = path.join(REPO, "report", "presentation.pptx");

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
    "Hi, I'm Arsenii. For my CSC 30100 final I built a startup-survival " +
    "threshold calculator from scratch — and I want to walk you through " +
    "what it found. " +
    "[10 seconds]"
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
    "Every venture capitalist looks at a startup and tries to answer one " +
    "question: will this company survive? You can answer that with " +
    "intuition, or you can answer it with math. I built the math. " +
    "Here's the result. Take a typical software-as-a-service startup — " +
    "reasonable growth, reasonable conversion, reasonable costs. There is " +
    "a single number — the rate at which paying users cancel each month — " +
    "above which the company runs out of money before it can ever recover, " +
    "within a 10-year horizon. For our default profile that number is " +
    "about 14 percent. Below 14 percent monthly churn, the company " +
    "survives. Above 14, it doesn't. I want to show you how I found it, " +
    "and how confident I am in the answer. " +
    "[40 seconds]"
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

  // Equations as a multi-line text block in a monospace font
  const eqLines = [
    { text: "dU/dt    = g · U · (1 − U/K)",
      options: { breakLine: true } },
    { text: "             logistic acquisition",
      options: { color: MUTED, italic: true, fontSize: 14, breakLine: true } },
    { text: "dA/dt    = α · g · U · (1 − U/K) − μ · A",
      options: { breakLine: true } },
    { text: "             conversion − churn",
      options: { color: MUTED, italic: true, fontSize: 14, breakLine: true } },
    { text: "dR/dt    = μ_R · (p · A − R)",
      options: { breakLine: true } },
    { text: "             billing-cycle lag toward p·A",
      options: { color: MUTED, italic: true, fontSize: 14, breakLine: true } },
    { text: "dCash/dt = R − F − v · g · U · (1 − U/K)",
      options: { breakLine: true } },
    { text: "             revenue − costs",
      options: { color: MUTED, italic: true, fontSize: 14 } },
  ];
  s.addText(eqLines, {
    x: 0.55, y: 1.45, w: 5.6, h: 3.5,
    fontFace: "Consolas", fontSize: 17, color: INK,
    valign: "top", margin: 0,
  });

  // Inset: default trajectory figure (shrunken)
  s.addImage({
    path: path.join(FIG, "nb01_default_trajectory.png"),
    x: 6.3, y: 1.5, w: 3.5, h: 2.2,
    sizing: { type: "contain", w: 3.5, h: 2.2 },
  });
  s.addText("Default-SaaS trajectory, 60 months (RK4)", {
    x: 6.3, y: 3.75, w: 3.5, h: 0.3,
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
    "I modeled a startup as four coupled differential equations on users, " +
    "paying users, revenue, and cash. Users follow logistic acquisition. " +
    "Paying users are conversion minus churn. Revenue lags the paying-user " +
    "base — what I call the billing-cycle lag, capturing annual contracts " +
    "and deferred recognition. Cash is revenue minus fixed and variable " +
    "costs. The whole system runs on eight parameters that a VC can " +
    "estimate from public data: growth rate, market size, ARPU, churn, " +
    "costs. The inset on the right shows the default-SaaS profile " +
    "integrated for 60 months — the canonical S-curve in users, the " +
    "lagged revenue catching up, the cash trajectory dipping before it " +
    "recovers. " +
    "[50 seconds]"
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
    "I implemented all five ODE solvers from scratch — no SciPy. Each " +
    "method matches its theoretical convergence order to within 4 percent. " +
    "Euler at slope 1, Heun at slope 2, the three 4th-order methods at " +
    "slope 4. The lines you see on this log-log plot are the proof. " +
    "Without this slide, every number downstream is a guess. This is the " +
    "contract everything else rests on. " +
    "[45 seconds]"
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

  // Hero figure — give it most of the slide
  s.addImage({
    path: path.join(FIG, "nb03_loss_surface_2param.png"),
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
    "I fit the model to noisy revenue data using gradient descent and Adam " +
    "— both implemented from scratch. The growth rate g recovers to within " +
    "one percent of truth. But fitting growth rate AND billing-cycle lag " +
    "together produces this valley — not a point. The two parameters trade " +
    "off because a faster lag mimics a higher growth rate over a finite " +
    "window. This is what's called structural identifiability. I asked the " +
    "harder question: does that ambiguity matter for the answer? I computed " +
    "the smallest-eigenvalue eigenvector of the calibration loss Hessian — " +
    "that's the direction the data is least informative about — and " +
    "recomputed the survival threshold along it. The threshold varies by " +
    "about 2.4 percent along the worst direction. Even though the " +
    "calibration is ambiguous, the answer it produces is meaningfully " +
    "robust to that ambiguity. " +
    "[60 seconds]"
  );
}

// ===========================================================================
// SLIDE 6 — THE ANSWER (light, big number + two figures)
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
    path: path.join(FIG, "nb05_iteration_paths.png"),
    x: 5.15, y: 2.15, w: 4.5, h: 2.6,
    sizing: { type: "contain", w: 4.5, h: 2.6 },
  });
  s.addText("Newton vs bisection vs secant", {
    x: 5.15, y: 4.8, w: 4.5, h: 0.3,
    fontFace: BODY_FONT, fontSize: 11, color: MUTED, italic: true,
    align: "center", margin: 0,
  });

  // Caveat strip at bottom
  s.addText(
    "Caveat: CI conditions on α at its calibrated MAP; α is the dominant " +
    "sensitivity, so the marginal CI is wider. Documented in the report.",
    {
      x: 0.55, y: 5.15, w: 9.2, h: 0.3,
      fontFace: BODY_FONT, fontSize: 10, color: MUTED, italic: true,
      align: "center", margin: 0,
    }
  );

  addPageNumber(s, 6, TOTAL_SLIDES);

  s.addNotes(
    "I sampled the calibrated parameters from their Monte Carlo posterior, " +
    "ran the ODE for each sample, and used Newton's method to find " +
    "break-even on the cash curve. Three root-finders — Newton in 3 " +
    "iterations, secant in 4, bisection in 20 — all converge to the same " +
    "answer. The critical churn rate above which the business never " +
    "recovers within ten years is fourteen point two percent per month. " +
    "The 95 percent confidence interval is 8 to 16 percent. One important " +
    "caveat — and this matters for honest scientific reporting — the " +
    "conversion rate alpha is held at its calibrated value in this Monte " +
    "Carlo. Alpha is actually the dominant sensitivity, so the marginal CI " +
    "under joint uncertainty is wider. I document this in the report. " +
    "[60 seconds]"
  );
}

// ===========================================================================
// SLIDE 7 — LIVE DEMO (dark, mostly empty + small QR)
// ===========================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Big "LIVE DEMO" callout
  s.addText("Live demo", {
    x: 0.6, y: 1.0, w: 8.8, h: 1.0,
    fontFace: HEADER_FONT, fontSize: 56, color: WHITE,
    bold: true, align: "center", valign: "middle", margin: 0,
  });

  s.addText("startup-growth-simulator.streamlit.app", {
    x: 0.6, y: 2.05, w: 8.8, h: 0.4,
    fontFace: "Consolas", fontSize: 18, color: ICE,
    align: "center", valign: "middle", margin: 0,
  });

  // Center accent rule
  s.addShape("rect", {
    x: 4.4, y: 2.6, w: 1.2, h: 0.02,
    fill: { color: ACCENT }, line: { color: ACCENT, width: 0 },
  });

  // Audience-instruction text below the rule
  s.addText(
    "Scan to follow along on your phone — or watch on the projector.",
    {
      x: 0.6, y: 2.75, w: 8.8, h: 0.4,
      fontFace: BODY_FONT, fontSize: 14, color: ICE, italic: true,
      align: "center", margin: 0,
    }
  );

  // Small QR code in bottom-left
  s.addImage({
    path: path.join(QR, "qr_small.png"),
    x: 0.4, y: 3.4, w: 1.6, h: 1.6,
  });
  s.addText("scan", {
    x: 0.4, y: 5.0, w: 1.6, h: 0.3,
    fontFace: BODY_FONT, fontSize: 11, color: ICE,
    align: "center", margin: 0,
  });

  // Tiny backup hint at bottom (presenter-only, very small)
  s.addText(
    "If demo unresponsive: switch to slide 10 (offline backup); audience " +
    "scans QR on their phones.",
    {
      x: 2.2, y: 5.05, w: 7.5, h: 0.3,
      fontFace: BODY_FONT, fontSize: 9, color: MUTED, italic: true,
      align: "left", margin: 0,
    }
  );

  s.addNotes(
    "Let me show you the dashboard. Switch to the browser tab where the " +
    "Streamlit app is already loaded. " +
    "I can pick a startup profile — let's start with early-stage SaaS. " +
    "Wait for trajectory to render. " +
    "Now I drag the churn slider from three to eight percent — watch the " +
    "cash curve flip from recovering to terminal. The runway-dies marker " +
    "moves from intact to month 18. " +
    "Now I jump to the Monte Carlo panel — this runs a thousand simulations " +
    "of the model under parameter uncertainty. Click the Monte Carlo tab, " +
    "click Run. " +
    "The histogram is the distribution of terminal valuations. P-of-unicorn " +
    "is essentially zero for this profile, which is the honest answer. " +
    "Now jump to the break-even tab — same number my slide just showed, " +
    "mu-star equals 14.17 percent, computed live by three different " +
    "root-finders that all agree. " +
    "Last tab — sensitivity. I select mu-star from the dropdown and click " +
    "compute. About 12 seconds wait — fill with: this runs the same " +
    "finite-difference computations my slide deck used. There's the " +
    "tornado — alpha at the top, exactly as I claimed. " +
    "[BACKUP if Streamlit fails: jump to slide 10, narrate over the " +
    "screenshot, audience can still scan the QR.] " +
    "[90 seconds]"
  );
}

// ===========================================================================
// SLIDE 8 — WHAT I LEARNED (light, three-card layout)
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
    "Three quick lessons. One — I caught a structural bug in my revenue " +
    "equation early and fixed it before any calibration touched it; the " +
    "wrong model would have produced precise nonsense. Two — " +
    "identifiability matters more than accuracy; whether you CAN recover " +
    "a parameter is the deeper question. Three — writing tests before " +
    "notebook code is the discipline that separates engineering from " +
    "coursework. " +
    "[30 seconds]"
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
    "Code is on GitHub, dashboard is live, scan the QR code — what " +
    "startup would you fund? Thanks. " +
    "[15 seconds]"
  );
}

// ===========================================================================
// SLIDE 10 — HIDDEN BACKUP IF LIVE DEMO FAILS
// ===========================================================================
{
  const s = pres.addSlide();
  s.hidden = true;
  s.background = { color: WHITE };
  addAccentBar(s);

  s.addText("Demo (offline backup)", {
    x: 0.55, y: 0.35, w: 9.2, h: 0.55,
    fontFace: HEADER_FONT, fontSize: 24, color: NAVY, bold: true,
    margin: 0,
  });

  s.addText(
    "Hidden slide — used only if startup-growth-simulator.streamlit.app " +
    "is unresponsive during the live demo. Same script as slide 7, but " +
    "narrated over this static screenshot.",
    {
      x: 0.55, y: 0.95, w: 9.2, h: 0.55,
      fontFace: BODY_FONT, fontSize: 12, color: MUTED, italic: true,
      margin: 0,
    }
  );

  // Use the default trajectory as the screenshot stand-in
  s.addImage({
    path: path.join(FIG, "nb01_default_trajectory.png"),
    x: 1.0, y: 1.6, w: 8.0, h: 3.6,
    sizing: { type: "contain", w: 8.0, h: 3.6 },
  });

  s.addText(
    "Audience can still scan the QR on slide 7 to try the dashboard on their phones — " +
    "I'll narrate the same demo over this image.",
    {
      x: 0.55, y: 5.3, w: 9.2, h: 0.3,
      fontFace: BODY_FONT, fontSize: 10, color: MUTED, italic: true,
      align: "center", margin: 0,
    }
  );

  s.addNotes(
    "HIDDEN SLIDE — do not advance to this in a successful demo. " +
    "Only used if the live Streamlit app is unresponsive. Narrate the same " +
    "demo script as slide 7 over this static dashboard screenshot. The " +
    "audience can still scan the QR code from slide 7 to try the live " +
    "dashboard on their own phones. The numbers (μ*=14.17%, 95% CI " +
    "[8.0%, 16.0%], P(unicorn)=0% for default-SaaS) were already on " +
    "slides 5 and 6 — emphasize that the live demo would have shown the " +
    "same numbers reproducing live, but the math is independent of the UI."
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
