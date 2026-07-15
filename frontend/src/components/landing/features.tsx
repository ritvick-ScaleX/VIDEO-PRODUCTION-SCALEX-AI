"use client";

import {
  BarChart3,
  Boxes,
  Clapperboard,
  FileText,
  Image as ImageIcon,
  Lightbulb,
  Search,
  Video,
  type LucideIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  FadeInView,
  FadeItem,
  StaggerGroup,
} from "@/components/animations/motion";

type Feature = {
  icon: LucideIcon;
  title: string;
  description: string;
};

const FEATURES: Feature[] = [
  {
    icon: Boxes,
    title: "Brands from a URL",
    description:
      "Paste your website and ScaleX AI pulls in the logo, colours, tagline — and infers your brand voice.",
  },
  {
    icon: Search,
    title: "Product Import",
    description:
      "Drop in a product URL to capture photos, price, features and details — then pick which photos the AI may use.",
  },
  {
    icon: ImageIcon,
    title: "Studio Images",
    description:
      "White-background packshots and lifestyle creatives built from your real product photos — never a look-alike.",
  },
  {
    icon: Lightbulb,
    title: "Idea Engine",
    description:
      "Describe your campaign in a line; get distinct directions with hooks. Pick one — every idea stays saved.",
  },
  {
    icon: Clapperboard,
    title: "Script Studio",
    description:
      "Hook-first Hinglish scripts with a shootable storyboard. Edit, reprompt, and preview every frame before render.",
  },
  {
    icon: Video,
    title: "Realistic AI Video",
    description:
      "A real presenter shows your exact product across multiple shots, lip-synced in Hinglish — stitched into one ad.",
  },
  {
    icon: FileText,
    title: "Ad Copy",
    description:
      "On-brand headlines, captions and CTAs for every platform, tuned to your tone.",
  },
  {
    icon: BarChart3,
    title: "Analytics & Export",
    description:
      "Track output across brands and products, then export images, videos and PDF briefs in one click.",
  },
];

export function Features() {
  return (
    <section id="features" className="relative scroll-mt-24 py-24 sm:py-32">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-aurora-radial opacity-30" />
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <FadeInView className="mx-auto max-w-2xl text-center">
          <Badge variant="accent" className="mb-4">
            Everything in one studio
          </Badge>
          <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
            One product URL in.{" "}
            <span className="text-gradient bg-aurora-line">A full campaign out.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
            A complete creative pipeline — brand import, studio images, ideas,
            scripts and realistic video — all aware of your brand.
          </p>
        </FadeInView>

        <StaggerGroup className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <FadeItem key={feature.title}>
                <div className="glass hover-lift group h-full rounded-3xl p-6">
                  <span className="mb-5 inline-grid h-12 w-12 place-items-center rounded-2xl bg-aurora-line bg-[length:200%_200%] text-white shadow-glow transition-transform duration-300 group-hover:scale-105 group-hover:animate-gradient-pan">
                    <Icon className="h-6 w-6" />
                  </span>
                  <h3 className="font-display text-lg font-semibold tracking-tight">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              </FadeItem>
            );
          })}
        </StaggerGroup>
      </div>
    </section>
  );
}
