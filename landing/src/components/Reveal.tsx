"use client";

/**
 * Reveal — wraps children in a subtle scroll-triggered fade-up.
 *
 * The motion is intentionally restrained: 16px upward translation, 600ms
 * ease-out, fires once when the element scrolls into view. This is the
 * Apple/Linear/Stripe "I noticed details" polish move — visitors don't
 * consciously register it, but the page feels designed instead of slapped
 * together.
 *
 * Respects prefers-reduced-motion via framer-motion's built-in handling.
 */

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface RevealProps {
  children: ReactNode;
  /** Delay in seconds before the animation starts, useful for staggers. */
  delay?: number;
  /** Override className on the wrapping element. */
  className?: string;
}

export function Reveal({ children, delay = 0, className }: RevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
