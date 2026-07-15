"use client";

import Link from "next/link";
import { ArrowRight, PlayCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FadeUp } from "@/components/animations/motion";
import { DashboardPreview } from "@/components/landing/dashboard-preview";

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-36 pb-20 sm:pt-44 sm:pb-28">
      {/* Background layers */}
      <div className="aurora-bg" />
      <div className="pointer-events-none absolute inset-0 -z-10 grid-bg opacity-60" />

      {/* Floating blurred orbs */}
      <div className="pointer-events-none absolute -left-24 top-24 -z-10 h-72 w-72 rounded-full bg-aurora-violet/25 blur-3xl animate-float" />
      <div
        className="pointer-events-none absolute -right-16 top-40 -z-10 h-80 w-80 rounded-full bg-aurora-cyan/20 blur-3xl animate-float"
        style={{ animationDelay: "-2.5s" }}
      />
      <div
        className="pointer-events-none absolute bottom-0 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-aurora-fuchsia/20 blur-3xl animate-float"
        style={{ animationDelay: "-4s" }}
      />

      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="mx-auto max-w-3xl text-center">
          <FadeUp delay={0.05}>
            <Badge
              variant="secondary"
              className="mb-6 gap-1.5 border-white/[0.08] px-3 py-1 text-xs"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              AI Creative Studio · v1.0
            </Badge>
          </FadeUp>

          <FadeUp delay={0.12}>
            <h1 className="font-display text-5xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
              Paste a product URL. Get a{" "}
              <span className="text-gradient bg-aurora-line animate-gradient-pan">
                real video ad
              </span>
              .
            </h1>
          </FadeUp>

          <FadeUp delay={0.2}>
            <p className="mx-auto mt-6 max-w-2xl text-balance text-lg leading-relaxed text-muted-foreground sm:text-xl">
              ScaleX AI imports your brand and products, generates studio images
              and campaign ideas, writes the script — then renders a realistic
              multi-shot video ad where a real presenter shows your exact product,
              speaking in Hinglish.
            </p>
          </FadeUp>

          <FadeUp delay={0.28}>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button
                asChild
                variant="aurora"
                size="lg"
                className="group w-full sm:w-auto"
              >
                <Link href="/dashboard">
                  Open the Studio
                  <ArrowRight className="transition-transform duration-200 group-hover:translate-x-0.5" />
                </Link>
              </Button>
              <Button
                asChild
                variant="glass"
                size="lg"
                className="w-full sm:w-auto"
              >
                <a href="#how">
                  <PlayCircle className="text-accent" />
                  See how it works
                </a>
              </Button>
            </div>
          </FadeUp>

          <FadeUp delay={0.36}>
            <p className="mt-6 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
              <span>No signup</span>
              <span className="text-border">·</span>
              <span>Runs locally</span>
              <span className="text-border">·</span>
              <span>AI-powered</span>
            </p>
          </FadeUp>
        </div>

        <div className="mt-16 sm:mt-20">
          <DashboardPreview />
        </div>
      </div>
    </section>
  );
}
