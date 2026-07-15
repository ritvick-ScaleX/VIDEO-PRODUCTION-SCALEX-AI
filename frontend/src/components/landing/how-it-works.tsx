"use client";

import { Boxes, Film, Lightbulb, Link2, type LucideIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  FadeInView,
  FadeItem,
  StaggerGroup,
} from "@/components/animations/motion";

type Step = {
  n: number;
  icon: LucideIcon;
  title: string;
  description: string;
};

const STEPS: Step[] = [
  {
    n: 1,
    icon: Boxes,
    title: "Add your brand",
    description:
      "Paste your website — ScaleX AI grabs the logo, colours and tagline, and infers your brand voice.",
  },
  {
    n: 2,
    icon: Link2,
    title: "List your products",
    description:
      "Paste each product URL. Photos, price and details are captured — you choose which photos the AI can use.",
  },
  {
    n: 3,
    icon: Lightbulb,
    title: "Pick an idea",
    description:
      "Describe the campaign you want. Choose one of the AI's directions and it writes the Hinglish script and frames.",
  },
  {
    n: 4,
    icon: Film,
    title: "Render & export",
    description:
      "A realistic multi-shot video ad with your exact product — plus packshots, creatives and copy, ready to export.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="relative scroll-mt-24 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <FadeInView className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary" className="mb-4 border-white/[0.08]">
            How it works
          </Badge>
          <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
            From URL to video ad in{" "}
            <span className="text-gradient bg-aurora-line">four steps</span>.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
            No briefs, no boilerplate. Give ScaleX AI a link and it does the rest.
          </p>
        </FadeInView>

        <div className="relative mt-16">
          {/* Connective line on desktop */}
          <div
            aria-hidden
            className="pointer-events-none absolute left-0 right-0 top-8 hidden h-px bg-gradient-to-r from-transparent via-border to-transparent md:block"
          />

          <StaggerGroup className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
            {STEPS.map((step) => {
              const Icon = step.icon;
              return (
                <FadeItem key={step.n}>
                  <div className="relative flex flex-col items-center text-center md:items-start md:text-left">
                    <div className="relative z-10 flex items-center gap-3">
                      <span className="grid h-16 w-16 place-items-center rounded-2xl bg-aurora-line bg-[length:200%_200%] font-display text-2xl font-bold text-white shadow-glow">
                        {step.n}
                      </span>
                    </div>
                    <div className="mt-5">
                      <div className="mb-2 inline-flex items-center gap-2 text-primary">
                        <Icon className="h-4 w-4" />
                        <span className="text-xs font-semibold uppercase tracking-wide">
                          Step {step.n}
                        </span>
                      </div>
                      <h3 className="font-display text-xl font-semibold tracking-tight">
                        {step.title}
                      </h3>
                      <p className="mt-2 max-w-xs text-sm leading-relaxed text-muted-foreground md:max-w-none">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </FadeItem>
              );
            })}
          </StaggerGroup>
        </div>
      </div>
    </section>
  );
}
