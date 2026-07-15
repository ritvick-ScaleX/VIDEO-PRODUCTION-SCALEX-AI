"use client";

import * as React from "react";
import { cn, initials } from "@/lib/utils";

/** Brand profile icon: the brand's logo when available, else its initials. */
export function BrandAvatar({
  name,
  logoUrl,
  className,
  textClass = "text-[10px]",
}: {
  name: string;
  logoUrl?: string | null;
  className?: string;
  textClass?: string;
}) {
  const [broken, setBroken] = React.useState(false);
  const showLogo = !!logoUrl && !broken;

  return (
    <span
      className={cn(
        "relative grid shrink-0 place-items-center overflow-hidden rounded-lg font-bold text-white",
        showLogo ? "bg-white" : "bg-aurora-line",
        className
      )}
    >
      {showLogo ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={logoUrl!}
          alt={name}
          className="h-full w-full object-contain p-0.5"
          onError={() => setBroken(true)}
        />
      ) : (
        <span className={textClass}>{initials(name)}</span>
      )}
    </span>
  );
}
