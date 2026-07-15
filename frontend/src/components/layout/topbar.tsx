"use client";

import { Boxes, LogOut, Menu, Plus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { BrandWordmark } from "@/components/layout/brand-mark";
import { AiModeFooter, NavLinks } from "@/components/layout/sidebar";
import { BrandSelector } from "@/components/layout/brand-selector";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { currentUser, logout } from "@/lib/auth";

export function Topbar() {
  const [open, setOpen] = React.useState(false);
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border/60 bg-background/70 px-4 backdrop-blur-xl lg:px-8">
      {/* Mobile menu */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button variant="glass" size="icon" className="lg:hidden" aria-label="Menu">
            <Menu className="h-5 w-5" />
          </Button>
        </DialogTrigger>
        <DialogContent className="left-0 top-0 h-full w-[280px] max-w-[85vw] translate-x-0 translate-y-0 rounded-none rounded-r-3xl data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left">
          <DialogTitle className="sr-only">Navigation</DialogTitle>
          <div className="mb-4">
            <BrandWordmark />
          </div>
          <div className="flex-1 overflow-y-auto">
            <NavLinks onNavigate={() => setOpen(false)} />
          </div>
          <div className="pt-4">
            <AiModeFooter />
          </div>
        </DialogContent>
      </Dialog>

      <BrandSelector />

      <div className="ml-auto flex items-center gap-2">
        <Button asChild variant="aurora" size="sm" className="hidden sm:inline-flex">
          <Link href="/products">
            <Plus className="h-4 w-4" />
            New Product
          </Link>
        </Button>
        <Button asChild variant="ghost" size="sm" className="hidden md:inline-flex">
          <Link href="/brands">
            <Boxes className="h-4 w-4" />
            Brands
          </Link>
        </Button>
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}

function UserMenu() {
  const router = useRouter();
  const [user, setUser] = React.useState<string | null>(null);
  React.useEffect(() => setUser(currentUser()), []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button aria-label="Account" className="rounded-full focus-ring">
          <Avatar className="h-9 w-9 ring-1 ring-border">
            <AvatarFallback className="bg-aurora-line text-xs font-bold text-white">
              {(user?.[0] ?? "S").toUpperCase()}
            </AvatarFallback>
          </Avatar>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[230px]">
        <DropdownMenuLabel className="truncate font-normal text-muted-foreground">
          {user ?? "Signed in"}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={() => {
            logout();
            router.replace("/login");
          }}
          className="text-destructive focus:text-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
