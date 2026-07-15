"use client";

import type { LucideIcon } from "lucide-react";
import { FadeUp } from "@/components/animations/motion";
import { Badge } from "@/components/ui/badge";

export function PageHeader({
  title,
  description,
  icon: Icon,
  eyebrow,
  actions,
}: {
  title: string;
  description?: string;
  icon?: LucideIcon;
  eyebrow?: string;
  actions?: React.ReactNode;
}) {
  return (
    <FadeUp className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="flex items-start gap-4">
        {Icon && (
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-aurora-line bg-[length:200%_200%] animate-gradient-pan text-white shadow-glow">
            <Icon className="h-6 w-6" />
          </div>
        )}
        <div>
          {eyebrow && (
            <Badge variant="secondary" className="mb-2">
              {eyebrow}
            </Badge>
          )}
          <h1 className="font-display text-2xl font-bold tracking-tight sm:text-3xl">
            {title}
          </h1>
          {description && (
            <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground sm:text-base">
              {description}
            </p>
          )}
        </div>
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </FadeUp>
  );
}
