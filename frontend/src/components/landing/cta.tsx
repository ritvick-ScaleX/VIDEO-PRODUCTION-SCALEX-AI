"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FadeInView } from "@/components/animations/motion";

export function Cta() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <FadeInView>
          <div className="glass-strong relative overflow-hidden rounded-[2.5rem] px-6 py-16 text-center shadow-glow sm:px-16 sm:py-20">
            {/* Aurora glow */}
            <div className="pointer-events-none absolute inset-0 -z-10 bg-aurora-radial opacity-80" />
            <div className="pointer-events-none absolute -top-24 left-1/2 -z-10 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-aurora-violet/30 blur-3xl" />
            <div
              className="pointer-events-none absolute bottom-0 right-0 -z-10 h-56 w-56 rounded-full bg-aurora-cyan/20 blur-3xl animate-float"
              style={{ animationDelay: "-3s" }}
            />

            <span className="inline-grid h-14 w-14 place-items-center rounded-2xl bg-aurora-line bg-[length:200%_200%] text-white shadow-glow animate-gradient-pan">
              <Sparkles className="h-7 w-7" />
            </span>

            <h2 className="mx-auto mt-6 max-w-2xl font-display text-4xl font-bold tracking-tight sm:text-5xl">
              Your next video ad is one{" "}
              <span className="text-gradient bg-aurora-line">URL</span> away.
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
              Open the studio, paste a product link, and watch it become a
              realistic on-brand video ad. No signup, no setup.
            </p>

            <div className="mt-9 flex justify-center">
              <Button asChild variant="aurora" size="lg" className="group">
                <Link href="/dashboard">
                  Open the Studio
                  <ArrowRight className="transition-transform duration-200 group-hover:translate-x-0.5" />
                </Link>
              </Button>
            </div>
          </div>
        </FadeInView>
      </div>
    </section>
  );
}
