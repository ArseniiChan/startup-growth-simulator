/**
 * The single landing-page route.
 *
 * Structure — six sections, each one earning its presence:
 *   1. Hero               — the headline (Option B), the number, two CTAs.
 *   2. What is this?      — for classmates with no VC experience. Plain English.
 *   3. The math           — for the Burden professor. Three sentences, named.
 *   4. The valley         — the project's structural-identifiability finding.
 *   5. What I learned     — three takeaways (mirrors slide 8 of the deck).
 *   6. Footer             — author, course, repo, dashboard, mu* in print.
 *
 * Editorial Navy palette per Phase 4 council verdict:
 *   - Background pure white
 *   - Ink #0F172A (slate-900) for primary text
 *   - Muted #475569 (slate-600) for captions and "survives" duotone
 *   - Accent #DC2626 (red-600) reserved for: the 14.2% glyph, the
 *     failure-mode callout, and the primary CTA. Nothing else.
 */

import Image from "next/image";

const DASHBOARD_URL = "https://startup-growth-simulator.streamlit.app";
const REPO_URL = "https://github.com/ArseniiChan/startup-growth-simulator";

// External-link arrow used on every outbound link. Inline SVG so we don't
// pull a whole icon library for a single glyph.
function ArrowOut({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 12 12"
      aria-hidden="true"
      className={`inline-block h-3 w-3 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 9 L9 3 M4 3 H9 V8" />
    </svg>
  );
}

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 pb-24 pt-16 sm:px-8 sm:pt-24">
      {/* ───────────────────────────────────────────────────────────────
          1. HERO
          ──────────────────────────────────────────────────────────── */}
      <header className="mb-24 sm:mb-32">
        {/* Eyebrow — uppercase tracking-wider, the AirAware register */}
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
          Numerical Analysis · CSC 30100 · Spring 2026
        </p>

        {/* The headline — Option B, locked. Tracking-tightest is editorial. */}
        <h1 className="mt-6 text-balance text-4xl font-semibold leading-[1.05] tracking-tightest text-ink sm:text-[56px]">
          The exact monthly user-churn rate above which{" "}
          <span className="text-muted">no amount of growth</span> saves the
          business.
        </h1>

        {/* Hero number block — duotone (red glyph + slate-600 CI) per First
            Principles' insight. JetBrains Mono on the number itself. */}
        <div className="mt-10 flex flex-col gap-2 sm:flex-row sm:items-baseline sm:gap-6">
          <div className="font-mono text-7xl font-bold leading-none tracking-tight text-accent sm:text-8xl">
            14.2<span className="text-5xl sm:text-6xl">%</span>
          </div>
          <div className="font-mono text-base text-muted">
            <div>per month, default-SaaS profile</div>
            <div>95% CI [8.0%, 16.0%]</div>
          </div>
        </div>

        {/* CTAs — primary navy button + ghost link. Restraint per RUI. */}
        <div className="mt-12 flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
          <a
            href={DASHBOARD_URL}
            target="_blank"
            rel="noreferrer"
            className="group inline-flex items-center justify-center gap-2 rounded-md bg-ink px-6 py-3 text-sm font-semibold text-white transition hover:bg-ink/90 focus:outline-none focus:ring-2 focus:ring-ink focus:ring-offset-2"
          >
            Launch the live tool
            <ArrowOut className="opacity-70 transition group-hover:translate-x-0.5 group-hover:opacity-100" />
          </a>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-md px-3 py-3 text-sm font-medium text-muted transition hover:text-ink"
          >
            Read the code
            <ArrowOut />
          </a>
        </div>

        {/* Micro-text under CTAs — sets expectation for click-through */}
        <p className="mt-4 text-xs text-muted">
          Live dashboard runs the engine in your browser. ~12s for a Monte
          Carlo run; everything else is instant.
        </p>
      </header>

      {/* ───────────────────────────────────────────────────────────────
          2. WHAT IS THIS?
          ──────────────────────────────────────────────────────────── */}
      <section className="mb-24 sm:mb-32">
        <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
          What this is, in plain English
        </h2>
        <div className="mt-5 space-y-5 text-lg leading-relaxed text-ink">
          <p>
            Every venture capitalist looks at a startup and tries to answer
            one question:{" "}
            <span className="font-semibold">will this company survive?</span>{" "}
            You can answer with intuition, or you can answer with math. I
            built the math.
          </p>
          <p>
            For a typical software-as-a-service startup — reasonable growth,
            reasonable conversion, reasonable costs — there is a single
            number. The monthly rate at which paying users cancel. Below it,
            the company survives a 10-year horizon. Above it, the runway
            runs out before the trajectory ever recovers. For our default
            profile that number is{" "}
            <span className="font-semibold text-accent">about 14%</span> per
            month, with calibration uncertainty putting the 95% interval at{" "}
            <span className="font-mono text-muted">[8%, 16%]</span>.
          </p>
        </div>
      </section>

      {/* ───────────────────────────────────────────────────────────────
          3. THE MATH (one paragraph, named)
          ──────────────────────────────────────────────────────────── */}
      <section className="mb-24 sm:mb-32">
        <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
          The math, briefly
        </h2>
        <div className="mt-5 space-y-5 text-base leading-relaxed text-ink">
          <p>
            A four-dimensional ODE on (Users, Active subscribers, Revenue,
            Cash) with logistic acquisition and a billing-cycle-lag revenue
            equation, solved with five from-scratch ODE methods (Euler, Heun,
            RK4, Adams-Bashforth-4, Adams-Moulton predictor-corrector).
            Calibrated against noisy quarterly revenue with from-scratch
            gradient descent and Adam. The threshold μ* is the root of
            terminal cash, found by Newton, bisection, and secant
            (3 / 14 / 4 iterations respectively — exactly the textbook
            ordering). The confidence interval comes from a Monte Carlo
            posterior over the calibrated parameters with Kahan-summed
            estimators and antithetic variates.
          </p>
          <p className="text-sm text-muted">
            Every method here is implemented from scratch — Burden et&nbsp;al.,
            chapter by chapter. No SciPy.{" "}
            <span className="text-ink">114 unit tests.</span> Validation-first:
            no engine module is imported by a notebook until its tests pass.
          </p>
        </div>
      </section>

      {/* ───────────────────────────────────────────────────────────────
          4. THE VALLEY (the structural-identifiability finding)
          ──────────────────────────────────────────────────────────── */}
      <section className="mb-24 sm:mb-32">
        <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
          The result I'm proudest of
        </h2>
        <h3 className="mt-5 text-2xl font-semibold leading-tight tracking-tight text-ink sm:text-3xl">
          A direction in parameter space the data can't distinguish — and a
          proof the answer is robust to it.
        </h3>

        <figure className="mt-8">
          <div className="overflow-hidden rounded-md border border-rule">
            <Image
              src="/figures/valley.png"
              alt="Loss-surface contour plot showing a curved valley in (g, μ_R) parameter space — the calibration cannot separately identify the two parameters."
              width={1200}
              height={800}
              priority
              className="h-auto w-full"
            />
          </div>
          <figcaption className="mt-4 text-sm leading-relaxed text-muted">
            Loss surface for the calibrated parameters (growth rate{" "}
            <span className="font-mono text-ink">g</span>, billing-cycle lag{" "}
            <span className="font-mono text-ink">μ_R</span>). The fit is a
            curved valley, not a single best-fit point — the two parameters
            partially compensate for each other over a finite observation
            window. So I asked: does that ambiguity matter for the answer? I
            computed the smallest-eigenvalue eigenvector of the calibration
            loss Hessian (the direction the data is least informative about)
            and walked the threshold along it.{" "}
            <span className="text-ink">μ* varies by 2.4%.</span>{" "}
            Even though the calibration is ambiguous, the answer is robust to
            the ambiguity. That's a structural-identifiability finding.
          </figcaption>
        </figure>
      </section>

      {/* ───────────────────────────────────────────────────────────────
          5. WHAT I LEARNED — three cards, mirrors slide 8 of the deck
          ──────────────────────────────────────────────────────────── */}
      <section className="mb-24 sm:mb-32">
        <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
          Three things this taught me
        </h2>
        <ol className="mt-8 grid gap-10 sm:grid-cols-3 sm:gap-8">
          {[
            {
              n: "01",
              title: "A wrong model produces precise nonsense.",
              body:
                "I caught a structural defect in the revenue equation in week two and fixed it before any calibration ran on top of it. The original would have produced a precise answer to the wrong question.",
            },
            {
              n: "02",
              title: "Identifiability matters more than accuracy.",
              body:
                "Whether you can recover a parameter is the deeper question. The Hessian eigenvector along the calibration valley is the answer — not the eyeballed direction.",
            },
            {
              n: "03",
              title: "Validation-first separates engineering from coursework.",
              body:
                "114 tests gate every notebook. No engine module enters a notebook until its tests pass. The discipline is the deliverable.",
            },
          ].map((l) => (
            <li key={l.n} className="flex flex-col gap-3">
              <span className="font-mono text-sm font-semibold text-accent">
                {l.n}
              </span>
              <h3 className="text-base font-semibold leading-snug text-ink">
                {l.title}
              </h3>
              <p className="text-sm leading-relaxed text-muted">{l.body}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* ───────────────────────────────────────────────────────────────
          6. FOOTER — author + links + the dashboard CTA in writing
          ──────────────────────────────────────────────────────────── */}
      <footer className="border-t border-rule pt-12">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-end sm:justify-between sm:gap-12">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
              Try it yourself
            </p>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-ink">
              The dashboard runs the same engine you just read about: solve
              the ODE for any parameter set, compute μ* live with three
              root-finders, and watch the cash curve flip from recovery to
              terminal as you drag the churn slider.
            </p>
            <a
              href={DASHBOARD_URL}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex items-center gap-2 rounded-md bg-accent px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
            >
              Launch dashboard
              <ArrowOut />
            </a>
          </div>

          <div className="flex flex-col gap-2 text-xs text-muted sm:items-end">
            <p className="text-ink">Arsenii Chan</p>
            <p>CSC 30100, Spring 2026</p>
            <p>City College of New York</p>
            <div className="mt-3 flex gap-4">
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="transition hover:text-ink"
              >
                GitHub <ArrowOut />
              </a>
              <a
                href={DASHBOARD_URL}
                target="_blank"
                rel="noreferrer"
                className="transition hover:text-ink"
              >
                Dashboard <ArrowOut />
              </a>
            </div>
          </div>
        </div>

        <p className="mt-12 text-[11px] leading-relaxed text-muted">
          μ* is the runway-survival threshold at T=120 months — the smallest
          monthly user-churn rate at which the default-SaaS profile ends the
          horizon cash-negative. Reported CI conditions on the conversion
          rate α at its calibrated MAP (α has the dominant sensitivity, so
          the marginal CI under joint uncertainty is wider). Full
          documentation in the report.
        </p>
      </footer>
    </main>
  );
}
