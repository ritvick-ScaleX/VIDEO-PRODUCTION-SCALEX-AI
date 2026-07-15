"use client";

import { Check, ChevronsUpDown, Plus } from "lucide-react";
import Link from "next/link";
import { BrandAvatar } from "@/components/shared/brand-avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useActiveBrand } from "@/lib/hooks";
import { cn } from "@/lib/utils";

export function BrandSelector() {
  const { active, brands, setActiveId } = useActiveBrand();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex max-w-[220px] items-center gap-2.5 rounded-xl glass px-3 py-2 text-sm transition-colors hover:bg-card/80">
          {active ? (
            <BrandAvatar name={active.name} logoUrl={active.logo_url} className="h-6 w-6" />
          ) : (
            <span className="grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-aurora-line text-[10px] font-bold text-white">
              —
            </span>
          )}
          <span className="truncate font-medium">{active ? active.name : "No brand"}</span>
          <ChevronsUpDown className="ml-auto h-3.5 w-3.5 shrink-0 opacity-50" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[260px]">
        <DropdownMenuLabel>Active brand</DropdownMenuLabel>
        <div className="max-h-64 overflow-y-auto">
          {brands.length === 0 && (
            <p className="px-3 py-2 text-xs text-muted-foreground">No brands yet.</p>
          )}
          {brands.map((b) => (
            <DropdownMenuItem key={b.id} onClick={() => setActiveId(b.id)}>
              <BrandAvatar name={b.name} logoUrl={b.logo_url} className="h-5 w-5" />
              <span className="truncate">{b.name}</span>
              {active?.id === b.id && <Check className="ml-auto h-4 w-4 text-primary" />}
            </DropdownMenuItem>
          ))}
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/brands" className={cn("text-primary")}>
            <Plus className="h-4 w-4" />
            New brand
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
