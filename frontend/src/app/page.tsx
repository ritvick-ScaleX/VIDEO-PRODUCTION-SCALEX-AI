import type { Metadata } from "next";
import { Navbar } from "@/components/landing/navbar";
import { Hero } from "@/components/landing/hero";
import { Features } from "@/components/landing/features";
import { HowItWorks } from "@/components/landing/how-it-works";
import { Testimonials } from "@/components/landing/testimonials";
import { Faq } from "@/components/landing/faq";
import { Cta } from "@/components/landing/cta";
import { Footer } from "@/components/landing/footer";

export const metadata: Metadata = {
  title: "ScaleX AI — Paste a product URL, get a real video ad",
  description:
    "ScaleX AI v1.0 imports your brand and products, generates studio images and campaign ideas, writes the script, and renders a realistic multi-shot video ad — a real presenter showing your exact product, speaking Hinglish. No signup, runs locally.",
  openGraph: {
    title: "ScaleX AI — AI Creative Studio v1.0",
    description:
      "From product URL to realistic AI video ad — brand import, studio images, ideas, Hinglish scripts, and multi-shot video in one studio.",
    type: "website",
  },
};

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Testimonials />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </div>
  );
}
