"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandWordmark } from "@/components/layout/brand-mark";
import { NAV_GROUPS, NAV_ITEMS } from "@/components/layout/nav";
import { useSystemInfo } from "@/lib/hooks";
import { cn } from "@/lib/utils";

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <nav className="flex flex-col gap-6">
      {NAV_GROUPS.map((group) => (
        <div key={group}>
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/60">
            {group}
          </p>
          <ul className="space-y-1">
            {NAV_ITEMS.filter((i) => i.group === group).map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(item.href + "/");
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onNavigate}
                    className={cn(
                      "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                      active
                        ? "text-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {active && (
                      <motion.span
                        layoutId="nav-active"
                        className="absolute inset-0 -z-10 rounded-xl bg-primary/15 ring-1 ring-primary/20"
                        transition={{ type: "spring", stiffness: 400, damping: 32 }}
                      />
                    )}
                    <Icon
                      className={cn(
                        "h-[18px] w-[18px] transition-colors",
                        active ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                      )}
                    />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function AiModeFooter() {
  const { data } = useSystemInfo();
  const live = data?.ai_mode === "live";
  return (
    <div className="glass rounded-2xl p-3.5">
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "h-2 w-2 rounded-full",
            live ? "bg-success shadow-[0_0_8px_hsl(var(--success))]" : "bg-accent shadow-glow-cyan"
          )}
        />
        <span className="text-xs font-medium">
          {live ? "Live AI" : "Mock mode"}
        </span>
      </div>
      <p className="mt-1 text-[11px] leading-snug text-muted-foreground">
        {live
          ? "Generating on-brand creative"
          : "Add an API key for live generations"}
      </p>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[264px] flex-col border-r border-border/60 bg-card/40 backdrop-blur-xl lg:flex">
      <div className="flex h-16 items-center px-6">
        <Link href="/dashboard">
          <BrandWordmark />
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <NavLinks />
      </div>
      <div className="p-4">
        <AiModeFooter />
      </div>
    </aside>
  );
}

export { NavLinks, AiModeFooter };
