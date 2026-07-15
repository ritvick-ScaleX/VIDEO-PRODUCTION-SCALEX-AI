import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind class names with conflict resolution. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Relative time like "3h ago". */
export function timeAgo(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const secs = Math.floor((Date.now() - d.getTime()) / 1000);
  const table: [number, string][] = [
    [60, "s"],
    [3600, "m"],
    [86400, "h"],
    [604800, "d"],
    [2592000, "w"],
  ];
  if (secs < 60) return "just now";
  let unit = "s";
  let value = secs;
  for (let i = 0; i < table.length; i++) {
    const [limit, label] = table[i];
    if (secs < limit) {
      const prev = i === 0 ? 1 : table[i - 1][0];
      value = Math.floor(secs / prev);
      unit = label;
      break;
    }
    unit = label;
    value = Math.floor(secs / limit);
  }
  return `${value}${unit} ago`;
}

/** Compact number formatting (1.2k, 3.4M). */
export function formatNumber(n: number): string {
  if (n < 1000) return `${n}`;
  if (n < 1_000_000) return `${(n / 1000).toFixed(1).replace(/\.0$/, "")}k`;
  return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
}

export function titleCase(s: string): string {
  return s.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** User-facing label for a product status (internal names stay technical). */
export function statusLabel(s: string): string {
  return titleCase(s === "scraping" ? "importing" : s);
}

export function initials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}
