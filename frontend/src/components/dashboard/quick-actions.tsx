"use client";

import {
  BarChart3,
  Boxes,
  Download,
  Package,
  Plus,
  Settings,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Action {
  label: string;
  href: string;
  icon: LucideIcon;
  color: string;
}

const ACTIONS: Action[] = [
  { label: "New Product", href: "/products", icon: Plus, color: "#6D5EF8" },
  { label: "Brands", href: "/brands", icon: Boxes, color: "#4F46E5" },
  { label: "Products", href: "/products", icon: Package, color: "#22D3EE" },
  { label: "Analytics", href: "/analytics", icon: BarChart3, color: "#C026D3" },
  { label: "Exports", href: "/exports", icon: Download, color: "#34D399" },
  { label: "Settings", href: "/settings", icon: Settings, color: "#6D5EF8" },
];

export function QuickActions() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Quick actions</CardTitle>
        <CardDescription>Jump straight into a workflow</CardDescription>
      </CardHeader>
      <CardContent>
        <StaggerGroup className="grid grid-cols-2 gap-3">
          {ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <FadeItem key={action.label}>
                <Link
                  href={action.href}
                  className="group relative flex h-full flex-col gap-3 overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.12] hover:bg-white/[0.04] hover:shadow-glow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                >
                  <div
                    aria-hidden
                    className="pointer-events-none absolute -right-6 -top-8 h-20 w-20 rounded-full opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-30"
                    style={{ backgroundColor: action.color }}
                  />
                  <span
                    className="grid h-10 w-10 place-items-center rounded-xl text-white shadow-glow transition-transform duration-300 group-hover:scale-105"
                    style={{
                      background: `linear-gradient(135deg, ${action.color}, ${action.color}b3)`,
                    }}
                  >
                    <Icon className="h-5 w-5" />
                  </span>
                  <span className="text-sm font-medium leading-tight text-foreground">
                    {action.label}
                  </span>
                </Link>
              </FadeItem>
            );
          })}
        </StaggerGroup>
      </CardContent>
    </Card>
  );
}

export default QuickActions;
