"use client";

import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { FadeInView } from "@/components/animations/motion";

const FAQS = [
  {
    q: "What does ScaleX AI actually do?",
    a: "ScaleX AI is an AI creative studio. Add a brand, paste product URLs, and it imports everything, generates studio images and campaign ideas, writes Hinglish scripts with storyboard frames, and renders realistic multi-shot video ads featuring your exact product.",
  },
  {
    q: "Will the video show my real product?",
    a: "Yes. Your imported product photos anchor every generation — you even choose which photos the AI is allowed to use. The rendered video features a real presenter showing your exact product with its label and design intact, not a look-alike.",
  },
  {
    q: "Do I need an API key to try it?",
    a: "No. ScaleX AI runs out of the box with realistic sample content so you can explore the whole studio without any setup. Add your API key to switch on live AI generations.",
  },
  {
    q: "What language do the video ads speak?",
    a: "v1.0 is tuned for the Indian market: an Indian presenter speaking natural Hinglish (Hindi-English), lip-synced, across multiple camera angles stitched into one ad. More languages and presenters are planned.",
  },
  {
    q: "Where is my data stored?",
    a: "Everything runs locally. Your brands, products and generated assets live in a local database on your machine — nothing is sent anywhere except the AI calls you explicitly trigger.",
  },
  {
    q: "What's on the roadmap?",
    a: "The studio is the focus today. Authentication, billing and team collaboration are planned for a later release — for now ScaleX AI is built to run locally, free, and without a signup.",
  },
];

export function Faq() {
  return (
    <section id="faq" className="relative scroll-mt-24 py-24 sm:py-32">
      <div className="mx-auto max-w-3xl px-4 sm:px-6">
        <FadeInView className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary" className="mb-4 border-white/[0.08]">
            FAQ
          </Badge>
          <h2 className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
            Questions,{" "}
            <span className="text-gradient bg-aurora-line">answered</span>.
          </h2>
        </FadeInView>

        <FadeInView delay={0.1} className="mt-12">
          <Accordion type="single" collapsible className="space-y-3">
            {FAQS.map((item, i) => (
              <AccordionItem key={i} value={`item-${i}`} className="border-none">
                <AccordionTrigger>{item.q}</AccordionTrigger>
                <AccordionContent>{item.a}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </FadeInView>
      </div>
    </section>
  );
}
