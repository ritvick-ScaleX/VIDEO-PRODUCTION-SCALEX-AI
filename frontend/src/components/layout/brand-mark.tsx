import { cn } from "@/lib/utils";

/** The ScaleX glyph — the brand's gradient favicon mark. */
export function BrandMark({ className }: { className?: string }) {
  return (
    <span className={cn("relative grid place-items-center overflow-hidden rounded-xl", className)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/scalex-favicon.svg" alt="ScaleX AI" className="h-full w-full object-contain" />
    </span>
  );
}

export function BrandWordmark({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <BrandMark className="h-8 w-8" />
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/scalex-logo.svg" alt="ScaleX" className="h-[18px] w-auto" />
      <span className="font-display text-lg font-bold leading-none tracking-tight text-gradient bg-aurora-line">
        AI
      </span>
    </div>
  );
}
