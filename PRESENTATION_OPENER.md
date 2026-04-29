# 90-Second Cold-Open

*Written before any further code work, per the chairman's directive. Read
this verbatim or close to it; it frames everything else.*

---

**Slide 1 — Title (10s):**

> "Hi, I'm Arsenii. For my CSC 30100 final I built a startup-survival
> threshold calculator from scratch — and I want to walk you through what
> it found."

**Slide 2 — The question, in plain English (40s):**

> "Every venture capitalist looks at a startup and tries to answer one
> question: will this company survive? You can answer that with intuition,
> or you can answer it with math. I built the math.
>
> Here's the result. Take a typical software-as-a-service startup —
> reasonable growth, reasonable conversion, reasonable costs. There is a
> *single number* — the rate at which paying users cancel each month —
> above which the company runs out of money before it can ever recover,
> within a 10-year horizon. For our default profile that number is
> **about 14%**. Below 14% monthly churn, the company survives. Above 14%,
> it doesn't. I want to show you how I found it, and how confident I am
> in the answer."

**Slide 3 — The non-identifiability finding (40s):**

> "But there's a second result I'm prouder of. When I tried to fit my
> model to noisy revenue data, I found that two of the model's
> parameters — the growth rate and the billing-cycle lag — can't be
> separately identified from the data. The fit produces a curved valley,
> not a single best-fit point. So I asked: does that ambiguity matter
> for the answer? I computed the smallest-eigenvalue eigenvector of the
> calibration loss Hessian — that's the direction the data is *least*
> informative about — and recomputed the survival threshold along it.
> **The threshold varies by about 2.4% along the worst direction.**
> Even though the calibration is ambiguous, the answer it produces is
> meaningfully robust to that ambiguity. That's a
> structural-identifiability finding, and it's why I'm confident in
> 14%."

---

## Sentences I want to land cleanly:

1. *"Above this monthly user-cancellation rate, no amount of growth saves
   the business within ten years."* — the simple definition of μ\*.
2. *"We found a parameter direction the data can't distinguish — and
   proved our answer is robust to it."* — the identifiability story.
3. *"Every numerical method here was implemented from scratch — Burden et
   al. chapter by chapter. No SciPy."* — the course-content claim.

## Backup if the live demo fails:

A static screenshot of the dashboard goes on slide 7. Narrate the same
demo over the screenshot. The numbers (μ\*, 95% CI, P(unicorn)) are
already on slide 6.

## Time targets:

- Cold-open (slides 1-3): 90s combined
- Solver convergence (slide 4): 45s
- Calibration valley (slide 5): 60s
- μ\* with CI (slide 6): 60s
- Live demo (slide 7): 90-100s
- Lessons + QR (slides 8-9): 45s
- **Total target: 6:30 with 30s margin**
