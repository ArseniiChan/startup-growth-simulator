/**
 * Single-route scrollytelling dashboard. The Streamlit app is deprecated as
 * the primary surface; everything lives here on Vercel as a unified Next.js
 * experience. Editorial Navy palette throughout.
 *
 * Section order (top-down narrative):
 *
 *   1. Top nav (full-bleed, anchors viewport edges)
 *   2. Hero (the headline, the 14.2%, two CTAs that scroll-to-section)
 *   3. The question, in plain English (for classmates with no VC background)
 *   4. Live exploration — TrajectoryChart with profile chips (interactive #1)
 *   5. The math, briefly (for the Burden professor)
 *   6. Calibration — the valley contour (the structural-identifiability finding)
 *   7. The headline answer — μ* slider (interactive #2 — the marquee interaction)
 *   8. Confidence — Monte Carlo posterior histogram
 *   9. Sensitivity — tornado bars
 *  10. Three lessons
 *  11. Footer band
 *
 * Visitors who want raw exploration can click the small footer link to the
 * Streamlit app — but the canonical experience is this one continuous page.
 */

import { TrajectoryChart } from "@/components/TrajectoryChart";
import { MuStarSlider } from "@/components/MuStarSlider";
import { ValleyContour } from "@/components/ValleyContour";
import { PosteriorHistogram } from "@/components/PosteriorHistogram";
import { TornadoChart } from "@/components/TornadoChart";
import { VcInsights } from "@/components/VcInsights";
import { Reveal } from "@/components/Reveal";

const REPO_URL = "https://github.com/ArseniiChan/startup-growth-simulator";
const STREAMLIT_URL = "https://startup-growth-simulator.streamlit.app";

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

export default function Page() {
  return (
    <div className="flex min-h-screen flex-col bg-white text-ink">
      {/* ───────────────────────────────────────────────────────────
          NAV — full-bleed, sticky on scroll for in-page anchors
          ──────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-40 border-b border-rule bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10">
          <a href="#hero" className="flex items-baseline gap-3 text-sm font-semibold text-ink">
            <span className="font-mono text-accent">μ*</span>
            <span>Startup Growth</span>
            <span className="hidden text-xs font-normal text-muted md:inline">
              · CSC 30100 · Spring 2026
            </span>
          </a>
          <div className="flex items-center gap-2 text-sm font-medium sm:gap-5">
            <a
              href="#explore"
              className="hidden text-muted transition hover:text-ink sm:inline"
            >
              Explore
            </a>
            <a
              href="#answer"
              className="hidden text-muted transition hover:text-ink sm:inline"
            >
              The answer
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="hidden text-muted transition hover:text-ink md:inline"
            >
              GitHub <ArrowOut className="ml-0.5" />
            </a>
            <a
              href="#answer"
              className="rounded-md bg-ink px-3.5 py-1.5 text-xs font-semibold text-white transition hover:bg-ink/90"
            >
              See μ*
            </a>
          </div>
        </div>
      </nav>

      <main className="flex-1">
        {/* ─────────────────────────────────────────────────────────
            1. HERO
            ────────────────────────────────────────────────────── */}
        <section id="hero" className="border-b border-rule">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-32">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
              Numerical Analysis · Final Project
            </p>
            <h1 className="mt-6 max-w-5xl text-balance text-[40px] font-semibold leading-[1.04] tracking-tightest text-ink sm:text-6xl lg:text-7xl">
              The exact monthly user-churn rate above which{" "}
              <span className="text-muted">no amount of growth</span> saves the
              business.
            </h1>

            <div className="mt-12 flex flex-col gap-3 sm:flex-row sm:items-baseline sm:gap-10">
              <div className="font-mono text-[80px] font-bold leading-none tracking-tight text-accent sm:text-[120px]">
                14.2<span className="text-[56px] sm:text-[80px]">%</span>
              </div>
              <div className="font-mono text-base leading-relaxed text-muted">
                <div>per month, default-SaaS profile</div>
                <div>95% CI [8.0%, 16.0%]</div>
                <div className="mt-2 text-xs text-ink">
                  10-year horizon · 114 unit tests · no SciPy
                </div>
              </div>
            </div>

            <div className="mt-14 flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
              <a
                href="#answer"
                className="group inline-flex items-center justify-center gap-2 rounded-md bg-ink px-7 py-3.5 text-sm font-semibold text-white transition hover:bg-ink/90"
              >
                See the answer move
                <ArrowOut className="opacity-70 transition group-hover:translate-x-0.5 group-hover:opacity-100" />
              </a>
              <a
                href="#explore"
                className="inline-flex items-center justify-center gap-2 rounded-md px-3 py-3 text-sm font-medium text-muted transition hover:text-ink"
              >
                Or start with the model
                <ArrowOut />
              </a>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            2. PLAIN ENGLISH
            ────────────────────────────────────────────────────── */}
        <section id="explainer" className="border-b border-rule bg-cream">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <div className="grid gap-12 lg:grid-cols-[1fr_2fr] lg:gap-20">
              <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted lg:sticky lg:top-24 lg:self-start">
                What this is, in plain English
              </h2>
              <div className="max-w-2xl space-y-5 text-lg leading-relaxed text-ink">
                <p>
                  Every venture capitalist looks at a startup and tries to
                  answer one question:{" "}
                  <span className="font-semibold">will this company survive?</span>{" "}
                  You can answer that with intuition, or you can answer it
                  with math. I built the math.
                </p>
                <p>
                  For a typical software-as-a-service startup — reasonable
                  growth, reasonable conversion, reasonable costs — there is
                  a single number. The monthly rate at which paying users
                  cancel. Below it, the company survives a 10-year horizon.
                  Above it, the runway runs out before the trajectory ever
                  recovers. For our default profile that number is{" "}
                  <span className="font-semibold text-accent">about 14%</span>{" "}
                  per month, with calibration uncertainty putting the 95%
                  interval at{" "}
                  <span className="font-mono text-muted">[8%, 16%]</span>.
                </p>
                <p className="text-sm text-muted">
                  Below: the 4-dimensional ODE I built. Pick a startup
                  profile to watch the trajectory unfold. Then drag the
                  churn rate to find the survival threshold for yourself.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            3. EXPLORE — TrajectoryChart (interactive #1)
            ────────────────────────────────────────────────────── */}
        <section id="explore" className="border-b border-rule bg-white">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <Reveal>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                The model
              </p>
              <h2 className="mt-5 max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">
                A 4D ODE on Users, Active subscribers, Revenue, and Cash.
              </h2>
              <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted">
                Logistic acquisition, conversion, churn, billing-cycle lag,
                fixed and variable costs. Solved with five from-scratch ODE
                methods (Euler, Heun, RK4, Adams-Bashforth-4, Adams-Moulton
                predictor-corrector). Pick a profile to see the trajectory.
              </p>
            </Reveal>

            <Reveal delay={0.1}>
              <div className="mt-12">
                <TrajectoryChart />
              </div>
            </Reveal>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            4. THE MATH, BRIEFLY
            ────────────────────────────────────────────────────── */}
        <section className="border-b border-rule bg-cream">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <div className="grid gap-12 lg:grid-cols-[1fr_2fr] lg:gap-20">
              <h2 className="text-xs font-semibold uppercase tracking-[0.22em] text-muted lg:sticky lg:top-24 lg:self-start">
                The math, briefly
              </h2>
              <div className="max-w-2xl space-y-5 text-base leading-relaxed text-ink">
                <p>
                  Calibrated against noisy quarterly revenue with from-scratch
                  gradient descent and Adam. The threshold μ* is the root of
                  terminal cash, found by Newton, bisection, and secant
                  (3 / 14 / 4 iterations respectively — exactly the textbook
                  ordering). The confidence interval comes from a Monte Carlo
                  posterior over the calibrated parameters, computed with
                  Kahan-summed estimators and antithetic variates.
                </p>
                <p className="text-sm text-muted">
                  Every method here is implemented from scratch — Burden et
                  al., chapter by chapter.{" "}
                  <span className="text-ink">No SciPy.</span>{" "}
                  <span className="text-ink">114 unit tests.</span>{" "}
                  Validation-first: no engine module enters a notebook until
                  its tests pass.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            5. CALIBRATION — the valley
            ────────────────────────────────────────────────────── */}
        <section id="valley" className="border-b border-rule bg-white">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <Reveal>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                The result I'm proudest of
              </p>
              <h2 className="mt-5 max-w-4xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl lg:text-5xl">
                A direction in parameter space the data can't distinguish — and
                a proof the answer is robust to it.
              </h2>
            </Reveal>

            <div className="mt-12 grid gap-10 lg:grid-cols-[3fr_2fr] lg:items-start lg:gap-16">
              <div>
                <ValleyContour />
              </div>
              <div className="max-w-md text-base leading-relaxed text-ink lg:sticky lg:top-24">
                <p>
                  The fit is a curved valley, not a single best-fit point. The
                  growth rate <span className="font-mono">g</span> and the
                  billing-cycle lag <span className="font-mono">μ_R</span>{" "}
                  partially compensate for each other over a finite
                  observation window — a faster lag mimics a higher growth
                  rate, and the data can't tell them apart.
                </p>
                <p className="mt-4 text-sm text-muted">
                  Does that ambiguity matter for the answer? I computed the
                  smallest-eigenvalue eigenvector of the calibration loss
                  Hessian — the direction the data is least informative
                  about — and walked the threshold along it.{" "}
                  <span className="text-ink">μ* varies by 2.4%.</span> Even
                  though the calibration is ambiguous, the answer is robust
                  to the ambiguity. That is a structural-identifiability
                  finding.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            6. THE ANSWER — μ* slider (interactive #2)
            ────────────────────────────────────────────────────── */}
        <section id="answer" className="border-b border-rule bg-cream">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <Reveal>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
                Drive the threshold
              </p>
              <h2 className="mt-5 max-w-4xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl lg:text-5xl">
                Drag the churn rate. Watch the company live or die.
              </h2>
              <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted">
                For each value of monthly churn, the cash balance at the end of
                the 10-year horizon is precomputed from the 4D ODE. The dashed
                line is the runway-survival threshold μ*: above it, every
                parameter setting we tested ends with the company cash-negative.
              </p>
            </Reveal>

            <Reveal delay={0.1}>
              <div className="mt-12">
                <MuStarSlider />
              </div>
            </Reveal>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            7. VC INSIGHTS — dark navy band, the "stop and read" moment
            after the marquee finding has just landed.
            ────────────────────────────────────────────────────── */}
        <VcInsights />

        {/* ─────────────────────────────────────────────────────────
            8. CONFIDENCE — MC posterior
            ────────────────────────────────────────────────────── */}
        <section id="confidence" className="border-b border-rule bg-white">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
              How confident
            </p>
            <h2 className="mt-5 max-w-4xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">
              Sample the calibrated parameters, refit μ* on each draw, look at
              the spread.
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted">
              The 95% credible interval on μ* comes from this posterior:
              draw (g, μ_R) from their calibration distribution, run a fresh
              bisection to find μ*, repeat. The mean lands within 0.6% of the
              point estimate.
            </p>

            <div className="mt-12">
              <PosteriorHistogram />
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            8. SENSITIVITY — tornado
            ────────────────────────────────────────────────────── */}
        <section id="sensitivity" className="border-b border-rule bg-cream">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
              Which parameter moves the threshold
            </p>
            <h2 className="mt-5 max-w-4xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">
              ∂μ*/∂(parameter), computed by central differences on the ODE
              output.
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted">
              Conversion rate <span className="font-mono">α</span> dominates,
              with the billing-cycle lag <span className="font-mono">μ_R</span>{" "}
              second and growth rate <span className="font-mono">g</span>{" "}
              third. Fixed cost <span className="font-mono">F</span> and ARPU{" "}
              <span className="font-mono">p</span> barely move the threshold
              at all — they shift the magnitude of cash but not the existence
              of recovery.
            </p>

            <div className="mt-12">
              <TornadoChart />
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────
            9. THREE LESSONS
            ────────────────────────────────────────────────────── */}
        <section className="border-b border-rule bg-white">
          <div className="mx-auto max-w-6xl px-6 py-20 sm:px-10 sm:py-24">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted">
              Three things this taught me
            </p>
            <ol className="mt-12 grid gap-12 sm:grid-cols-3 sm:gap-10">
              {[
                {
                  n: "01",
                  title: "A wrong model produces precise nonsense.",
                  body:
                    "I caught a structural defect in the revenue equation in week two and fixed it before any calibration ran on top. The original would have produced a precise answer to the wrong question.",
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
          </div>
        </section>
      </main>

      {/* ───────────────────────────────────────────────────────────
          FOOTER
          ──────────────────────────────────────────────────────── */}
      <footer className="bg-cream">
        <div className="mx-auto max-w-6xl px-6 py-12 sm:px-10">
          <div className="flex flex-col gap-8 sm:flex-row sm:items-end sm:justify-between sm:gap-12">
            <div className="flex flex-col gap-1">
              <p className="text-sm font-semibold text-ink">Arsenii Chan</p>
              <p className="text-xs text-muted">CSC 30100 · Spring 2026</p>
              <p className="text-xs text-muted">City College of New York</p>
            </div>
            <div className="flex flex-col items-start gap-2 text-xs sm:items-end">
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="text-muted transition hover:text-ink"
              >
                github.com/ArseniiChan/startup-growth-simulator{" "}
                <ArrowOut className="ml-0.5" />
              </a>
              <a
                href={STREAMLIT_URL}
                target="_blank"
                rel="noreferrer"
                className="text-muted transition hover:text-ink"
              >
                Raw Python notebook (Streamlit){" "}
                <ArrowOut className="ml-0.5" />
              </a>
            </div>
          </div>

          <p className="mt-10 max-w-3xl text-[11px] leading-relaxed text-muted">
            μ* is the runway-survival threshold at T=120 months — the smallest
            monthly user-churn rate at which the default-SaaS profile ends the
            horizon cash-negative. Reported CI conditions on the conversion
            rate α at its calibrated MAP (α has the dominant sensitivity, so
            the marginal CI under joint uncertainty is wider). Datasets on
            this page are precomputed offline by the from-scratch Python
            engine and served as static JSON; the page does not run Python at
            runtime.
          </p>
        </div>
      </footer>
    </div>
  );
}
