"use client";

import { Quote, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  FadeInView,
  FadeItem,
  StaggerGroup,
} from "@/components/animations/motion";
import { initials } from "@/lib/utils";

type Testimonial = {
  name: string;
  role: string;
  quote: string;
};

const TESTIMONIALS: Testimonial[] = [
  {
    name: "Placeholder Founder",
    role: "Founder, Sample DTC Brand",
    quote:
      "ScaleX AI turned a single product page into a week of on-brand content. This is placeholder copy standing in for a real review.",
  },
  {
    name: "Sample Marketer",
    role: "Growth Lead, Example Co.",
    quote:
      "The brand memory means every asset sounds like us. Generic placeholder testimonial shown for layout purposes.",
  },
  {
    name: "Demo Creator",
    role: "Creator, Placeholder Studio",
    quote:
      "UGC scripts in seconds, and the creative scores actually help. This quote is a stand-in placeholder, not a real endorsement.",
  },
];

export function Testimonials() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <FadeInView className="mx-auto max-w-2xl text-center">
          <Badge variant="accent" className="mb-4">
            Loved by creators
          </Badge>
          <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
            Built for teams that ship{" "}
            <span className="text-gradient bg-aurora-line">fast</span>.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-sm text-muted-foreground">
            Placeholder testimonials — replace with real customer quotes before launch.
          </p>
        </FadeInView>

        <StaggerGroup className="mt-14 grid grid-cols-1 gap-4 md:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <FadeItem key={t.name}>
              <figure className="glass hover-lift flex h-full flex-col rounded-3xl p-6">
                <Quote className="h-7 w-7 text-primary/70" />
                <div className="mt-3 flex gap-0.5" aria-label="5 out of 5 stars">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className="h-4 w-4 fill-aurora-violet text-aurora-violet"
                    />
                  ))}
                </div>
                <blockquote className="mt-4 flex-1 text-sm leading-relaxed text-foreground/90">
                  &ldquo;{t.quote}&rdquo;
                </blockquote>
                <figcaption className="mt-6 flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback>{initials(t.name)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-semibold">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.role}</p>
                  </div>
                </figcaption>
              </figure>
            </FadeItem>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
