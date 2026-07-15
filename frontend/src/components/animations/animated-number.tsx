"use client";

import { animate, useInView } from "framer-motion";
import * as React from "react";
import { formatNumber } from "@/lib/utils";

export function AnimatedNumber({
  value,
  format = false,
  decimals = 0,
  className,
  duration = 1.1,
}: {
  value: number;
  format?: boolean;
  decimals?: number;
  className?: string;
  duration?: number;
}) {
  const ref = React.useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  React.useEffect(() => {
    if (!inView || !ref.current) return;
    const node = ref.current;
    const controls = animate(0, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate(latest) {
        node.textContent = format
          ? formatNumber(Math.round(latest))
          : latest.toFixed(decimals);
      },
    });
    return () => controls.stop();
  }, [inView, value, format, decimals, duration]);

  return (
    <span ref={ref} className={className}>
      {format ? formatNumber(0) : (0).toFixed(decimals)}
    </span>
  );
}
