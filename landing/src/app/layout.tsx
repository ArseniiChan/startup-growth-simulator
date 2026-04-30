import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

const SITE_URL = "https://startup-growth.vercel.app";
const TITLE = "The exact monthly user-churn rate above which no amount of growth saves the business: 14.2%";
const DESCRIPTION =
  "A from-scratch numerical-analysis study of when a SaaS startup runs out of recovery — μ* with a Monte Carlo confidence interval, and a structural-identifiability finding behind it. CSC 30100, Spring 2026.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  authors: [{ name: "Arsenii Chan" }],
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
    siteName: "Startup Growth — Numerical Analysis",
    images: [
      {
        url: "/figures/valley.png",
        width: 1200,
        height: 800,
        alt: "Curved-valley contour plot in (g, μ_R) parameter space — the structural-identifiability finding.",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    images: ["/figures/valley.png"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        {/* Force light mode regardless of OS preference. */}
        <meta name="color-scheme" content="light" />
      </head>
      <body className="bg-white font-sans text-ink antialiased">{children}</body>
    </html>
  );
}
