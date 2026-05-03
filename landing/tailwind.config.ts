import type { Config } from "tailwindcss";

// Editorial Navy palette, locked in Phase 4.
// Background pure white, ink slate-900, accent reserved for the hero number.
// The slate-600 is the duotone token used for captions, axis labels,
// secondary text, and the "survives" half of the survives/dies story.
// The accent red is reserved for: the 14.2% glyph, the failure-mode
// callout in the body, and one CTA button. Nothing else gets red.

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0F172A",        // slate-900 — primary text
        muted: "#475569",      // slate-600 — duotone secondary (captions, "survives")
        rule: "#E2E8F0",       // slate-200 — subtle dividers
        cream: "#F8FAFC",      // slate-50  — section-alternation background (used sparingly)
        accent: "#DC2626",     // red-600   — reserved for the 14.2% glyph + CTA + one callout
      },
      fontFamily: {
        // System sans-serif default; we'll layer Inter via @next/font in layout.tsx.
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        // JetBrains Mono on the hero number — the load-bearing glyph.
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.04em",   // editorial display tracking
      },
    },
  },
  plugins: [],
};

export default config;
